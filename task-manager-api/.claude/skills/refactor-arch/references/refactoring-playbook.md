# Refactoring Playbook (Phase 3)

Concrete transformations, each mapped to catalog entries. Examples are given in Python (Flask) and
JavaScript (Express); apply the same idea in the detected stack. Apply in this order:
**PB-01 config → PB-03 structure → security (PB-02, 04, 05, 06, 10) → PB-07/08 layering →
PB-09…16 → LOW fixes (PB-17…19)**.

| PB | Fixes | Transformation |
|---|---|---|
| PB-01 | AP-01, AP-10 | Externalize config & secrets; secure runtime flags |
| PB-02 | AP-02 | Parameterized queries |
| PB-03 | AP-03 | Split God module into Model / Controller / View |
| PB-04 | AP-04 | Slow salted password hashing |
| PB-05 | AP-05 | Guard or remove dangerous endpoints |
| PB-06 | AP-06 | Serializer allow-lists & safe logging |
| PB-07 | AP-07 | Thin route → controller use case |
| PB-08 | AP-08, AP-09 | App factory + dependency injection instead of globals |
| PB-09 | AP-11 | Transactions & referential integrity |
| PB-10 | AP-12 | Signed tokens |
| PB-11 | AP-13 | Remove N+1 (JOIN / eager load / batch / GROUP BY) |
| PB-12 | AP-14 | Centralized input validation |
| PB-13 | AP-15 | Central error handler + domain errors |
| PB-14 | AP-16 | Extract the duplicated rule once |
| PB-15 | AP-17 | Replace deprecated APIs |
| PB-16 | AP-18 | Callbacks → async/await |
| PB-17 | AP-19 | Named constants |
| PB-18 | AP-20, 21, 23 | Rename, delete dead code, simplify booleans |
| PB-19 | AP-22 | Real logger |

---

## PB-01 — Externalize configuration and secrets

**Before (Python)**
```python
app = Flask(__name__)
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
app.run(host="0.0.0.0", port=5000, debug=True)
```
**After**
```python
# src/config/settings.py
import os

class Settings:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    DEBUG = os.environ.get("FLASK_DEBUG", "0") == "1"
    HOST = os.environ.get("HOST", "127.0.0.1")
    PORT = int(os.environ.get("PORT", "5000"))
    DATABASE_PATH = os.environ.get("DATABASE_PATH", "loja.db")

# app.py (entry point)
from src.app import create_app
app = create_app()
if __name__ == "__main__":
    s = app.config["SETTINGS"]
    app.run(host=s.HOST, port=s.PORT, debug=s.DEBUG)
```
**Before (JS)**
```js
const config = { dbPass: "senha_super_secreta_prod_123", paymentGatewayKey: "pk_live_123", port: 3000 };
```
**After**
```js
// src/config/settings.js
module.exports = Object.freeze({
  port: Number(process.env.PORT || 3000),
  databaseFile: process.env.DATABASE_FILE || ':memory:',
  paymentGatewayKey: process.env.PAYMENT_GATEWAY_KEY || '',   // no live key in source
  smtpUser: process.env.SMTP_USER || '',
});
```
Also add a `.env.example` listing every variable (no real values). Never print secrets on boot.

## PB-02 — Parameterized queries

**Before**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'")
query += " AND (nome LIKE '%" + termo + "%')"
```
**After**
```python
cursor.execute("SELECT * FROM usuarios WHERE email = ?", (email,))
clauses, params = ["1=1"], []
if termo:
    clauses.append("(nome LIKE ? OR descricao LIKE ?)")
    params += [f"%{termo}%", f"%{termo}%"]
cursor.execute(f"SELECT * FROM produtos WHERE {' AND '.join(clauses)}", params)  # only placeholders interpolated
```
**JS**
```js
// Before
db.all(`SELECT * FROM users WHERE email = '${email}'`);
// After
db.all('SELECT * FROM users WHERE email = ?', [email]);
```

## PB-03 — Split a God module into Model / Controller / View

**Before** — `models.py` (CRUD for 4 entities + reports) and `app.py` (routes + admin SQL) all wired
to one global connection; or a JS class with `initDb()` + `setupRoutes(app)` containing every handler.

**After** — one file per entity per layer:
```python
# src/models/produto_model.py  (persistence only)
class ProdutoModel:
    def __init__(self, db):            # db injected
        self.db = db
    def find_by_id(self, produto_id):
        row = self.db.execute("SELECT * FROM produtos WHERE id = ?", (produto_id,)).fetchone()
        return dict(row) if row else None

# src/controllers/produto_controller.py  (use cases)
class ProdutoController:
    def __init__(self, produtos: ProdutoModel):
        self.produtos = produtos
    def obter(self, produto_id):
        produto = self.produtos.find_by_id(produto_id)
        if not produto:
            raise NotFoundError("Produto não encontrado")
        return produto

# src/views/produto_routes.py  (HTTP only)
def create_produto_blueprint(controller):
    bp = Blueprint("produtos", __name__)
    @bp.get("/produtos/<int:produto_id>")
    def buscar_produto(produto_id):
        return jsonify({"dados": controller.obter(produto_id), "sucesso": True}), 200
    return bp
```
```js
// JS: AppManager.setupRoutes → views/checkoutRoutes.js
function checkoutRoutes(controller) {
  const router = express.Router();
  router.post('/api/checkout', asyncHandler(async (req, res) => {
    const result = await controller.checkout(req.body);
    res.status(200).json(result);
  }));
  return router;
}
```
Delete the old god files once every route is served by the new modules.

## PB-04 — Slow, salted password hashing

**Before**
```python
self.password = hashlib.md5(pwd.encode()).hexdigest()
```
```js
function badCrypto(pwd) { let h = ""; for (let i = 0; i < 10000; i++) h += Buffer.from(pwd).toString('base64').substring(0, 2); return h.substring(0, 10); }
```
**After**
```python
from werkzeug.security import generate_password_hash, check_password_hash  # ships with Flask
self.password = generate_password_hash(pwd)
def check_password(self, pwd): return check_password_hash(self.password, pwd)
```
```js
// src/services/passwordHasher.js
const crypto = require('crypto');
function hash(password) {
  const salt = crypto.randomBytes(16).toString('hex');
  const key = crypto.scryptSync(password, salt, 64).toString('hex');
  return `scrypt$${salt}$${key}`;
}
function verify(password, stored) {
  const [, salt, key] = stored.split('$');
  const candidate = crypto.scryptSync(password, salt, 64);
  return crypto.timingSafeEqual(candidate, Buffer.from(key, 'hex'));
}
```
Login must look the user up by e-mail (parameterized), then verify the hash in code — never compare
passwords in SQL. Seed data must be hashed through the same function.

## PB-05 — Guard or remove dangerous endpoints

**Before**
```python
@app.route("/admin/query", methods=["POST"])
def executar_query():
    cursor.execute(request.get_json()["sql"])
```
**After** — preserve the route (contract) but require an admin credential from config and narrow
what it can do:
```python
# src/middlewares/auth.py
def require_admin_token(settings):
    def decorator(fn):
        @wraps(fn)
        def wrapper(*a, **kw):
            token = request.headers.get("X-Admin-Token", "")
            if not settings.ADMIN_TOKEN or not hmac.compare_digest(token, settings.ADMIN_TOKEN):
                raise ForbiddenError("Acesso administrativo negado")
            return fn(*a, **kw)
        return wrapper
    return decorator
```
Arbitrary-SQL endpoints: allow only a single read-only `SELECT` (reject `;` and non-SELECT) or
remove them if the README does not document them — state the decision in the summary.
Express: `router.use('/api/admin', requireAdminToken(settings))`.

## PB-06 — Serializer allow-lists and safe logging

**Before**
```python
def to_dict(self): return {"id": self.id, "email": self.email, "password": self.password}
return jsonify({"status": "ok", "secret_key": "minha-chave-super-secreta-123", "debug": True})
```
```js
console.log(`Processando cartão ${cc} na chave ${config.paymentGatewayKey}`);
```
**After**
```python
PUBLIC_FIELDS = ("id", "name", "email", "role", "active", "created_at")
def to_dict(self): return {f: getattr(self, f) for f in PUBLIC_FIELDS}
return jsonify({"status": "ok", "database": "connected", "counts": counts})   # no secrets
```
```js
logger.info(`Processing card ****${card.slice(-4)}`);  // never log full PAN or keys
```

## PB-07 — Thin route → controller use case

**Before (Flask)**
```python
@app.post("/pedidos")
def criar_pedido():
    dados = request.get_json()
    for item in dados["itens"]:
        produto = cursor.execute(...).fetchone()
        if produto["estoque"] < item["quantidade"]: return jsonify({"erro": "..."}), 400
    ...insert pedido, itens, update estoque...
    print("ENVIANDO EMAIL ...")
```
**After**
```python
# view
@bp.post("/pedidos")
def criar_pedido():
    resultado = controller.criar(request.get_json(silent=True))
    return jsonify({"dados": resultado, "sucesso": True, "mensagem": "Pedido criado com sucesso"}), 201

# controller
def criar(self, dados):
    usuario_id, itens = validate_pedido(dados)        # PB-12
    for item in itens:
        produto = self.produtos.find_by_id(item["produto_id"])
        if produto is None: raise ValidationError(f"Produto {item['produto_id']} não encontrado")
        if produto["estoque"] < item["quantidade"]: raise ValidationError(f"Estoque insuficiente para {produto['nome']}")
    pedido = self.pedidos.create_with_items(usuario_id, itens)   # one transaction (PB-09)
    self.notifier.pedido_criado(pedido)
    return pedido
```

## PB-08 — App factory + dependency injection instead of globals

**Before**
```python
db_connection = None
def get_db():
    global db_connection
    if db_connection is None: db_connection = sqlite3.connect("loja.db", check_same_thread=False)
    return db_connection
```
```js
let globalCache = {}; let totalRevenue = 0;
class AppManager { constructor() { this.db = new sqlite3.Database(':memory:'); } }
```
**After**
```python
# src/app.py — composition root
def create_app(settings=None):
    settings = settings or Settings()
    app = Flask(__name__)
    app.config.from_object(settings)
    db = Database(settings.DATABASE_PATH)            # per-app instance, injected below
    produtos = ProdutoModel(db)
    app.register_blueprint(create_produto_blueprint(ProdutoController(produtos)))
    register_error_handlers(app)
    return app
```
For Flask + SQLite prefer one connection per request (`flask.g` + `teardown_appcontext`) over a
shared global connection.
```js
// src/createApp.js
function createApp({ settings, db }) {
  const app = express();
  app.use(express.json());
  const courses = new CourseModel(db);
  const checkout = new CheckoutController({ courses, users: new UserModel(db), payments: new PaymentGateway(settings) });
  app.use(checkoutRoutes(checkout));
  app.use(errorHandler);
  return app;
}
```
Caches/counters become instance members of an injected service, not exported module variables.

## PB-09 — Transactions and referential integrity

**Before**
```js
db.run("DELETE FROM users WHERE id = ?", [id], () => res.send("Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."));
```
**After**
```js
async deleteUserCascade(userId) {
  await this.db.run('BEGIN');
  try {
    await this.db.run('DELETE FROM payments WHERE enrollment_id IN (SELECT id FROM enrollments WHERE user_id = ?)', [userId]);
    await this.db.run('DELETE FROM enrollments WHERE user_id = ?', [userId]);
    await this.db.run('DELETE FROM users WHERE id = ?', [userId]);
    await this.db.run('COMMIT');
  } catch (err) { await this.db.run('ROLLBACK'); throw err; }
}
```
```python
with conn:   # sqlite3 connection as context manager = commit or rollback
    cur = conn.execute("INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)", (uid, STATUS_PENDENTE, total))
    conn.executemany("INSERT INTO itens_pedido (...) VALUES (?, ?, ?, ?)", rows)
    conn.executemany("UPDATE produtos SET estoque = estoque - ? WHERE id = ?", stock_rows)
```
ORM: wrap in one `db.session.commit()` with rollback in the error handler; configure
`cascade="all, delete-orphan"` where deleting the parent must delete children.
Keep the response text/status if clients depend on it, but make the data consistent.

## PB-10 — Signed tokens instead of fake ones

**Before**
```python
return jsonify({"token": "fake-jwt-token-" + str(user.id)})
```
**After** (no new dependency — `itsdangerous` ships with Flask)
```python
from itsdangerous import URLSafeTimedSerializer
def issue_token(settings, user_id):
    return URLSafeTimedSerializer(settings.SECRET_KEY, salt="auth").dumps({"user_id": user_id})
```
Node: `crypto.createHmac('sha256', settings.tokenSecret)` over a base64 payload, or `jsonwebtoken`.
Keep the response field name (`token`).

## PB-11 — Remove N+1 queries

**Before**
```python
for t in Task.query.all():
    user = User.query.get(t.user_id)          # 1 query per task
    cat = Category.query.get(t.category_id)   # 1 more per task
```
**After**
```python
from sqlalchemy.orm import joinedload
tasks = db.session.scalars(select(Task).options(joinedload(Task.user), joinedload(Task.category))).unique().all()
```
Raw SQL:
```python
rows = conn.execute("""
    SELECT i.pedido_id, i.produto_id, i.quantidade, i.preco_unitario, p.nome AS produto_nome
    FROM itens_pedido i LEFT JOIN produtos p ON p.id = i.produto_id
    WHERE i.pedido_id IN ({})""".format(",".join("?" * len(ids))), ids).fetchall()
```
Counts per status: `SELECT status, COUNT(*) FROM tasks GROUP BY status` instead of one query per status.
JS: one `JOIN` query + group in memory instead of `db.get` inside `forEach`.

## PB-12 — Centralized input validation

**Before** — `if "nome" not in dados ... if preco < 0` copy-pasted in create and update, crashing
with 500 when `preco` is a string.

**After**
```python
# src/controllers/validators.py
def validate_produto(dados):
    if not isinstance(dados, dict): raise ValidationError("Dados inválidos")
    for campo, msg in (("nome", "Nome é obrigatório"), ("preco", "Preço é obrigatório"), ("estoque", "Estoque é obrigatório")):
        if campo not in dados: raise ValidationError(msg)
    if not isinstance(dados["preco"], (int, float)) or dados["preco"] < 0: raise ValidationError("Preço não pode ser negativo")
    ...
    return ProdutoInput(...)
```
```js
function validateCheckout(body) {
  const { usr, eml, pwd, c_id: courseId, card } = body || {};
  if (!usr || !eml || !courseId || !card) throw new ValidationError('Bad Request');
  return { name: usr, email: eml, password: pwd, courseId: Number(courseId), card: String(card) };
}
```
Keep the original error messages and status codes so clients see the same contract.

## PB-13 — Central error handler + domain errors

**Before**
```python
def listar_produtos():
    try: ...
    except Exception as e:
        return jsonify({"erro": str(e)}), 500      # repeated in every handler, leaks internals
```
**After**
```python
# src/errors.py
class AppError(Exception):
    status = 400
    def __init__(self, message): super().__init__(message); self.message = message
class ValidationError(AppError): status = 400
class UnauthorizedError(AppError): status = 401
class ForbiddenError(AppError): status = 403
class NotFoundError(AppError): status = 404
class ConflictError(AppError): status = 409

# src/middlewares/error_handler.py
def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({"erro": err.message, "sucesso": False}), err.status
    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception("Unhandled error")
        return jsonify({"erro": "Erro interno do servidor"}), 500
```
```js
// src/middlewares/errorHandler.js
module.exports = (err, req, res, next) => {
  if (err instanceof AppError) return res.status(err.status).send(err.message);
  console.error(err);
  res.status(500).send('Erro interno');
};
```
Use the project's existing error key (`erro` vs `error`) and body type (JSON vs text) so the
contract stays the same. Let `HTTPException` (Flask 404/405) pass through unchanged.

## PB-14 — Extract duplicated logic once

**Before** — the "overdue" rule written inline in 5 handlers:
```python
if t.due_date:
    if t.due_date < datetime.utcnow():
        if t.status != 'done' and t.status != 'cancelled':
            overdue = True
```
**After** — one method on the model, reused everywhere:
```python
CLOSED_STATUSES = frozenset({"done", "cancelled"})
def is_overdue(self, now=None):
    now = now or utcnow_naive()
    return bool(self.due_date and self.due_date < now and self.status not in CLOSED_STATUSES)
```
Same for row→dict mappers: one `_to_dict(row)` per model instead of one per function.

## PB-15 — Replace deprecated APIs

```python
# Before                                  # After
datetime.utcnow()                          datetime.now(timezone.utc)
                                           # naive-UTC columns: datetime.now(timezone.utc).replace(tzinfo=None)
Task.query.get(task_id)                    db.session.get(Task, task_id)
@app.before_first_request                  run init inside create_app()
```
```js
// Before                                 // After
new Buffer(pwd)                           Buffer.from(pwd)
url.parse(req.url)                        new URL(req.url, `http://${req.headers.host}`)
app.use(bodyParser.json())                app.use(express.json())
```
When the DB stores naive UTC datetimes (SQLAlchemy `DateTime` without timezone), keep values naive
UTC to avoid naive/aware comparison errors — use a helper `utcnow_naive()`.

## PB-16 — Callback hell → async/await

**Before**
```js
db.get(sqlA, [a], (err, x) => {
  db.get(sqlB, [b], (err, y) => {
    db.run(sqlC, [c], function (err) { ... res.json(...) });
  });
});
```
**After**
```js
// src/database/connection.js
const { promisify } = require('util');
function wrap(raw) {
  return {
    get: promisify(raw.get.bind(raw)),
    all: promisify(raw.all.bind(raw)),
    run: (sql, params = []) => new Promise((resolve, reject) =>
      raw.run(sql, params, function (err) { err ? reject(err) : resolve({ lastID: this.lastID, changes: this.changes }); })),
  };
}
// controller
const course = await courses.findActiveById(courseId);
const user = await users.findByEmail(email);
const { lastID } = await enrollments.create(user.id, course.id);
```
Express 4 does not catch rejected promises: wrap handlers with
`const asyncHandler = fn => (req, res, next) => Promise.resolve(fn(req, res, next)).catch(next);`

## PB-17 — Named constants

**Before**
```python
if faturamento > 10000: desconto = faturamento * 0.1
elif faturamento > 5000: desconto = faturamento * 0.05
```
**After**
```python
# src/config/constants.py (or controllers/<domain>_rules.py)
DISCOUNT_TIERS = ((10000, 0.10), (5000, 0.05), (1000, 0.02))   # (threshold, rate), descending
def desconto_para(faturamento):
    return next((faturamento * rate for limite, rate in DISCOUNT_TIERS if faturamento > limite), 0)
```
```js
const APPROVED_CARD_PREFIX = '4'; const PAYMENT_STATUS = Object.freeze({ PAID: 'PAID', DENIED: 'DENIED' });
```

## PB-18 — Rename, delete dead code, simplify booleans

```python
# Before
import os, sys, json, time      # unused
def is_admin(self):
    if self.role == 'admin':
        return True
    else:
        return False
if type(tags) == list: ...
# After
def is_admin(self): return self.role == "admin"
if isinstance(tags, list): ...
```
```js
// Before
let u = req.body.usr; let e = req.body.eml; let cc = req.body.card;
// After (wire names unchanged, internal names meaningful)
const { usr: name, eml: email, card: cardNumber } = req.body;
```

## PB-19 — Real logger instead of print/console.log

```python
# Before
print("Produto criado com ID: " + str(id))
# After
logger = logging.getLogger(__name__)
logger.info("Produto criado id=%s", produto_id)
```
```js
// Before: console.log(`[LOG] Salvando no cache: ${key}`)
// After: a tiny logger module with levels (or pino/winston if already a dependency)
logger.info('cache.set', { key });
```
Fake side effects (`print("ENVIANDO EMAIL")`) move to a `services/notification_service` with the
same observable behaviour, so they can later be replaced by a real implementation via DI.
