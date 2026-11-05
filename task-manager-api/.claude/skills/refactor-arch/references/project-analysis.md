# Project Analysis Heuristics (Phase 1)

Goal: build an accurate, evidence-based picture of the project **before** judging it. Every value
printed in the Phase 1 block must come from a file you read or a command you ran.

## 1. Source inventory

Include: application source files (`*.py`, `*.js`, `*.ts`, `*.mjs`, `*.cjs`, `*.go`, `*.rb`,
`*.java`, `*.kt`, `*.php`, `*.cs`), SQL/schema files, seed scripts, HTTP request collections
(`*.http`, Postman JSON) — the last two only as *documentation* of endpoints.

Exclude: `.git/`, `.claude/`, `node_modules/`, `.venv/`, `venv/`, `env/`, `__pycache__/`,
`dist/`, `build/`, `coverage/`, `*.lock`, `package-lock.json`, `*.db`, `*.sqlite`, `*.min.js`.

Count: "Source files" = application source files only (empty `__init__.py` files count — they are
part of the package structure — but say so if they dominate). LOC via:

```bash
find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' \) \
  -not -path './node_modules/*' -not -path './.venv/*' -not -path './.claude/*' -not -path './.git/*' \
  | xargs wc -l
```

## 2. Language detection

| Signal (manifest / file) | Language | Version source |
|---|---|---|
| `requirements.txt`, `pyproject.toml`, `setup.py`, `Pipfile`, `*.py` | Python | `python3 --version`, `requires-python`, `.python-version` |
| `package.json` + `*.js`/`*.mjs`/`*.cjs` | JavaScript (Node.js) | `engines.node`, `.nvmrc`, `node --version` |
| `package.json` + `tsconfig.json` / `*.ts` | TypeScript (Node.js) | `typescript` devDependency |
| `go.mod` | Go | `go` directive |
| `pom.xml`, `build.gradle(.kts)` | Java / Kotlin | `<java.version>`, `jvmToolchain` |
| `Gemfile` | Ruby | `.ruby-version` |
| `composer.json` | PHP | `require.php` |
| `*.csproj` | C# | `TargetFramework` |

If several languages exist, the one owning the entry point is the primary language.

## 3. Framework detection

| Language | Dependency / import signal | Framework | Route declaration signal |
|---|---|---|---|
| Python | `flask` in requirements; `Flask(__name__)` | Flask | `@app.route`, `@bp.route`, `app.add_url_rule`, `Blueprint(` |
| Python | `fastapi`; `FastAPI()` | FastAPI | `@app.get/post`, `APIRouter(` |
| Python | `django`; `manage.py`, `urls.py` | Django | `path(`, `re_path(` in `urls.py` |
| Node | `express`; `express()` | Express | `app.get/post/put/delete(`, `router.<verb>(`, `express.Router()` |
| Node | `fastify` / `@nestjs/core` / `koa` | Fastify / NestJS / Koa | `fastify.get(`, `@Get()`, `router.get(` |
| Go | `gin-gonic/gin`, `labstack/echo`, `net/http` | Gin / Echo / stdlib | `r.GET(`, `e.GET(`, `http.HandleFunc(` |
| Java | `spring-boot-starter-web` | Spring Boot | `@GetMapping`, `@RestController` |
| Ruby | `rails` / `sinatra` | Rails / Sinatra | `routes.rb`, `get '/x' do` |

Report the **declared** version from the manifest (`flask==3.1.1`, `"express": "^4.18.2"`). If the
installed version is known (`pip show`, `npm ls`), you may add it.

## 4. Database detection

| Signal | Engine / access style |
|---|---|
| `import sqlite3`, `sqlite3.connect(` | SQLite, raw driver (Python) |
| `require('sqlite3')`, `new sqlite3.Database(` | SQLite, raw driver (Node); `':memory:'` = in-memory, data lost on restart |
| `flask_sqlalchemy`, `SQLAlchemy()`, `db.Model` | SQLAlchemy ORM; URI in `SQLALCHEMY_DATABASE_URI` |
| `psycopg`, `pg`, `mysql`, `mysql2`, `pymysql` | PostgreSQL / MySQL raw driver |
| `prisma`, `sequelize`, `typeorm`, `mongoose`, `knex` | ORM / query builder |

Tables: collect from `CREATE TABLE` statements, `__tablename__`, ORM model classes, migrations.

## 5. Entry point & run command

Order of precedence: README "how to run" section → `package.json` `scripts.start` / `main` →
`if __name__ == "__main__":` / `app.run(` → `app.listen(` → `Procfile` / Dockerfile `CMD`.
Also record: port (hard-coded or env), seed/bootstrap scripts that must run first, and whether the
DB is created on boot.

## 6. Domain inference

Derive the domain from entity names (tables, models, route prefixes) and user-facing strings.
Name the domain and list the main entities in the project's own vocabulary, e.g.
"E-commerce API (produtos, pedidos, usuários)", "LMS with checkout (courses, enrollments, payments)",
"Task Manager (tasks, users, categories, reports)".

## 7. Architecture mapping

For each source file, tag which responsibilities it contains:

| Tag | Evidence |
|---|---|
| ROUTING | route declarations, request parsing (`request.get_json`, `req.body`) |
| BUSINESS | rules/calculations (discounts, stock checks, status transitions, payment decisions) |
| PERSISTENCE | SQL strings, `cursor.execute`, ORM queries (`.query.`, `db.session`), `db.run/get/all` |
| CONFIG | secrets, URIs, ports, flags (`DEBUG`, `SECRET_KEY`) |
| PRESENTATION | response formatting / serialization (`jsonify`, `res.json`, `to_dict`) |
| INFRA | e-mail/SMS/payment gateways, logging, caching |

Then classify:

| Level | Criteria | Phase 3 strategy |
|---|---|---|
| `MONOLITH` | One or few files mix ≥3 tags; no layer folders; routes wired directly to DB code | Full restructure into the MVC layout |
| `PARTIALLY LAYERED` | Layer folders exist (`models/`, `routes/`, `services/`...) **but** routes still contain BUSINESS + PERSISTENCE, config is inline, no controllers/error middleware | Evolve in place: add missing layers, thin out routes, centralise config/errors |
| `LAYERED` | Each file has one dominant tag, dependencies point inward | Targeted fixes only |

A file with ≥3 tags and >150 lines is a God-module candidate (AP-03).

## 8. Endpoint inventory

List every route as `METHOD /path → file:line handler`. Count it for the Phase 1 block. This list
becomes the smoke-test spec in Phase 3, so do not skip routes (including admin/debug routes).
