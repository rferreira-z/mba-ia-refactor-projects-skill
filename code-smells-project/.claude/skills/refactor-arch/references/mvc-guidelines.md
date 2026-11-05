# MVC Architecture Guidelines (Phase 3 target)

The target is a **layered MVC architecture for HTTP APIs**. In an API there is no HTML template, so
the **View** is the HTTP boundary: routes + request parsing + response serialization.

```text
HTTP request
   │
   ▼
View / Routes  ──►  Controller  ──►  Model (entity + repository)  ──►  Database
 (HTTP in/out)      (use cases,       (data access, mapping,
                     business rules)    persistence only)
   ▲                    │
   └── serialized ◄─────┘   Errors bubble up as typed exceptions ──► Error-handling middleware
```

Dependencies point **one way**: Views → Controllers → Models. Models never import Flask/Express;
Controllers never touch `request`/`req`/`res`; Views never contain SQL/ORM calls.

## Layers and responsibilities

| Layer | Folder | MUST | MUST NOT |
|---|---|---|---|
| **Config** | `config/` | Read every setting from environment variables with safe dev defaults (secret key, DB URL/path, debug flag, port, external keys); validate required values at startup | Contain real secrets; be mutated at runtime |
| **Model** | `models/` | Represent entities and encapsulate persistence: parameterized SQL or ORM queries, row↔object mapping, transactions for multi-row writes; expose intention-revealing functions (`find_by_id`, `create`, `list_with_items`) | Import the web framework; read the request; build HTTP responses; hold business policy (discount tiers, payment approval) |
| **Controller** | `controllers/` | Implement use cases / application flow: validate business rules, orchestrate models and services, decide outcomes, raise domain errors (`NotFoundError`, `ValidationError`) | Touch `request`/`res`; return HTTP status codes directly; contain SQL |
| **View / Routes** | `views/` (or existing `routes/`) | Declare endpoints (Blueprint / `express.Router`), parse & shape input, call one controller function, serialize output (including hiding sensitive fields), map success to status codes | Contain business rules or persistence; catch generic exceptions (leave it to the error handler) |
| **Middlewares** | `middlewares/` | Central error handler mapping domain errors → HTTP (400/401/403/404/409/500) with a consistent JSON body; auth guards; request logging | Contain business rules |
| **Services** (optional) | `services/` | Wrap infrastructure / external systems: payment gateway, e-mail/SMS, password hashing, token signing | Know about HTTP |
| **Composition root** | `app.py` / `app.js` (`create_app()` / `createApp()`) | Build config, DB connection, services, register views and middlewares — the **only** place where concrete dependencies are wired | Contain routes or business logic |
| **Entry point** | `app.py` / `server.js` / existing start file | Call the factory and start the server using config (host/port/debug from env) | Anything else |

## Reference layouts

### Python / Flask (from a monolith)

```text
<project>/
├── app.py                         # entry point: from src.app import create_app; app = create_app()
├── requirements.txt
└── src/
    ├── __init__.py
    ├── app.py                     # create_app(): composition root
    ├── config/settings.py         # Settings from os.environ
    ├── database.py                # connection factory / init_db / seed (no global mutable state)
    ├── models/<entity>_model.py   # one per aggregate (produto, usuario, pedido...)
    ├── controllers/<entity>_controller.py
    ├── views/<entity>_routes.py   # Blueprints
    ├── middlewares/error_handler.py
    ├── middlewares/auth.py        # (if admin routes exist)
    ├── services/                  # password hasher, notifications...
    └── errors.py                  # AppError hierarchy
```

Keeping a thin root `app.py` preserves `python app.py` and `flask --app app run`.

### Node / Express

```text
<project>/
├── package.json                   # "start" still works
└── src/
    ├── app.js                     # entry point (keeps the original start command) → createApp() + listen
    ├── createApp.js               # composition root
    ├── config/settings.js         # process.env with dev defaults
    ├── database/connection.js     # opens DB, promisified run/get/all, schema + seed
    ├── models/<entity>Model.js    # repositories (async functions, parameterized SQL)
    ├── controllers/<entity>Controller.js
    ├── views/<entity>Routes.js    # express.Router(), thin async handlers
    ├── middlewares/errorHandler.js  # (err, req, res, next)
    ├── middlewares/asyncHandler.js
    ├── services/                  # paymentGateway.js, passwordHasher.js
    └── errors.js
```

### Already layered project (e.g. `models/`, `routes/`, `services/`, `utils/` present)

Keep the existing folder names that already map 1:1 to a layer (`routes/` = Views, `models/` =
Models). Add what is missing (`config/`, `controllers/`, `middlewares/`, app factory), move business
logic and queries out of the routes into controllers/models, and dissolve `utils/` grab-bags into the
layer each helper belongs to. Do not rename folders purely for cosmetics.

## Strategy by starting point

| Phase 1 level | Strategy |
|---|---|
| `MONOLITH` | Create the full layout above; split god modules by entity; delete the old files once every route is served by the new layers. |
| `PARTIALLY LAYERED` | Evolve in place: introduce app factory + config + error middleware, add `controllers/`, slim routes to ≤ ~15 lines each, push queries into models/repositories, centralise duplicated rules. |
| `LAYERED` | Fix findings locally; do not restructure. |

## Non-negotiable rules for the refactored code

1. No secret literal anywhere in source — config reads env vars; dev defaults must be obviously
   non-production (e.g. `"dev-only-change-me"`), and debug defaults to **off**.
2. All SQL is parameterized; multi-step writes run in a transaction.
3. Passwords are hashed with a slow, salted KDF (Werkzeug `generate_password_hash`, Node
   `crypto.scrypt`/bcrypt); password fields never leave the model/serializer.
4. One error-handling path: views/controllers raise; the middleware formats. Unexpected errors log
   the stack server-side and return a generic 500 body.
5. Business constants live in one place (`constants`/config), not inline.
6. Public API contract preserved: same routes, methods, request field names and response envelopes
   (e.g. `{"dados": ..., "sucesso": true}`), except security-motivated changes listed in the summary.
7. Each file has one responsibility; a file over ~200 lines is a smell to re-check.
