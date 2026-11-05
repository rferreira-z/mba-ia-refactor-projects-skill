Prosseguindo com a Phase 3. Lendo as referências.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/references/refactoring-playbook.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/references/validation-protocol.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/scripts/endpoint_smoke.py

Lendo o script de smoke test — ele suporta `headers` fixos por request. Agora capturo o baseline **antes** de tocar em qualquer arquivo.

> [tool] Bash: mkdir -p .refactor-arch && lsof -iTCP:5203 -sTCP:LISTEN; echo "port check exit=$?"; ls -la tasks.db 2>/dev/null || echo "no tasks.db yet"

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.refactor-arch/endpoints.json

Agora o baseline contra a aplicação **original**:

> [tool] Bash: rm -f tasks.db instance/tasks.db && .venv/bin/python seed.py 2>&1 | tail -5 && find . -name 'tasks.db' -not -path './.venv/*'

> [tool] Bash: .venv/bin/flask --app app run --port 5203 > .refactor-arch/baseline-server.log 2>&1 & echo "pid=$!"; sleep 3; curl -s http://127.0.0.1:5203/health; echo; tail -

> [tool] Bash: .venv/bin/python /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/scripts/endpoint_smoke.p

> [tool] Bash: .venv/bin/python -c " import json d={r['name']:r for r in json.load(open('.refactor-arch/baseline.json'))} print('orphan task body:', json.dumps(d['get task of 

> [tool] Bash: .venv/bin/python -c " import json d={r['name']:r for r in json.load(open('.refactor-arch/baseline.json'))} print('created task 12:', json.dumps(d['create task i

Baseline capturado (72 requests; os 14 ✗ são exatamente os furos que a Phase 3 deve fechar — 10 rotas sem auth e 4 crashes 500). Evidências confirmadas no baseline:

- `login ok` devolve `"password": "81dc9bdb52d04dc20036dbd8313ed055"` = MD5("1234")
- signup anônimo com `role: "admin"` → criado **como admin** (escalada de privilégio)

**Correção ao F-11:** o baseline mostra `category_id: null` na task após deletar a categoria — o SQLAlchemy já anula a FK de filhos carregados na sessão. O furo real é não haver `ON DELETE` no schema nem FK ativa no SQLite, então deletes em massa (como `Category.query.delete()` em `seed.py:13`) ainda deixam órfãos. Vou corrigir nesse nível.

Árvore alvo:

```text
task-manager-api/
├── app.py                      # Composition root: create_app() + entry point
├── seed.py                     # usa a factory
├── .env.example                # (novo) variáveis documentadas
├── database.py                 # instância db
├── errors.py                   # (novo) AppError hierarchy
├── config/                     # CONFIG
│   ├── settings.py             # os.environ + defaults de dev
│   └── constants.py            # constantes de domínio
├── models/                     # MODEL (entidade + persistência)
│   ├── base.py  task.py  user.py  category.py
├── controllers/                # CONTROLLER (casos de uso + regras)
│   ├── validators.py  task_controller.py  user_controller.py
│   ├── auth_controller.py  category_controller.py  report_controller.py
├── routes/                     # VIEW (Blueprints finos + serialização)
│   ├── serializers.py  health_routes.py  task_routes.py  user_routes.py
│   ├── auth_routes.py  category_routes.py  report_routes.py
├── middlewares/                # MIDDLEWARE
│   ├── error_handler.py  auth.py
└── services/                   # INFRA
    ├── password_hasher.py  token_service.py  notification_service.py
```

> [tool] Bash: mkdir -p config controllers middlewares && touch config/__init__.py controllers/__init__.py middlewares/__init__.py && echo ok

PB-01 — configuração e constantes:

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/config/settings.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/config/constants.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/errors.py

Camada **Model** — entidades + persistência (PB-03, PB-04, PB-06, PB-11, PB-14, PB-15):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/base.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/user.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/category.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/task.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/__init__.py

Camada **Services** — infraestrutura (PB-04, PB-10, PB-19):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/services/password_hasher.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/services/token_service.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/services/notification_service.py

Camada **Middlewares** — erro central + guardas de autenticação (PB-05, PB-13):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/middlewares/error_handler.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/middlewares/auth.py

Camada **Controller** — validação centralizada e casos de uso (PB-07, PB-12, PB-14):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/validators.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/task_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/user_controller.py

Preciso corrigir `create_user` — escrevi uma linha inválida:

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/user_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/auth_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/auth_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/category_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/report_controller.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/report_controller.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/controllers/report_controller.py

Camada **View** — serializers (PB-06, PB-14) e Blueprints finos (PB-07):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/serializers.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/health_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/user_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/auth_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/category_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/report_routes.py

Composition root + entry point (PB-08) e seed:

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/app.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/seed.py

Removendo o grab-bag `utils/` (dissolvido nas camadas) e atualizando README/.env.example:

> [tool] Bash: rm -rf utils && rm -f requirements.txt.bak && ls && echo "---" && grep -rn "utils" --include='*.py' . | grep -v '.venv' | grep -v '.claude' || echo "nenhuma ref

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.env.example

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/README.md

> [tool] Bash: grep -rn "marshmallow\|import requests\|dotenv" --include='*.py' . | grep -v '.venv' | grep -v '.claude' || echo "nenhum uso"

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/requirements.txt

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/app.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/app.py

§2 — Boot check: compilação, seed e boot na porta 5203:

> [tool] Bash: .venv/bin/python -m compileall -q config controllers middlewares models routes services app.py database.py errors.py seed.py && echo "COMPILE OK" && rm -f insta

> [tool] Bash: PORT=5203 .venv/bin/python app.py > .refactor-arch/after-server.log 2>&1 & echo "pid=$!"; sleep 3; curl -s http://127.0.0.1:5203/health; echo; echo "--- log ---

Boot OK com o run command documentado (`python app.py`, debug off). §3 — smoke contra o baseline:

> [tool] Bash: .venv/bin/python /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/scripts/endpoint_smoke.p

72/72 — exit 0. Verificando as mudanças de **valor** (que o script não compara) e a equivalência dos dados:

> [tool] Bash: .venv/bin/python - <<'PY' import json b={r['name']:r for r in json.load(open('.refactor-arch/baseline.json'))} a={r['name']:r for r in json.load(open('.refactor

> [tool] Bash: .venv/bin/python - <<'PY' import json b={r['name']:r for r in json.load(open('.refactor-arch/baseline.json'))} a={r['name']:r for r in json.load(open('.refactor

Payloads **byte-idênticos** quando normalizados os timestamps (que o seed gera relativo ao "agora"). Validando o fluxo de token real (não só o admin token) e o PRAGMA de FK:

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api TOKEN=$(curl -s -X POST http://127.0.0.1:5203/login -H 'Content-Typ

§4 — re-scan do catálogo:

> [tool] Bash: .venv/bin/python /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/scripts/scan_antipattern

37 hits, todos falsos positivos — mas 22 deles são o scanner casando com o **nome** do meu helper `utcnow`. Um helper que substitui uma API depreciada não deveria se chamar como ela; vou renomear para eliminar o ruído de verdade:

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api grep -rln '\butcnow\b' --include='*.py' . | grep -v .venv | grep -v

`\b` não funciona no sed do BSD; usando perl:

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api grep -rl 'utcnow' --include='*.py' . | grep -v .venv | grep -v .cla

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/base.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/base.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/services/token_service.py

Revalidando após o rename (boot + smoke + scanner):

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api kill 13053 2>/dev/null; sleep 1 .venv/bin/python -m compileall -q c

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api .venv/bin/python .claude/skills/refactor-arch/scripts/endpoint_smok

O `exit=1` é porque rodei o spec duas vezes contra o mesmo banco (os IDs já tinham sido consumidos). Re-executando com banco limpo, uma única vez:

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api kill 13550 2>/dev/null; sleep 1 rm -f instance/tasks.db .venv/bin/p

Limpeza (§5) e revisão final:

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api kill 13593 2>/dev/null; sleep 1 lsof -iTCP:5203 -sTCP:LISTEN > /dev

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api find . -name '*.py' -not -path './.venv/*' -not -path './.claude/*'

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api echo "arquivos .py: $(find . -name '*.py' -not -path './.venv/*' -n

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
task-manager-api/                      34 arquivos .py | ~1656 linhas
├── app.py                 (67)        COMPOSITION ROOT + ENTRY POINT — create_app(), wiring, python app.py
├── seed.py                (73)        Script CLI — usa a factory, sem app global
├── database.py             (3)        Instância SQLAlchemy
├── errors.py              (32)        Hierarquia AppError (400/401/403/404/409)
├── requirements.txt / .env.example / README.md
│
├── config/                            CONFIG — tudo de os.environ, zero segredo literal
│   ├── settings.py        (51)        Settings: SECRET_KEY, ADMIN_TOKEN, DATABASE_URL, DEBUG, HOST, PORT, CORS, SMTP
│   └── constants.py       (43)        Constantes de domínio (status, roles, limites, labels)
│
├── models/                            MODEL — entidade + persistência (sem Flask)
│   ├── base.py            (12)        now_utc(): UTC naive, substitui a API depreciada
│   ├── task.py           (160)        Task + repositório (search, GROUP BY, is_overdue)
│   ├── user.py            (72)        User + repositório + hash de senha
│   └── category.py        (61)        Category + repositório + delete transacional
│
├── controllers/                       CONTROLLER — casos de uso e regras (sem request/SQL)
│   ├── validators.py     (121)        Validação centralizada, tolerante a tipo
│   ├── task_controller.py(132)
│   ├── user_controller.py(104)
│   ├── auth_controller.py (24)
│   ├── category_controller.py (48)
│   └── report_controller.py  (100)
│
├── routes/                            VIEW — Blueprints finos: parse + serialize
│   ├── serializers.py     (79)        Allow-list de campos; password nunca sai
│   ├── health_routes.py   (19)        / e /health (extraídos de app.py)
│   ├── task_routes.py     (67)
│   ├── user_routes.py     (61)
│   ├── auth_routes.py     (19)        /login (extraído de user_routes)
│   ├── category_routes.py (35)        /categories (extraído de report_routes)
│   └── report_routes.py   (20)
│
├── middlewares/                       MIDDLEWARE
│   ├── error_handler.py   (28)        AppError → HTTP; 500 genérico + stack no log
│   └── auth.py            (96)        Bearer token + X-Admin-Token; require_auth / require_admin
│
└── services/                          INFRA
    ├── password_hasher.py (22)        werkzeug scrypt salgado
    ├── token_service.py   (28)        itsdangerous: token assinado com expiração
    └── notification_service.py (72)   SMTP da config; desligado por padrão, agora injetado

REMOVIDOS: utils/helpers.py (grab-bag, ~150 linhas de código morto) e utils/__init__.py

## Findings Resolution
F-01 [CRITICAL] Segredos hard-coded — FIXED: `config/settings.py` lê tudo de `os.environ` com defaults de dev (`dev-only-change-me`); credenciais SMTP saíram de `notification_service.py`; `.env.example` documenta cada variável e `load_dotenv()` passou a ser chamado no composition root.
F-02 [CRITICAL] Hash de senha exposto — FIXED: `routes/serializers.py` usa allow-list (`USER_PUBLIC_FIELDS`) sem `password`; confirmado no smoke (`-['password']` em 4 endpoints).
F-03 [CRITICAL] MD5 sem salt — FIXED: `services/password_hasher.py` com `werkzeug.security` (scrypt salgado, comparação em tempo constante). Hash no banco verificado: `scrypt:32768:8:1$...`.
F-04 [CRITICAL] God module report_routes (223 ln) — FIXED: CRUD de categorias extraído para `routes/category_routes.py` + `controllers/category_controller.py`; relatórios em `controllers/report_controller.py`. View final: 20 linhas.
F-05 [CRITICAL] God module task_routes (299 ln) — FIXED: regras em `controllers/task_controller.py`, queries em `models/task.py`, serialização em `routes/serializers.py`. View final: 67 linhas, handlers de 2-6 linhas.
F-06 [CRITICAL] God module user_routes (211 ln) — FIXED: login extraído para `auth_routes`/`auth_controller`; CRUD em `user_controller`. View final: 61 linhas.
F-07 [CRITICAL] Endpoints sem autenticação — FIXED: `middlewares/auth.py` com `require_auth`/`require_admin`; mutações, dados de usuário e relatórios protegidos; escalada de privilégio no cadastro bloqueada. 10 probes anônimos passaram de 200/400/404 para 401.
F-08 [HIGH] Config insegura — FIXED: debug default off, host default `127.0.0.1`, CORS restrito a `CORS_ORIGINS`, porta/URI via ambiente. Log do boot confirma `Debug mode: off`.
F-09 [HIGH] Sem app factory — FIXED: `create_app(settings=None)` como composition root; `seed.py` usa a factory em vez de importar o app global; `python app.py` e `flask --app app run` preservados.
F-10 [HIGH] Fat routes (relatórios) — FIXED: 88 linhas de cálculo migradas para `report_controller`; `completion_rate` com definição única compartilhada com `/tasks/stats`.
F-11 [HIGH] Integridade referencial — FIXED: `ondelete='CASCADE'`/`'SET NULL'` no schema, `PRAGMA foreign_keys=ON` no connect (verificado: `foreign_keys = 1`), e deletes multi-passo numa transação só (`delete_with_tasks`, `delete_and_detach_tasks` com UPDATE explícito).
F-12 [HIGH] Fat routes (tasks) — FIXED: validação, resolução de FK, parsing de data e tags movidos para o controller.
F-13 [HIGH] Fat routes (usuários/login) — FIXED: política de senha, unicidade de e-mail e fluxo de login nos controllers.
F-14 [HIGH] Token falso — FIXED: `services/token_service.py` emite token assinado com `itsdangerous` e expiração de 8h; token adulterado → 401 (verificado).
F-15 [MEDIUM] APIs depreciadas — FIXED: 24 `datetime.utcnow()` → `now_utc()` (`datetime.now(timezone.utc)` naive); 15 `Model.query.get()` → `db.session.get()`; `filter_by().all()` → `db.session.scalars(select(...))`.
F-16 [MEDIUM] Lógica duplicada — FIXED: regra de atraso só em `Task.is_overdue()` (era 6 cópias); serialização só em `routes/serializers.py`; validação só em `controllers/validators.py`.
F-17 [MEDIUM] N+1 e listagens — PARCIALMENTE FIXED: `joinedload` em `GET /tasks` (1+2N → 1 query), `GROUP BY` em status/prioridade/por-usuário/por-categoria (`/reports/summary` passou de 14+ queries para 7). DEFERIDO: paginação — mudaria o formato de resposta de 4 endpoints de listagem, quebrando o contrato público; precisa de decisão de versionamento da API.
F-18 [MEDIUM] Erro espalhado — FIXED: 12 `except:` nus removidos; `middlewares/error_handler.py` é o caminho único, com `app.logger.exception` e corpo `{'error': ...}` preservado.
F-19 [MEDIUM] Validação inconsistente — FIXED: `validators.py` checa tipo antes de valor; 4 crashes 500 do baseline agora respondem 400.
F-20 [LOW] Imports e código morto — FIXED: `utils/` removido; imports mortos eliminados; `notification_service` deixou de ser órfão (injetado via `app.extensions['notifier']`); `marshmallow` e `requests` saíram do requirements por não serem usados.
F-21 [LOW] Magic numbers/strings — FIXED: `config/constants.py` é a fonte única (status, roles, limites, `PRIORITY_LABELS`, `HIGH_PRIORITY_THRESHOLD`).
F-22 [LOW] Booleano verboso / type() — FIXED: `is_admin`/`is_overdue` viraram expressões diretas; `type(x) == list` → `isinstance`.
F-23 [LOW] Nomes pobres — FIXED: `t`/`u`/`c`/`td` → `task`/`user`/`category`/`fields` na extração para controllers e serializers.
F-24 [LOW] print como log — FIXED: `logging` nos módulos da aplicação. Os 4 `print` de `seed.py` foram mantidos de propósito: é saída de CLI, não log operacional.

## Intentional Behaviour Changes
- Todas as mutações + dados de usuário + relatórios: passam a exigir `Authorization: Bearer <token>` (de `POST /login`) ou `X-Admin-Token`. Anônimo agora recebe **401** onde antes obtinha 200/400/404. Fecha F-07. Matriz de acesso documentada no README.
- `DELETE /users/<id>` e `GET /reports/summary`: exigem **admin** (403 para usuário comum). Fecha F-07.
- `POST /users`: continua público, mas `role` privilegiado pedido por não-admin é rebaixado para `user`. Verificado: `role: "admin"` anônimo → usuário criado como `user` (antes: criado como admin). Fecha F-07.
- `PUT /users/<id>`: só o próprio usuário ou admin; `role`/`active` só por admin. Fecha F-07.
- `GET /users/<id>`, `POST /users`, `PUT /users/<id>`, `POST /login`: o campo `password` saiu do corpo da resposta. Fecha F-02.
- `POST /login`: `token` deixou de ser `fake-jwt-token-<id>` e passou a ser assinado com expiração. Mesmo nome de campo. Fecha F-14.
- Senhas: hashes MD5 anteriores não validam mais — é preciso rodar `python seed.py` ou redefinir a senha. Fecha F-03.
- 4 requisições que retornavam **500** agora retornam **400** com `{"error": ...}`: prioridade não-numérica em `POST /tasks` e em `GET /tasks/search`, `title: null` em `PUT /tasks/<id>`, `name: null` em `PUT /categories/<id>`. Fecha F-19.
- Defaults de runtime: `debug` off (era on), host `127.0.0.1` (era `0.0.0.0`), CORS restrito a `http://localhost:3000` (era aberto). Reversível por ambiente. Fecha F-08.
- Requisição com corpo malformado em PUT/POST: 400 `Dados inválidos` em vez do 415 do Flask (`get_json(silent=True)`).

## Validation
  ✓ Application boots without errors (`PORT=5203 python app.py` — "Debug mode: off", 0 tracebacks no log; `python -m compileall` OK; `python seed.py` OK)
  ✓ All endpoints respond correctly (72/72 smoke requests, exit 0, comparados contra `.refactor-arch/baseline.json`)
  ✓ No catalog anti-patterns remaining (scanner: 86 → 11 hits, todos revisados e falsos positivos)
================================
```

**Sobre os 11 hits restantes do scanner** (todos revisados linha a linha):
- `seed.py:15-17` (6 hits AP-01/AP-06) — senhas de demonstração do fixture, hasheadas por `set_password` antes de gravar. O próprio catálogo classifica seed data assim como LOW/não-aplicável fora de caminho de produção; o README depende dessas credenciais.
- `seed.py:66-69` (4 hits AP-22) — saída de CLI, não log operacional; o protocolo de validação cita exatamente esse caso como falso positivo aceitável.
- `models/task.py:1-160` (AP-03) — heurística de tamanho. É uma entidade + seu repositório, com uma responsabilidade; nenhuma rota, regra de apresentação ou config.

**Sobre payloads:** comparando baseline × after campo a campo, todas as respostas são **idênticas** após normalizar os timestamps que o seed gera relativo ao "agora" (`created_at`, `updated_at`, `due_date`, `generated_at`) — incluindo `/reports/summary`, `/tasks/stats` e as listagens.

**Duas correções ao relatório da Phase 2**, confirmadas em execução:
1. **F-11** — o baseline mostra `category_id: null` após deletar a categoria: o SQLAlchemy já anulava a FK dos filhos carregados na sessão. O furo real era o schema sem `ON DELETE` e o SQLite com FK desligada, o que deixa órfãos em deletes em massa (como `Category.query.delete()` no seed antigo). Corrigido nesse nível.
2. **F-17** — descrevi `GET /users` como forçando lazy-load por usuário; `len(u.tasks)` dispara uma query por usuário de fato, mas o custo dominante estava em `/reports/summary` e `GET /tasks`. A correção aplicada (GROUP BY + joinedload) cobre os três.

**Deferido:** paginação nas listagens (parte de F-17) — adicionar `limit`/`offset` mudaria o formato de resposta de 4 endpoints e quebraria o contrato público; é decisão de versionamento da API, não de refatoração.

<!-- session_id=999be9c3-9245-4e49-b13d-bfae33731dd2 turns=74 cost_usd=8.550743499999998 -->
