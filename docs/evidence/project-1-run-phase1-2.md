I'll start Phase 1.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/references/project-analysis.md

> [tool] Bash: ls -la && git rev-parse --show-toplevel

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/app.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/controllers.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/models.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/database.py

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/README.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/requirements.txt

> [tool] Bash: wc -l app.py controllers.py models.py database.py && python3 --version && .venv/bin/python -c "import flask, flask_cors; print('flask', flask.__version__)" 2>/d

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      Python 3.13.0 (venv local .venv)
Framework:     Flask 3.1.1 (flask-cors 5.0.1)
Dependencies:  flask==3.1.1, flask-cors==5.0.1
Domain:        API de e-commerce / loja virtual — produtos, usuários (clientes e admin), pedidos com itens e relatório de vendas
Architecture:  MONOLITH — sem pastas de camadas; app.py mistura config, rotas e SQL cru; models.py mistura persistência e regras de negócio; controllers.py mistura validação, regras e notificações
Source files:  4 files analyzed (~780 lines)
Entry point:   app.py (pip install -r requirements.txt && python app.py — porta 5000, debug=True)
DB:            SQLite (sqlite3 raw, arquivo loja.db, conexão global) — tables: produtos, usuarios, pedidos, itens_pedido
Endpoints:     19 routes (app.py — 16 via add_url_rule apontando para controllers.py, 3 declaradas inline em app.py)
================================
```

Detalhe do inventário de rotas (vira a spec de smoke-test na Fase 3):

| # | Rota | Handler |
|---|---|---|
| 1 | `GET /` | `app.py:33` |
| 2 | `GET /produtos` | `controllers.py:5` |
| 3 | `GET /produtos/busca` | `controllers.py:111` |
| 4 | `GET /produtos/<int:id>` | `controllers.py:14` |
| 5 | `POST /produtos` | `controllers.py:24` |
| 6 | `PUT /produtos/<int:id>` | `controllers.py:64` |
| 7 | `DELETE /produtos/<int:id>` | `controllers.py:98` |
| 8 | `GET /usuarios` | `controllers.py:128` |
| 9 | `GET /usuarios/<int:id>` | `controllers.py:136` |
| 10 | `POST /usuarios` | `controllers.py:146` |
| 11 | `POST /login` | `controllers.py:167` |
| 12 | `POST /pedidos` | `controllers.py:188` |
| 13 | `GET /pedidos` | `controllers.py:229` |
| 14 | `GET /pedidos/usuario/<int:usuario_id>` | `controllers.py:222` |
| 15 | `PUT /pedidos/<int:pedido_id>/status` | `controllers.py:237` |
| 16 | `GET /relatorios/vendas` | `controllers.py:257` |
| 17 | `GET /health` | `controllers.py:264` |
| 18 | `POST /admin/reset-db` | `app.py:48` |
| 19 | `POST /admin/query` | `app.py:60` |

Agora a Fase 2.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/references/anti-patterns-catalog.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/references/report-template.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/references/mvc-guidelines.md

> [tool] Bash: python3 /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/code-smells-project/.claude/skills/refactor-arch/scripts/scan_antipatterns.py .

Li os 4 arquivos por completo e conferi cada hit do scanner. Montando o relatório.

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/reports/audit-project-1.md

================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3.13 + Flask 3.1.1 (flask-cors 5.0.1), SQLite via driver `sqlite3`
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 7 | HIGH: 6 | MEDIUM: 5 | LOW: 5

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | Chave secreta hardcoded e duplicada | `app.py:7`; `controllers.py:289` |
| F-02 | CRITICAL | Endpoints administrativos/destrutivos sem autenticação | `app.py:47-57, 59-78` |
| F-03 | CRITICAL | God module: `controllers.py` concentra todos os domínios | `controllers.py:1-292` |
| F-04 | CRITICAL | Exposição de dados sensíveis (senhas, secret key, stack de erro) | `controllers.py:276-290`; `models.py:83, 99` |
| F-05 | CRITICAL | SQL Injection em 20 consultas | `models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291-297` |
| F-06 | CRITICAL | God module: `models.py` mistura persistência, regra de negócio e relatório | `models.py:1-314` |
| F-07 | CRITICAL | Senhas armazenadas e comparadas em texto puro | `models.py:105-131`; `database.py:75-83` |
| F-08 | HIGH | Configuração de runtime insegura (debug, bind-all, CORS aberto) | `app.py:7-9, 88` |
| F-09 | HIGH | Acoplamento forte: sem app factory nem injeção de dependência | `app.py:6-30`; `controllers.py:2-3`; `models.py:1` |
| F-10 | HIGH | Regra de negócio e persistência na camada de rota/controller | `app.py:48-78`; `controllers.py:24-62, 188-255` |
| F-11 | HIGH | Login sem emissão de credencial verificável | `controllers.py:167-186` |
| F-12 | HIGH | Estado global mutável na conexão de banco | `database.py:4-11` |
| F-13 | HIGH | Escrita multi-tabela sem transação e sem integridade referencial | `models.py:133-169`; `database.py:14-53` |
| F-14 | MEDIUM | Tratamento de erro espalhado e duplicado em 17 handlers | `controllers.py:10-12, …, 291-292`; `app.py:77-78` |
| F-15 | MEDIUM | Validação de entrada ausente ou inconsistente | `controllers.py:24-96, 146-165, 188-216, 237-243` |
| F-16 | MEDIUM | Validação duplicada entre criar e atualizar produto | `controllers.py:28-54, 72-90` |
| F-17 | MEDIUM | N+1 queries na listagem de pedidos e no relatório | `models.py:139-166, 177-199, 209-231, 239-254` |
| F-18 | MEDIUM | Mapeamento linha→dict e carga de pedidos duplicados | `models.py:12-21, 31-40, 304-313, 79-86, 95-102, 171-201, 203-233` |
| F-19 | LOW | `print` usado como log operacional (19 ocorrências) | `app.py:56, 83-86`; `controllers.py:8, 11, 57, …, 250` |
| F-20 | LOW | Números e strings mágicos de regra de negócio | `controllers.py:47, 49, 52, 242`; `models.py:256-262` |
| F-21 | LOW | Nomenclatura ruim: shadowing de `id`, `cursor2`/`cursor3` | `controllers.py:14, 56, 64, 98`; `models.py:24, 54, 65, 89, 187, 191, 219, 223` |
| F-22 | LOW | Imports não utilizados | `database.py:2`; `models.py:2` |
| F-23 | LOW | Condicional truthy descarta filtro de preço igual a zero | `models.py:294, 296` |

## Findings

### F-01 [CRITICAL] Chave secreta hardcoded e duplicada (AP-01)
File: app.py:7; controllers.py:289
Evidence: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
Description: A `SECRET_KEY` está literal no código-fonte (versionada) e aparece copiada no payload do `/health`. Não há leitura de variável de ambiente em nenhum ponto — o mesmo vale para `db_path = "loja.db"` (`database.py:5`) e a porta `5000` (`app.py:88`).
Impact: Qualquer pessoa com acesso ao repositório ou ao `/health` (público) obtém a chave de assinatura de sessões e pode forjá-las.
Recommendation: `config/settings.py` lendo `os.environ` com defaults de dev explicitamente não-produtivos; remover a chave do `/health` (PB-01).

### F-02 [CRITICAL] Endpoints administrativos/destrutivos sem autenticação (AP-05)
File: app.py:47-57, 59-78
Evidence: `cursor.execute(query)` — com `query = dados.get("sql", "")` vindo do corpo da requisição
Description: `POST /admin/reset-db` apaga as quatro tabelas e `POST /admin/query` executa SQL arbitrário do cliente. Nenhum tem auth ou verificação de papel. Pelo mesmo motivo `DELETE /produtos/<id>`, `GET /pedidos` e `GET /relatorios/vendas` também são públicos.
Impact: Destruição total de dados e leitura/escrita irrestrita do banco por qualquer cliente HTTP.
Recommendation: `middlewares/auth.py` com guard de admin nas rotas sensíveis e **remoção** do endpoint de SQL arbitrário (PB-05).

### F-03 [CRITICAL] God module: `controllers.py` concentra todos os domínios (AP-03)
File: controllers.py:1-292
Evidence: `from flask import request, jsonify` + `import models` + `from database import get_db`
Description: 292 linhas importando `request`, a camada de modelos e a conexão direta, acumulando ROUTING, BUSINESS, PRESENTATION e PERSISTENCE (`cursor.execute` em `health_check`, linhas 266-274) para três agregados distintos mais relatório e health.
Impact: Mudança em produtos toca o mesmo arquivo de usuários e pedidos; nenhuma regra é testável sem contexto HTTP.
Recommendation: Dividir por agregado em `controllers/` com rotas migrando para blueprints em `views/` (PB-03).

### F-04 [CRITICAL] Exposição de dados sensíveis (AP-06)
File: controllers.py:276-290, 12 (e demais `str(e)`); models.py:83, 99
Evidence: `"db_path": "loja.db", "debug": True, "secret_key": "minha-chave-super-secreta-123"`
Description: Três vazamentos: (1) `/health` devolve secret key, caminho do banco e flag de debug; (2) `get_todos_usuarios` e `get_usuario_por_id` incluem `senha` no dicionário, que `GET /usuarios` serializa — senhas de todos os usuários públicas; (3) todos os `except` devolvem `str(e)`, expondo o schema do SQLite.
Impact: Comprometimento total de credenciais e da chave de assinatura sem explorar nenhuma outra falha.
Recommendation: Serializar usuários sem `senha`, reduzir o `/health` a status/contadores, 500 genérico com stack só no log (PB-06). **Mudança de comportamento intencional** a registrar na Fase 3.

### F-05 [CRITICAL] SQL Injection em 20 consultas (AP-02)
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291-297
Evidence: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
Description: Nenhuma query de `models.py` usa placeholders. O pior caso é `login_usuario`: o email `admin@loja.com' --` autentica como admin sem senha. `buscar_produtos` monta o `WHERE` a partir de `request.args`. Os únicos parâmetros corretos do projeto estão no seed (`database.py:70-83`).
Impact: Bypass de autenticação, leitura de toda a base, alteração e destruição de dados a partir de endpoints públicos.
Recommendation: Reescrever cada query com placeholders `?` e tupla de parâmetros separada, inclusive a busca dinâmica (PB-02).

### F-06 [CRITICAL] God module: `models.py` mistura persistência, regra de negócio e relatório (AP-03)
File: models.py:1-314
Evidence: `if faturamento > 10000: desconto = faturamento * 0.1` dentro do módulo de acesso a dados
Description: 314 linhas com CRUD de quatro tabelas, o fluxo completo de pedido com baixa de estoque (133-169), a política de descontos e o ticket médio (235-273) — a camada de persistência decidindo regra de negócio — mais o mapeamento linha→dict.
Impact: Impossível testar a regra de desconto sem banco; política comercial escondida dentro de um arquivo de SQL.
Recommendation: Separar em `models/produto_model.py`, `usuario_model.py`, `pedido_model.py`, movendo regra para `controllers/` (PB-03).

### F-07 [CRITICAL] Senhas armazenadas e comparadas em texto puro (AP-04)
File: models.py:105-131; database.py:75-83
Evidence: `"INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" + nome + "', '" + email + "', '" + senha + "', ...`
Description: `criar_usuario` grava a senha sem hash, o seed faz o mesmo com `admin123`/`123456`/`senha123`, e `login_usuario` autentica comparando a senha dentro do `WHERE` do SQL.
Impact: Um dump do `loja.db` — ou um simples `GET /usuarios` (F-04) — entrega todas as senhas em claro.
Recommendation: `werkzeug.security.generate_password_hash`/`check_password_hash` (Werkzeug já vem com Flask, sem pacote novo) (PB-04).

### F-08 [HIGH] Configuração de runtime insegura (AP-10)
File: app.py:7-9, 88
Evidence: `app.run(host="0.0.0.0", port=5000, debug=True)`
Description: Debug ligado em dois lugares junto de `host="0.0.0.0"`, publicando o console do Werkzeug em todas as interfaces. `CORS(app)` libera qualquer origem. Host, porta e caminho do banco são literais sem override.
Impact: Debugger do Werkzeug exposto = execução remota de código. CORS irrestrito permite chamadas de qualquer site no navegador da vítima.
Recommendation: `DEBUG`/`HOST`/`PORT`/`CORS_ORIGINS` via `os.environ`, com `DEBUG` default **off** (PB-01).

### F-09 [HIGH] Acoplamento forte: sem app factory nem injeção de dependência (AP-09)
File: app.py:6-30; controllers.py:2-3; models.py:1
Evidence: `app = Flask(__name__)` em tempo de import, seguido de 16 `app.add_url_rule(...)`
Description: Sem `create_app()`; todas as camadas importam `get_db` diretamente; rotas registradas por 16 chamadas manuais em vez de blueprints.
Impact: Impossível instanciar a app com config de teste ou banco em memória; nenhum dublê de conexão.
Recommendation: `src/app.py` com `create_app()` como composition root e blueprints por agregado (PB-08).

### F-10 [HIGH] Regra de negócio e persistência na camada de rota/controller (AP-07)
File: app.py:48-78; controllers.py:24-62, 64-96, 188-220, 237-255, 264-292
Evidence: `print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + ...)`
Description: As rotas inline de `app.py` executam SQL cru. `criar_produto` tem 39 linhas de regra, `criar_pedido` dispara notificações (208-210), `atualizar_status_pedido` decide notificação por transição (247-250) e `health_check` abre cursor e roda quatro queries.
Impact: Regras só exercitáveis via HTTP; lógica de notificação colada ao handler; arquivo de rotas conhece o schema.
Recommendation: Rotas finas em `views/`, regras em `controllers/`, infraestrutura em `services/` (PB-07).

### F-11 [HIGH] Login sem emissão de credencial verificável (AP-12)
File: controllers.py:167-186
Evidence: `return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200`
Description: O `POST /login` valida credenciais e devolve dados do usuário — sem token, sessão ou cookie assinado. Como nenhum outro endpoint verifica identidade, o login é decorativo.
Impact: Não existe autenticação efetiva; não há como atribuir um pedido ou ação admin a um usuário.
Recommendation: Token assinado com `itsdangerous` (já dependência do Flask), validado pelo middleware de auth (PB-10). Adição compatível: a resposta mantém `dados`/`sucesso`.

### F-12 [HIGH] Estado global mutável na conexão de banco (AP-08)
File: database.py:4-11
Evidence: `global db_connection` / `sqlite3.connect(db_path, check_same_thread=False)`
Description: Conexão única em variável de módulo, compartilhada por todas as requisições com a proteção de thread do driver desligada. Schema e seed acontecem como efeito colateral da primeira chamada.
Impact: Requisições simultâneas compartilham cursor e transação implícita, podendo intercalar `commit`s e corromper a baixa de estoque.
Recommendation: Conexão por requisição via `flask.g` + `teardown_appcontext`, com `init_db()`/`seed()` chamados pelo `create_app()` (PB-08).

### F-13 [HIGH] Escrita multi-tabela sem transação e sem integridade referencial (AP-11)
File: models.py:133-169, 65-70; database.py:14-53
Evidence: `"UPDATE produtos SET estoque = estoque - " + str(item["quantidade"]) + " WHERE id = " + ...`
Description: `criar_pedido` insere pedido, N itens e debita estoque com um único `commit` e **sem `rollback`**. A verificação de estoque é feita antes do laço de escrita (check-then-act): duas requisições simultâneas aprovam a mesma unidade. Nenhuma tabela declara `FOREIGN KEY`, então `deletar_produto` deixa `itens_pedido` órfãos — é o que produz o `"Desconhecido"` em `models.py:196`.
Impact: Pedidos parcialmente gravados, estoque negativo sob concorrência, histórico irrecuperável.
Recommendation: `with db:` + rollback, `UPDATE ... WHERE id = ? AND estoque >= ?` com checagem de `rowcount`, e `FOREIGN KEY` no schema (PB-09).

### F-14 [MEDIUM] Tratamento de erro espalhado e duplicado em 17 handlers (AP-15)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292; app.py:77-78
Evidence: `except Exception as e: return jsonify({"erro": str(e)}), 500`
Description: O mesmo bloco em todos os 17 handlers, sem nenhum `@app.errorhandler`. Erros de domínio ora viram `return ... 404` espalhado, ora um dicionário `{"erro": ...}` inspecionado com `if "erro" in resultado` (`controllers.py:205`), misturando canal de erro e de dados.
Impact: `TypeError` de validação vira 500 em vez de 400; mudar o formato de erro exige editar 17 lugares.
Recommendation: Hierarquia `AppError` em `errors.py` e um `middlewares/error_handler.py` único (PB-13).

### F-15 [MEDIUM] Validação de entrada ausente ou inconsistente (AP-14)
File: controllers.py:24-96, 146-165, 188-216, 237-243
Evidence: `if preco < 0:` — sem verificar que `preco` é numérico
Description: `{"preco": "abc"}` levanta `TypeError` → 500 em vez de 400; `login` e `atualizar_status_pedido` chamam `dados.get(...)` sem checar `None` de corpo vazio; `criar_pedido` acessa `item["produto_id"]` sem validar a estrutura; `criar_usuario` não valida email nem unicidade (sem `UNIQUE` na coluna); `atualizar_status_pedido` não verifica se o pedido existe e retorna sucesso para IDs inexistentes.
Impact: Entradas inválidas viram 500; emails duplicados quebram o login; updates silenciosos mascaram bugs do cliente.
Recommendation: Validações por agregado checando presença, tipo e faixa, levantando `ValidationError` (PB-12).

### F-16 [MEDIUM] Validação duplicada entre criar e atualizar produto (AP-16)
File: controllers.py:28-54, 72-90
Evidence: `if "nome" not in dados: return jsonify({"erro": "Nome é obrigatório"}), 400` (linhas 30-31 e 74-75)
Description: Blocos repetidos com regras **divergentes**: o `criar` valida comprimento do nome (47-50) e categorias (52-54); o `atualizar` não valida nenhum dos dois.
Impact: Um `PUT` grava produto com nome de 1 caractere ou categoria inexistente — estado que o `POST` recusa.
Recommendation: Extrair `validar_produto(dados)` usada pelos dois casos de uso (PB-14).

### F-17 [MEDIUM] N+1 queries na listagem de pedidos e no relatório (AP-13)
File: models.py:139-166, 177-199, 209-231, 239-254
Evidence: `cursor3.execute("SELECT nome FROM produtos WHERE id = " + ...)` em laço aninhado
Description: `GET /pedidos` com 100 pedidos de 3 itens dispara 1 + 100 + 300 = 401 consultas. Em `criar_pedido` o `SELECT` do produto é refeito no segundo laço (155) embora já lido no primeiro (140). `relatorio_vendas` roda cinco agregações separadas onde um `GROUP BY status` resolveria.
Impact: Latência linear no volume de pedidos num endpoint que (F-02) é público e sem paginação.
Recommendation: `JOIN` único com `pedido_id IN (...)`; relatório consolidado em uma consulta com `GROUP BY` (PB-11).

### F-18 [MEDIUM] Mapeamento linha→dict e carga de pedidos duplicados (AP-16)
File: models.py:12-21, 31-40, 304-313; 79-86, 95-102; 171-201, 203-233
Evidence: o bloco de 8 chaves de produto aparece idêntico três vezes
Description: Mapeamento de `produtos` copiado em três funções, de `usuarios` em duas, e `get_pedidos_usuario`/`get_todos_pedidos` são 30 linhas idênticas diferindo só pelo `WHERE usuario_id`.
Impact: Adicionar coluna exige editar três funções; foi assim que `senha` ficou em dois serializadores (F-04).
Recommendation: Uma função de serialização por entidade e uma única carga de pedidos com filtro opcional (PB-14).

### F-19 [LOW] `print` usado como log operacional (AP-22)
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Evidence: `print("ENVIANDO SMS: Seu pedido foi recebido!")`
Description: 19 `print` sem níveis, timestamp ou destino configurável. Parte simula infraestrutura inexistente; outras imprimem o email de quem faz login (161, 179, 182).
Impact: Sem níveis não há como silenciar ruído nem elevar erros; emails em stdout são PII em log não estruturado.
Recommendation: `logging` configurado no app factory e `services/notificacao_service.py` explícito (PB-19).

### F-20 [LOW] Números e strings mágicos de regra de negócio (AP-19)
File: controllers.py:47, 49, 52, 242; models.py:256-262
Evidence: `if faturamento > 10000: desconto = faturamento * 0.1`
Description: Faixas de desconto e percentuais inline; limites de nome (`2`, `200`), lista de categorias e lista de status como literais duplicados entre `controllers.py:52`, `controllers.py:242` e o schema.
Impact: Mudar a política comercial exige caçar literais; a lista de status pode divergir do default do schema.
Recommendation: `CATEGORIAS_VALIDAS`, `STATUS_VALIDOS`, `FAIXAS_DESCONTO` em um módulo de constantes (PB-17).

### F-21 [LOW] Nomenclatura ruim: shadowing de `id`, `cursor2`/`cursor3` (AP-20)
File: controllers.py:14, 56, 64, 98; models.py:24, 54, 65, 89, 187, 191, 219, 223
Evidence: `def get_produto_por_id(id):` / `cursor3 = db.cursor()`
Description: Oito funções sombreiam o built-in `id`; cursores auxiliares numerados em vez de nomeados. Nota: `id` é só nome interno — o contrato (`"id"` no JSON, `<int:id>` na URL) não muda.
Impact: Leitura prejudicada e risco de bug se o `id()` built-in for necessário no escopo.
Recommendation: `produto_id`/`usuario_id` e `cursor_itens`/`cursor_produto` (PB-18).

### F-22 [LOW] Imports não utilizados (AP-21)
File: database.py:2; models.py:2
Evidence: `import os` (database.py:2) e `import sqlite3` (models.py:2)
Description: Nenhum dos dois nomes é referenciado nos respectivos arquivos (confirmado por busca).
Impact: Ruído; o `os` em `database.py` sugere falsamente que o caminho do banco vem do ambiente.
Recommendation: Remover durante a reorganização (PB-18).

### F-23 [LOW] Condicional truthy descarta filtro de preço igual a zero (AP-23)
File: models.py:294, 296
Evidence: `if preco_min:` / `if preco_max:`
Description: Teste de verdade em vez de `is not None`: `?preco_max=0` é tratado como "sem filtro" e devolve o catálogo inteiro. Mesmo padrão em `controllers.py:118-121`.
Impact: Resultado silenciosamente errado para entrada legítima.
Recommendation: Comparar explicitamente com `None` (PB-18).

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| — | — | Nenhuma API depreciada detectada para Python 3.13 + Flask 3.1.1. Sem `datetime.utcnow()`, `@app.before_first_request`, `flask.json.JSONEncoder`, `app.json_encoder` ou SQLAlchemy legado; timestamps vêm do `CURRENT_TIMESTAMP` do SQLite (`database.py:23, 33, 42`), sem adaptadores de data depreciados em 3.12. |

## Architecture Notes
- **Current architecture:** MONOLITH — quatro arquivos planos sem pastas de camada; `app.py` acumula config, registro de rotas e SQL cru; `controllers.py` mistura parse HTTP, regra de negócio, notificação e consulta direta; `models.py` mistura persistência, serialização e política comercial; todas as camadas importam a mesma conexão global.
- **Proposed target:** reestruturação completa para o layout MVC de referência Flask, com `app.py` na raiz preservando `python app.py` e o código em `src/`: `src/app.py` (`create_app()` como composition root), `src/config/settings.py` (configuração via `os.environ`), `src/database.py` (conexão por requisição + `init_db`/`seed`, sem global mutável), `src/models/` (um módulo por agregado, só SQL parametrizado, transações e mapeamento), `src/controllers/` (casos de uso, validação de regra, política de desconto, erros de domínio), `src/views/` (blueprints finos com parse e serialização), `src/middlewares/` (`error_handler.py` e `auth.py`), `src/services/` (hash de senha, token, notificações) e `src/errors.py` (hierarquia `AppError`).

================================
Total: 23 findings
================================

Report saved to /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/reports/audit-project-1.md

```text
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

<!-- session_id=324f454e-e1ae-498e-abf1-8606685d08ed turns=15 cost_usd=1.5062460000000002 -->
