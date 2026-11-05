# Anti-Patterns Catalog (Phase 2)

Each entry has: **ID**, default **severity**, what it is, **detection signals** (concrete, greppable
where possible, per language), how to raise/lower severity, and the playbook pattern that fixes it
(`PB-xx` in `refactoring-playbook.md`).

## Severity scale (MVC + SOLID based)

| Severity | Meaning |
|---|---|
| **CRITICAL** | Serious architecture or security flaw that breaks correct behaviour, exposes sensitive data (hardcoded credentials, SQL injection, leaked secrets) or completely violates separation of concerns (God class with DB + business logic + routing in one place). |
| **HIGH** | Strong MVC/SOLID violation that makes maintenance and testing very hard (heavy business logic inside routes/controllers, tight coupling without dependency injection, mutable global state, insecure runtime config). |
| **MEDIUM** | Standardisation problems, duplication or moderate performance bottlenecks (N+1 queries, misuse of middleware, missing validation, deprecated APIs, scattered error handling). |
| **LOW** | Readability: bad names, magic numbers, unused imports, print-debugging, verbose conditionals. |

Rules: use the default severity unless an escalation/de-escalation rule below applies. When one
location matches two entries, report both only if the fixes differ.

## Quick index

| ID | Anti-pattern | Default severity | Fix |
|---|---|---|---|
| AP-01 | Hardcoded credentials / secrets | CRITICAL | PB-01 |
| AP-02 | SQL injection (query built from strings) | CRITICAL | PB-02 |
| AP-03 | God class / God module | CRITICAL | PB-03 |
| AP-04 | Insecure password storage | CRITICAL | PB-04 |
| AP-05 | Unprotected destructive / admin endpoints | CRITICAL | PB-05 |
| AP-06 | Sensitive data exposure (responses / logs) | CRITICAL / HIGH | PB-06 |
| AP-07 | Business logic in routes / views ("fat route") | HIGH | PB-07 |
| AP-08 | Mutable global state | HIGH | PB-08 |
| AP-09 | Tight coupling, no dependency injection | HIGH | PB-08 |
| AP-10 | Insecure runtime configuration (debug on, bind-all) | HIGH | PB-01 |
| AP-11 | Missing transaction / broken referential integrity | HIGH | PB-09 |
| AP-12 | Fake or predictable authentication token | HIGH | PB-10 |
| AP-13 | N+1 queries / queries in loops | MEDIUM | PB-11 |
| AP-14 | Missing or inconsistent input validation | MEDIUM | PB-12 |
| AP-15 | Scattered / swallowed error handling | MEDIUM | PB-13 |
| AP-16 | Duplicated logic | MEDIUM | PB-14 |
| AP-17 | Deprecated / obsolete APIs | MEDIUM | PB-15 |
| AP-18 | Callback hell / deep nesting | MEDIUM | PB-16 |
| AP-19 | Magic numbers / magic strings | LOW | PB-17 |
| AP-20 | Poor naming | LOW | PB-18 |
| AP-21 | Unused imports / dead code | LOW | PB-18 |
| AP-22 | `print` / `console.log` used as logging | LOW | PB-19 |
| AP-23 | Verbose boolean logic / redundant conditionals | LOW | PB-18 |

---

## CRITICAL

### AP-01 — Hardcoded credentials / secrets
Secrets committed in source: framework secret keys, DB users/passwords, API/payment keys, SMTP
passwords, JWT secrets.
- Python: `SECRET_KEY\s*[\]=:]\s*['"]`, `password\s*=\s*['"]`, `app.config\[".*KEY"\]\s*=\s*"`
- JS/TS: object literals / consts with keys matching `/(pass|pwd|secret|key|token|apiKey)\w*\s*[:=]\s*["'][^"']{3,}/i`
  (e.g. `dbPass: "..."`, `paymentGatewayKey: "pk_live_..."`)
- Any language: strings starting `pk_live_`, `sk_live_`, `AKIA`, `ghp_`, `xox`, `-----BEGIN`
- Seed data with real-looking default passwords is LOW unless used in production code paths.
Escalate: none (always CRITICAL). Fix: PB-01.

### AP-02 — SQL injection
User-controlled values concatenated/interpolated into SQL.
- Python: `execute\(\s*f["']`, `execute\(.*["']\s*\+`, `"SELECT .*" \+ `, `% (` inside SQL, `.format(` on SQL strings
- JS/TS: SQL string with `+ req.`/`+ id` or template literal `` `...${...}...` `` passed to `db.run/get/all/query`
- ORM raw: `text(f"...")`, `db.engine.execute(f"...")`, `sequelize.query(\`...${`
Safe: placeholders (`?`, `%s`, `:name`, `$1`) with a separate params argument; ORM filter API.
Fix: PB-02.

### AP-03 — God class / God module
One class/file owns routing **and** business rules **and** persistence (≥3 responsibility tags from
project-analysis §7), usually >150 lines and spanning several domain entities.
- File imports both the web framework request object and the DB driver
- One class with methods for DB init, schema, seeding, route registration and business flows
  (e.g. `initDb()` + `setupRoutes(app)` in the same class)
- One `models.py`/`utils.js` containing CRUD for every entity + reports + validation
Report with the full line range (`file:1-314`). Fix: PB-03.

### AP-04 — Insecure password storage
- Plaintext: password column written straight from the request (`INSERT ... senha ...` with the raw value), login comparing `senha = '<input>'` in SQL
- Fast/unsalted hashes: `hashlib.md5(`, `hashlib.sha1(`, `hashlib.sha256(` on passwords, `createHash('md5'|'sha1')`
- Home-made "crypto": base64 / string manipulation loops presented as hashing (`Buffer.from(pwd).toString('base64')`)
Fix: PB-04.

### AP-05 — Unprotected destructive / admin endpoints
Endpoints that execute arbitrary SQL, reset/drop data, or expose financial/admin reports without
any authentication/authorisation check.
- Routes containing `admin`, `reset`, `query`, `debug`, `exec` + no auth decorator/middleware
- Handler passing request body straight into `execute(` (also AP-02)
- `DELETE` routes without ownership/role check
Severity: CRITICAL for arbitrary SQL / data wipe; HIGH for read-only admin reports. Fix: PB-05.

### AP-06 — Sensitive data exposure
- Responses: serializers returning `password`/`senha`/hash fields (`to_dict()` including password,
  `SELECT *` on users returned as-is); health/debug endpoints returning `secret_key`, DB paths,
  `debug` flags; raw exception messages `str(e)` returned to clients (also AP-15)
- Logs: card numbers, passwords, API keys interpolated into `print`/`console.log`
Severity: CRITICAL when secrets/keys/card data leak; HIGH for password hashes or PII. Fix: PB-06.

## HIGH

### AP-07 — Business logic in routes / views ("fat route")
Route handlers that, beyond parsing input and returning a response, compute business rules, run
queries, loop over aggregates or orchestrate side effects (payments, notifications).
- Handler body > ~30 lines; ORM/SQL calls inside handler (`Model.query`, `db.session`, `db.run`)
- Status/discount/overdue rules (`if faturamento > 10000`, `if t.due_date < now and status != 'done'`) inside handlers
- Side effects in handler (`print("ENVIANDO EMAIL")`, gateway calls)
Fix: PB-07.

### AP-08 — Mutable global state
- Python: `global` keyword, module-level mutable containers/connections mutated at runtime (`db_connection = None` + `global db_connection`)
- JS: module-level `let` objects/counters exported and mutated (`let globalCache = {}`, `let totalRevenue = 0`), singletons mutated by handlers
Severity: HIGH when shared across requests; MEDIUM for read-only module constants misuse. Fix: PB-08.

### AP-09 — Tight coupling, no dependency injection
- Handlers/models import and call a concrete DB connection/function directly (`from database import get_db` in every layer)
- Classes instantiate their own dependencies (`this.db = new sqlite3.Database(...)` inside a constructor, `NotificationService()` created inside a route)
- No composition root / app factory (`create_app()`, `createApp()`); app object created at import time
Fix: PB-08.

### AP-10 — Insecure runtime configuration
- `debug=True`, `app.config["DEBUG"] = True`, `app.run(debug=True, host="0.0.0.0")` (Werkzeug debugger = remote code execution)
- CORS wide open (`CORS(app)` with no origins) combined with credentialed endpoints — mention as part of this finding
- Hard-coded ports/hosts/DB paths with no environment override
Fix: PB-01.

### AP-11 — Missing transaction / broken referential integrity
- Multi-step writes (order + items + stock; enrollment + payment + audit) without a transaction or rollback on failure
- Deleting a parent row while children remain (`DELETE FROM users` while enrollments/payments reference it; response even admits "ficaram sujos")
- Check-then-act races on stock without atomic update
Fix: PB-09.

### AP-12 — Fake or predictable authentication token
- Tokens built from predictable data: `'fake-jwt-token-' + str(user.id)`, `"token-" + id`
- Login endpoint that returns user data but issues no verifiable credential
Fix: PB-10.

## MEDIUM

### AP-13 — N+1 queries / queries inside loops
- Python: a query call (`.query.get(`, `.query.filter`, `cursor.execute(`) inside a `for` loop over rows of another query; `len(u.tasks)` on a lazy relationship inside a loop
- JS: `db.get/all/run` inside `forEach`/`for`/`map` callbacks
- Several `COUNT(*)` queries that could be one `GROUP BY`
Severity: MEDIUM (HIGH if inside a hot listing endpoint with unbounded rows). Fix: PB-11.

### AP-14 — Missing or inconsistent input validation
- Request fields used without type/range checks (`dados["preco"] < 0` crashes when `preco` is a string; `priority < 1` with `None`)
- Validation rules duplicated with different limits between create and update
- Required fields not checked (`PUT` without body check, `request.get_json()` possibly `None`)
Fix: PB-12.

### AP-15 — Scattered / swallowed error handling
- Same `try/except Exception as e: return jsonify({"erro": str(e)}), 500` in every handler
- Bare `except:` (Python) or ignored `err` in callbacks (JS `(err) => { res.send(...) }` without checking `err`)
- No central error handler (`@app.errorhandler`, Express `(err, req, res, next)` middleware)
Fix: PB-13.

### AP-16 — Duplicated logic
Same block (≥5 lines or same rule) in ≥2 places: row→dict mapping repeated per function, "is overdue"
rule copied across files, identical validation in create/update, identical order-loading loops.
Fix: PB-14.

### AP-17 — Deprecated / obsolete APIs
Use of APIs deprecated or removed in the detected runtime/framework version. Always recommend the
modern equivalent.

| Stack | Deprecated | Modern replacement |
|---|---|---|
| Python ≥3.12 | `datetime.utcnow()`, `datetime.utcfromtimestamp()` | `datetime.now(timezone.utc)`, `datetime.fromtimestamp(ts, timezone.utc)` |
| SQLAlchemy ≥2.0 / Flask-SQLAlchemy ≥3 | `Model.query.get(id)` (legacy Query API) | `db.session.get(Model, id)`; `db.get_or_404(Model, id)` |
| SQLAlchemy ≥2.0 | `Model.query.filter_by(...).all()` in new code | `db.session.scalars(select(Model).filter_by(...)).all()` (legacy API still works — LOW) |
| Flask ≥2.3 | `@app.before_first_request`, `flask.json.JSONEncoder`, `app.json_encoder` | app-factory init code, `app.json` provider |
| Python | `imp`, `distutils`, `pkg_resources`, `asyncio.get_event_loop()` outside loop, `logging.warn` | `importlib`, `setuptools`/`packaging`, `importlib.metadata`, `asyncio.run`, `logging.warning` |
| Node | `new Buffer()`, `url.parse()`, `fs.exists()`, `crypto.createCipher()`, `util.isArray()`, `require('domain')` | `Buffer.from()`, `new URL()`, `fs.existsSync`/`fs.promises.access`, `crypto.createCipheriv()`, `Array.isArray()`, async error handling |
| Express 4/5 | `body-parser` package, `req.param()`, `res.send(status)`, `res.json(status, obj)`, `app.del()` | `express.json()`, `req.params/query/body`, `res.sendStatus()`, `res.status().json()`, `app.delete()` |
| Node sqlite3 | callback-only API nested in handlers | promise wrapper (`util.promisify`) / `async` repository functions |

Severity: MEDIUM when it emits deprecation warnings or is removed in the next major; LOW when only
stylistically legacy. If none apply, write in the report that no deprecated API was found (do not
invent one). Fix: PB-15.

### AP-18 — Callback hell / deep nesting
≥3 nested callbacks or ≥4 nested `if` levels in one function; manual counters to know when async
loops finish (`pending--; if (pending === 0) res.json(...)`). Fix: PB-16.

## LOW

### AP-19 — Magic numbers / magic strings
Unnamed literals with business meaning: discount thresholds (`10000`, `0.1`), status strings repeated
(`'pendente'`, `'PAID'`), limits (`200`, `4`), card rules (`startsWith("4")`), ports. Fix: PB-17.

### AP-20 — Poor naming
Single-letter / cryptic names outside tiny lambdas (`u`, `e`, `p`, `cc`, `cid`, `usr`, `eml`),
misleading names (`badCrypto`, `AppManager`, `utils` holding config), shadowing built-ins (`id`, `type`).
Note: public request field names (e.g. JSON `usr`, `eml`) are part of the API contract — rename
internal variables, not the wire format. Fix: PB-18.

### AP-21 — Unused imports / dead code
Imported names never referenced (`import os, sys, json` unused), unused functions/constants,
commented-out code. Verify with a search for each name before reporting. Fix: PB-18.

### AP-22 — print / console.log as logging
`print(`/`console.log(` used for operational logs or fake side effects; no log levels. (If they leak
secrets, report AP-06 instead.) Fix: PB-19.

### AP-23 — Verbose boolean logic / redundant conditionals
`if cond: return True else: return False`, nested `if` chains that are one boolean expression,
`type(x) == list` instead of `isinstance`. Fix: PB-18.
