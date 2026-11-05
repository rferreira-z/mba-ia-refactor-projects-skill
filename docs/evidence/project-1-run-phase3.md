Prosseguindo com a Fase 3 na porta 5201.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/references/refactoring-playbook.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/references/validation-protocol.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/scripts/endpoint_smoke.py

> [tool] Bash: lsof -iTCP:5201 -sTCP:LISTEN; echo "exit=$?"

Porta 5201 livre. Capturando o baseline do app **original** antes de tocar em qualquer arquivo.

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.refactor-arch/endpoints.json

> [tool] Bash: ls -la loja.db 2>/dev/null; rm -f loja.db; .venv/bin/python -m flask --app app run --port 5201 > /tmp/claude-501/baseline.log 2>&1 & echo "pid=$!"

> [tool] Bash: for i in 1 2 3 4 5 6 7 8 9 10; do curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5201/ 2>/dev/null && break; done; echo; cat /tmp/claude-501/baseline.l

> [tool] Bash: python3 .claude/skills/refactor-arch/scripts/endpoint_smoke.py .refactor-arch/endpoints.json http://127.0.0.1:5201 --out .refactor-arch/baseline.json; echo "EXI

Baseline gravado. As 5 falhas são exatamente os buracos que a Fase 3 deve fechar — a injeção de SQL no login retornou **200** (bypass confirmado), as rotas admin responderam sem token, e `preco: "abc"` quebrou em **500**.

> [tool] Bash: kill 11040 2>/dev/null; sleep 1; lsof -iTCP:5201 -sTCP:LISTEN; rm -f loja.db; rm -rf __pycache__; ls -la

O baseline cobre o contrato atual. Vou adicionar 3 requisições para os casos de integridade que pretendo corrigir (produto referenciado, e-mail duplicado, pedido inexistente) e **re-capturar o baseline com o código original ainda intacto**, para que cada mudança fique medida.

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.refactor-arch/endpoints.json

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.refactor-arch/endpoints.json

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.refactor-arch/endpoints.json

> [tool] Bash: rm -f loja.db && .venv/bin/python -m flask --app app run --port 5201 > /tmp/claude-501/baseline.log 2>&1 & echo "pid=$!"

> [tool] Bash: for i in $(seq 1 10); do curl -s -o /dev/null http://127.0.0.1:5201/ && break; done python3 .claude/skills/refactor-arch/scripts/endpoint_smoke.py .refactor-arc

> [tool] Bash: kill 12192 2>/dev/null; sleep 1; rm -f loja.db; rm -rf __pycache__ python3 -c " import json b={r['name']:r for r in json.load(open('.refactor-arch/baseline.json

Baseline completo: **49 requisições, 41 verdes, 8 defeitos fixados** como alvo. Agora a reestruturação. Árvore alvo:

```text
code-smells-project/
├── app.py                                  # Entry point (preserva `python app.py`)
├── requirements.txt
├── .env.example                            # novo — todas as variáveis, sem valores reais
├── README.md
└── src/
    ├── app.py                              # COMPOSITION ROOT — create_app()
    ├── errors.py                           # hierarquia AppError (sem framework)
    ├── database.py                         # conexão por request + schema/seed
    ├── config/
    │   ├── settings.py                     # CONFIG — tudo de os.environ
    │   └── constants.py                    # CONFIG — constantes de domínio
    ├── models/                             # MODEL — só SQL parametrizado + mapeamento
    │   ├── produto_model.py
    │   ├── usuario_model.py
    │   └── pedido_model.py
    ├── controllers/                        # CONTROLLER — casos de uso e regras
    │   ├── validators.py
    │   ├── produto_controller.py
    │   ├── usuario_controller.py
    │   ├── pedido_controller.py
    │   ├── relatorio_controller.py
    │   ├── sistema_controller.py
    │   └── admin_controller.py
    ├── views/                              # VIEW — Blueprints finos (HTTP in/out)
    │   ├── produto_routes.py
    │   ├── usuario_routes.py
    │   ├── pedido_routes.py
    │   ├── relatorio_routes.py
    │   ├── sistema_routes.py
    │   └── admin_routes.py
    ├── middlewares/
    │   ├── auth.py                         # guard X-Admin-Token
    │   └── error_handler.py                # tratamento central de erros
    └── services/                           # INFRA
        ├── password_service.py
        ├── token_service.py
        └── notificacao_service.py
```

> [tool] Bash: mkdir -p src/config src/models src/controllers src/views src/middlewares src/services && for d in src src/config src/models src/controllers src/views src/middle

Agora as camadas de base — config, erros e banco (PB-01, PB-08, PB-09, PB-13):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/config/settings.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/config/constants.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/errors.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/database.py

Agora a camada **Model** — só SQL parametrizado, mapeamento e transações (PB-02, PB-09, PB-11, PB-14):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/models/produto_model.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/models/usuario_model.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/models/pedido_model.py

Camada de **Services** (infraestrutura) — hash, token e notificações (PB-04, PB-10, PB-19):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/services/password_service.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/services/token_service.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/services/notificacao_service.py

Camada **Controller** — casos de uso e validação centralizada (PB-07, PB-12, PB-14, PB-17):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/validators.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/produto_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/usuario_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/pedido_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/relatorio_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/sistema_controller.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/controllers/admin_controller.py

Middlewares (PB-05, PB-13) e a camada **View** — Blueprints finos:

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/middlewares/error_handler.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/middlewares/auth.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/middlewares/auth.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/views/produto_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/views/usuario_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/views/pedido_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/views/relatorio_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/views/sistema_routes.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/views/admin_routes.py

O composition root e o entry point (PB-08):

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/app.py

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/app.py

Removendo os god modules obsoletos e atualizando a documentação:

> [tool] Bash: rm -f controllers.py models.py database.py && ls -1

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.env.example

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/README.md

Validação — compilação, boot e smoke contra o baseline:

> [tool] Bash: .venv/bin/python -m compileall -q src app.py && echo "COMPILE OK" rm -f loja.db SECRET_KEY=smoke-secret ADMIN_TOKEN=smoke-admin-token DATABASE_PATH=loja.db .ven

> [tool] Bash: for i in $(seq 1 15); do curl -s -o /dev/null http://127.0.0.1:5201/ && break; done; cat /tmp/claude-501/after.log

> [tool] Bash: python3 .claude/skills/refactor-arch/scripts/endpoint_smoke.py .refactor-arch/endpoints.json http://127.0.0.1:5201 --compare .refactor-arch/baseline.json --out 

49/49 verdes. Verificando o que o diff de chaves de topo não alcança — `senha` dentro de `dados`, o token do login — e o log do servidor:

> [tool] Bash: python3 -c " import json a={r['name']:r for r in json.load(open('.refactor-arch/after.json'))} b={r['name']:r for r in json.load(open('.refactor-arch/baseline.j

Tudo idêntico ao baseline exceto as mudanças intencionais; sem tracebacks. Agora o re-scan e a confirmação do comando documentado `python app.py`:

> [tool] Bash: kill 12945 2>/dev/null; sleep 1; rm -f loja.db python3 .claude/skills/refactor-arch/scripts/scan_antipatterns.py . 2>&1 | grep -v "^\.venv" 

De 84 para 11 hits. Revisando cada um: 9 são falsos positivos (decorator `@somente_admin` na linha seguinte, placeholders `?` interpolados, DTO de entrada, default de dev prescrito). Dois merecem ação real:

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/middlewares/error_handler.py

> [tool] Edit: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/src/models/pedido_model.py

Re-validando com o comando documentado `python app.py` (porta via env, sem editar código):

> [tool] Bash: .venv/bin/python -m compileall -q src app.py && echo "COMPILE OK" rm -f loja.db SECRET_KEY=smoke-secret ADMIN_TOKEN=smoke-admin-token PORT=5201 .venv/bin/python

> [tool] Bash: for i in $(seq 1 15); do curl -s -o /dev/null http://127.0.0.1:5201/ && break; done; cat /tmp/claude-501/after2.log; echo "--- smoke ---" python3 .claude/skills

> [tool] Bash: python3 .claude/skills/refactor-arch/scripts/endpoint_smoke.py .refactor-arch/endpoints.json http://127.0.0.1:5201 --compare .refactor-arch/baseline.json --out 

O `SMOKE_EXIT=1` é da **segunda** execução contra o mesmo servidor — o `/admin/reset-db` do final da primeira corrida esvaziou o banco. O protocolo exige banco limpo por corrida. Refazendo corretamente:

> [tool] Bash: kill 13189 2>/dev/null; sleep 1; rm -f loja.db SECRET_KEY=smoke-secret ADMIN_TOKEN=smoke-admin-token PORT=5201 .venv/bin/python app.py > /tmp/claude-501/final.l

> [tool] Bash: rm -f loja.db; find . -name "__pycache__" -type d -not -path "./.venv/*" -exec rm -rf {} + 2>/dev/null; rm -f /tmp/claude-501/*.log echo "--- árvore final ---";

Limpeza completa, processos encerrados, porta liberada.

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
code-smells-project/
├── app.py                              ENTRY POINT    — create_app() + run (preserva `python app.py`)
├── .env.example                        CONFIG         — todas as variáveis, sem valores reais
├── requirements.txt                    (inalterado — nenhuma dependência nova)
├── README.md                           documenta run command, env vars e camadas
└── src/
    ├── app.py                          COMPOSITION ROOT — único lugar que liga dependências concretas
    ├── errors.py                        AppError → ValidationError/Unauthorized/Forbidden/NotFound/Conflict
    ├── database.py                      INFRA          — conexão por request (flask.g), schema com FKs, seed
    ├── config/
    │   ├── settings.py                 CONFIG         — tudo de os.environ, debug off por padrão
    │   └── constants.py                CONFIG         — categorias, status, faixas de desconto, limites
    ├── models/                         MODEL          — só SQL parametrizado, mapeamento e transações
    │   ├── produto_model.py
    │   ├── usuario_model.py            allow-list de campos: o hash nunca sai daqui
    │   └── pedido_model.py             transação única + baixa atômica de estoque + JOIN sem N+1
    ├── controllers/                    CONTROLLER     — casos de uso, regras, erros de domínio
    │   ├── validators.py               validação única por agregado (criar e atualizar)
    │   ├── produto_controller.py
    │   ├── usuario_controller.py
    │   ├── pedido_controller.py
    │   ├── relatorio_controller.py     política de desconto mora aqui, não na persistência
    │   ├── sistema_controller.py
    │   └── admin_controller.py
    ├── views/                          VIEW           — Blueprints finos: parse + serialização, zero SQL
    │   ├── produto_routes.py
    │   ├── usuario_routes.py
    │   ├── pedido_routes.py
    │   ├── relatorio_routes.py
    │   ├── sistema_routes.py
    │   └── admin_routes.py             rotas atrás do guard de admin
    ├── middlewares/
    │   ├── auth.py                     MIDDLEWARE     — X-Admin-Token ou Bearer de usuário admin
    │   └── error_handler.py            MIDDLEWARE     — único ponto que mapeia erro → HTTP
    └── services/                       INFRA
        ├── password_service.py         Werkzeug (já vem com Flask)
        ├── token_service.py            itsdangerous (já vem com Flask)
        └── notificacao_service.py      e-mail/SMS/push atrás de interface injetável

Removidos: controllers.py (292 ln), models.py (314 ln), database.py (86 ln) — god modules substituídos.

## Findings Resolution
F-01 [CRITICAL] Chave secreta hardcoded — FIXED: `src/config/settings.py` lê tudo de `os.environ`; default dev `dev-only-change-me` com warning no boot; chave removida do `/health`.
F-02 [CRITICAL] Endpoints admin sem autenticação — FIXED: `src/middlewares/auth.py` exige `X-Admin-Token` (ou Bearer de admin); `/admin/query` aceita apenas um `SELECT` somente-leitura; sem token configurado nega tudo (fail-closed).
F-03 [CRITICAL] God module controllers.py — FIXED: dividido em 6 controllers por agregado + 6 blueprints; arquivo apagado.
F-04 [CRITICAL] Exposição de dados sensíveis — FIXED: allow-list `CAMPOS_PUBLICOS` em `usuario_model.py` (sem `senha`); `/health` devolve só status/database/counts/versao; erros inesperados viram mensagem genérica com stack só no log.
F-05 [CRITICAL] SQL Injection em 20 consultas — FIXED: 100% das consultas parametrizadas com `?`; a busca dinâmica acumula `condicoes`/`params` em listas paralelas.
F-06 [CRITICAL] God module models.py — FIXED: dividido em 3 models por agregado; a política de desconto migrou para `relatorio_controller.py`; arquivo apagado.
F-07 [CRITICAL] Senhas em texto puro — FIXED: `PasswordService` com `generate_password_hash`/`check_password_hash`; seed hasheado pelo mesmo serviço; login busca por email e compara o hash em código.
F-08 [HIGH] Config de runtime insegura — FIXED: `FLASK_DEBUG` default `0`, `HOST` default `127.0.0.1`, CORS limitado a `CORS_ORIGINS`.
F-09 [HIGH] Sem app factory nem DI — FIXED: `create_app()` em `src/app.py` como composition root; models/controllers recebem dependências por construtor; blueprints no lugar dos 16 `add_url_rule`.
F-10 [HIGH] Regra de negócio nas rotas — FIXED: views só fazem parse/serialização; regras nos controllers; notificações no `NotificacaoService`; `/health` consulta via models.
F-11 [HIGH] Login sem credencial verificável — FIXED: `TokenService` emite token assinado (itsdangerous) em `dados.token`; o guard admin aceita esse Bearer para usuários `admin`.
F-12 [HIGH] Estado global mutável — FIXED: `Database` com conexão por requisição em `flask.g` + `teardown_appcontext`; sem `global`, sem `check_same_thread=False`.
F-13 [HIGH] Sem transação nem integridade — FIXED: `criar_com_itens` roda em `transacao()` com rollback; baixa atômica `WHERE estoque >= ?` com checagem de `rowcount`; schema declara FOREIGN KEY + `PRAGMA foreign_keys = ON`.
F-14 [MEDIUM] Erro espalhado em 17 handlers — FIXED: zero `try/except` nos handlers; `register_error_handlers` mapeia `AppError`/`HTTPException`/`Exception`.
F-15 [MEDIUM] Validação ausente/inconsistente — FIXED: `validators.py` checa tipo e faixa; `preco: "abc"` agora é 400 (era 500); corpo ausente tratado; email validado e único; status de pedido inexistente vira 404.
F-16 [MEDIUM] Validação duplicada criar/atualizar — FIXED: `validar_produto()` única, usada pelos dois casos de uso.
F-17 [MEDIUM] N+1 queries — FIXED: listagem de pedidos em 2 consultas (pedidos + um `LEFT JOIN` com `IN`); relatório em 2 consultas com `GROUP BY` (eram 5 `COUNT`); criação de pedido carrega o catálogo em 1 consulta e insere itens com `executemany`.
F-18 [MEDIUM] Mapeamento e carga duplicados — FIXED: um `_to_dict` por model; `listar(usuario_id=None)` substitui as duas funções quase idênticas.
F-19 [LOW] print como log — FIXED: 19 `print` → `logging` configurado no factory; e-mails não vão mais para stdout.
F-20 [LOW] Números e strings mágicos — FIXED: `src/config/constants.py` com categorias, status, limites de nome e `FAIXAS_DESCONTO`.
F-21 [LOW] Shadowing de `id`, cursor2/cursor3 — FIXED: `produto_id`/`usuario_id`/`pedido_id`; cursores numerados eliminados junto com os laços aninhados.
F-22 [LOW] Imports não utilizados — FIXED: `os` e `sqlite3` órfãos removidos com os arquivos antigos.
F-23 [LOW] Filtro de preço com teste truthy — FIXED: `_preco_filtro` distingue `None` de `0`; valor não numérico vira 400 em vez de 500.

Nenhum finding diferido.

## Intentional Behaviour Changes
Segurança (fecham findings da Fase 2):
- `POST /login`: email com `' --` deixa de autenticar — 401 em vez de 200 (F-05, F-07).
- `GET /usuarios`, `GET /usuarios/<id>`: campo `senha` removido da resposta (F-04).
- `GET /health`: removidos `secret_key`, `db_path`, `debug` e `ambiente` (F-04).
- `POST /admin/reset-db` e `POST /admin/query`: exigem credencial admin — 403 sem ela (F-02).
- `POST /admin/query`: aceita apenas um `SELECT` somente-leitura — 400 para outras instruções (F-02).
- Erros inesperados devolvem `"Erro interno do servidor"` em vez de `str(e)` (F-04, F-14).
- CORS restrito a `CORS_ORIGINS` em vez de qualquer origem (F-08).

Correção e integridade:
- `POST /produtos` com `preco`/`estoque` não numérico: 400 em vez de 500 (F-15).
- `POST /usuarios` com email já cadastrado: 409 em vez de criar conta duplicada (F-15).
- `PUT /pedidos/<id>/status` de pedido inexistente: 404 em vez de 200 silencioso (F-15).
- `DELETE /produtos/<id>` de produto vinculado a pedido: 409 em vez de deixar itens órfãos (F-13).
- `POST /pedidos` com `usuario_id` inexistente: 400 em vez de 201 (F-13).
- `PUT /produtos/<id>` aplica as mesmas regras de nome e categoria do POST (F-16).
- Respostas de erro ganham `"sucesso": false` onde faltava — adição compatível, nenhuma chave removida (F-14).
- `token` adicionado dentro de `dados` no login — adição compatível (F-11).

## Validation
  ✓ Application boots without errors (`SECRET_KEY=… ADMIN_TOKEN=… PORT=5201 python app.py`; processo vivo, 0 tracebacks no log, `GET /` → 200; `python -m compileall -q src app.py` OK)
  ✓ All endpoints respond correctly (49/49 smoke requests, exit code 0 — 41 idênticas ao baseline + 8 defeitos que o baseline registrava e agora respondem o status correto)
  ✓ No catalog anti-patterns remaining (scanner: 9 hits, all reviewed — todos falsos positivos: `@somente_admin` na linha seguinte às 2 rotas admin; `?` placeholders interpolados em cláusula `IN`; DTO de entrada da validação, não serializador de resposta; default de dev prescrito pelo guia; `database.py` 168 ln e `validators.py` 160 ln têm responsabilidade única)
================================
```

Três observações sobre a validação, para você conferir:

- O baseline (`.refactor-arch/baseline.json`, 49 requisições) foi capturado **duas vezes** contra o código original intacto — a segunda após eu acrescentar os 3 casos de integridade que pretendia corrigir, para que cada mudança ficasse medida e não assumida.
- Os únicos diffs de chave reportados pelo script são os listados em *Intentional Behaviour Changes*; verifiquei à parte o que a comparação de chaves de topo não alcança (`senha` dentro de `dados`, token no login) comparando os corpos diretamente.
- Uma execução intermediária do smoke deu exit 1 porque rodei duas vezes contra o mesmo servidor — o `/admin/reset-db` do final da primeira corrida esvazia o banco. A corrida válida final, com banco limpo, deu 49/49 e exit 0.

`requirements.txt` não mudou: `werkzeug` e `itsdangerous` já acompanham o Flask.

<!-- session_id=324f454e-e1ae-498e-abf1-8606685d08ed turns=60 cost_usd=7.133373000000001 -->
