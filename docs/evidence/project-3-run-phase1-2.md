I'll start Phase 1 — project analysis.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/references/project-analysis.md

> [tool] Bash: pwd && git rev-parse --show-toplevel && ls -la

> [tool] Bash: find . -type f \( -name '*.py' -o -name '*.js' -o -name '*.ts' -o -name '*.sql' -o -name '*.http' \) -not -path './node_modules/*' -not -path './.venv/*' -not -

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/README.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/requirements.txt

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/app.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/database.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/__init__.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/task.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/user.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/models/category.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/task_routes.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/user_routes.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/routes/report_routes.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/utils/helpers.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/services/notification_service.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/seed.py

> [tool] Bash: cat routes/__init__.py services/__init__.py utils/__init__.py; echo "---"; python3 --version; .venv/bin/python --version 2>/dev/null; .venv/bin/pip show flask f

> [tool] Bash: find . -type f -name '*.py' -not -path './.venv/*' -not -path './.claude/*' -not -path '*/__pycache__/*' | wc -l

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.13.0 (venv local .venv)
Framework:     Flask 3.0.0 + Flask-SQLAlchemy 3.1.1 (Blueprints)
Dependencies:  flask==3.0.0, flask-sqlalchemy==3.1.1, flask-cors==4.0.0, marshmallow==3.20.1, requests==2.31.0, python-dotenv==1.0.0
Domain:        Task Manager — gestão de tarefas com usuários, categorias, relatórios de produtividade e login
Architecture:  PARTIALLY LAYERED — existem pastas models/, routes/, services/, utils/, mas as rotas concentram regra de negócio + persistência + serialização, config está inline em app.py, não há controllers nem middleware de erro, e services/ está órfão (nunca importado)
Source files:  15 files analyzed (~1158 lines; 3 __init__.py são vazios/re-export)
Entry point:   app.py (pip install -r requirements.txt && python seed.py && python app.py — porta 5000)
DB:            SQLite (sqlite:///tasks.db) via SQLAlchemy ORM — tables: users, categories, tasks
Endpoints:     22 routes (app.py: 2, routes/task_routes.py: 7, routes/user_routes.py: 7, routes/report_routes.py: 6)
================================
```

**Mapa de responsabilidades**

| Arquivo | Tags |
|---|---|
| `app.py` | ROUTING, CONFIG, PRESENTATION |
| `database.py` | PERSISTENCE (instância `db`) |
| `models/*.py` | PERSISTENCE, BUSINESS (validações, `is_overdue`), PRESENTATION (`to_dict`) |
| `routes/task_routes.py` | ROUTING, BUSINESS, PERSISTENCE, PRESENTATION (299 linhas → God-module) |
| `routes/user_routes.py` | ROUTING, BUSINESS, PERSISTENCE, PRESENTATION (211 linhas → God-module) |
| `routes/report_routes.py` | ROUTING, BUSINESS, PERSISTENCE, PRESENTATION (223 linhas → God-module; mistura relatórios **e** CRUD de categorias) |
| `services/notification_service.py` | INFRA, CONFIG (credenciais hard-coded) — **órfão** |
| `utils/helpers.py` | BUSINESS, CONFIG (constantes) — `process_task_data` nunca usado |
| `seed.py` | PERSISTENCE (bootstrap) |

Agora Fase 2 — auditoria.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/references/anti-patterns-catalog.md

> [tool] Bash: python3 /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/scripts/scan_antipatterns.py .

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/references/report-template.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/task-manager-api/.claude/skills/refactor-arch/references/mvc-guidelines.md

> [tool] Bash: for n in notification_service NotificationService process_task_data VALID_STATUSES VALID_ROLES MAX_TITLE_LENGTH MIN_PASSWORD_LENGTH DEFAULT_PRIORITY DEFAULT_COL

Agora vou escrever o relatório.

> [tool] Bash: mkdir -p ../reports && echo ok

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/reports/audit-project-3.md

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3.13 + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1158 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 7 | HIGH: 7 | MEDIUM: 5 | LOW: 5
```

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | Segredos hard-coded (SECRET_KEY e senha SMTP) | `app.py:13`; `services/notification_service.py:7-10` |
| F-02 | CRITICAL | Hash de senha exposto nas respostas da API | `models/user.py:16-25`; `routes/user_routes.py:33,85-86,129,209` |
| F-03 | CRITICAL | Armazenamento inseguro de senha (MD5 sem salt) | `models/user.py:27-32` |
| F-04 | CRITICAL | God module: relatórios + CRUD de categorias | `routes/report_routes.py:1-223` |
| F-05 | CRITICAL | God module: rotas + negócio + ORM + serialização | `routes/task_routes.py:1-299` |
| F-06 | CRITICAL | God module: rotas + autenticação + ORM | `routes/user_routes.py:1-211` |
| F-07 | CRITICAL | Endpoints destrutivos/escrita sem autenticação | `routes/*` (9 handlers) |
| F-08 | HIGH | Config insegura (debug, 0.0.0.0, CORS aberto) | `app.py:11-16,34` |
| F-09 | HIGH | Sem app factory; app construído no import | `app.py:9-31`; `seed.py:2` |
| F-10 | HIGH | Fat routes (relatórios) | `routes/report_routes.py:13-101,104-155` |
| F-11 | HIGH | Integridade referencial quebrada em DELETE | `routes/report_routes.py:211-223`; `routes/user_routes.py:140-151` |
| F-12 | HIGH | Fat routes (tasks) | `routes/task_routes.py:12-63,85-154,156-223,240-299` |
| F-13 | HIGH | Fat routes (usuários/login) | `routes/user_routes.py:43-90,92-132,153-183,185-211` |
| F-14 | HIGH | Token de autenticação falso e previsível | `routes/user_routes.py:207-211` |
| F-15 | MEDIUM | APIs depreciadas (`datetime.utcnow`, `query.get`) | 39 ocorrências em 8 arquivos |
| F-16 | MEDIUM | Lógica duplicada (atraso ×6, serialização, validação) | `models/task.py`; `routes/*` |
| F-17 | MEDIUM | N+1 queries e listagens sem paginação | `routes/*` (6 clusters) |
| F-18 | MEDIUM | Erro espalhado/engolido (12 `except:` nus) | `routes/*`; `utils/helpers.py` |
| F-19 | MEDIUM | Validação ausente/inconsistente (tipo errado → 500) | `routes/*` |
| F-20 | LOW | Imports não usados e ~150 linhas de código morto | `app.py:7`; `services/*`; `utils/helpers.py` |
| F-21 | LOW | Magic numbers / magic strings | `models/task.py`; `routes/*` |
| F-22 | LOW | Booleano verboso e `type() ==` | `models/task.py:38-60`; `models/user.py:34-38` |
| F-23 | LOW | Nomes pobres (`t`, `u`, `c`, `td`) | `routes/*`; `seed.py` |
| F-24 | LOW | `print` como log (13 ocorrências) | `routes/*`; `services/*`; `utils/helpers.py` |

**Destaques** (findings completos com evidência, impacto e recomendação estão no arquivo):

- **F-07** é o mais grave na prática: a API não tem *nenhuma* autenticação. Qualquer requisição anônima cria usuário com `role: "admin"` (`routes/user_routes.py:71-78`), troca a senha de qualquer um (`114-117`) e apaga usuário + todas as tasks (`134-151`).
- **F-02 + F-03** se compõem: MD5 sem salt (`models/user.py:29`) e o hash devolvido em 4 endpoints via `to_dict()` (`models/user.py:21`).
- **F-16** mostra a regra "task atrasada" escrita 6 vezes idênticas — incluindo `Task.is_overdue()`, que existe e nunca é chamado.
- **F-20**: `services/notification_service.py` é órfão, e 9 das 10 funções de `utils/helpers.py` + todas as 6 constantes nunca são usadas — inclusive `VALID_STATUSES`, que resolveria o F-21.

**Deprecated APIs**: confirmados — `datetime.utcnow()` em 24 pontos (depreciado no Python ≥3.12 → `datetime.now(timezone.utc)`) e `Model.query.get()` em 15 pontos (API legada SQLAlchemy 2.0 → `db.session.get(Model, id)`). Tabela por linha no relatório.

**Architecture Notes** — alvo: evolução *in place* (PARTIALLY LAYERED), mantendo `models/` e `routes/` e adicionando `config/`, `controllers/`, `middlewares/`, `services/` + app factory, com `category_routes.py` extraído de `report_routes.py` e `utils/helpers.py` dissolvido.

```text
Total: 24 findings
Report saved to /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/reports/audit-project-3.md
```

Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]

<!-- session_id=999be9c3-9245-4e49-b13d-bfae33731dd2 turns=27 cost_usd=1.8707259999999999 -->
