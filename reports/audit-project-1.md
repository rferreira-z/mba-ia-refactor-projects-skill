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
| F-14 | MEDIUM | Tratamento de erro espalhado e duplicado em 17 handlers | `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292`; `app.py:77-78` |
| F-15 | MEDIUM | Validação de entrada ausente ou inconsistente | `controllers.py:24-96, 146-165, 188-216, 237-243` |
| F-16 | MEDIUM | Validação duplicada entre criar e atualizar produto | `controllers.py:28-54, 72-90` |
| F-17 | MEDIUM | N+1 queries na listagem de pedidos e no relatório | `models.py:139-166, 177-199, 209-231, 239-254` |
| F-18 | MEDIUM | Mapeamento linha→dict e carga de pedidos duplicados | `models.py:12-21, 31-40, 304-313, 79-86, 95-102, 171-201, 203-233` |
| F-19 | LOW | `print` usado como log operacional (19 ocorrências) | `app.py:56, 83-86`; `controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250` |
| F-20 | LOW | Números e strings mágicos de regra de negócio | `controllers.py:47, 49, 52, 242`; `models.py:256-262` |
| F-21 | LOW | Nomenclatura ruim: shadowing de `id`, `cursor2`/`cursor3` | `controllers.py:14, 56, 64, 98`; `models.py:24, 54, 65, 89, 187, 191, 219, 223` |
| F-22 | LOW | Imports não utilizados | `database.py:2`; `models.py:2` |
| F-23 | LOW | Condicional truthy descarta filtro de preço igual a zero | `models.py:294, 296` |

## Findings

### F-01 [CRITICAL] Chave secreta hardcoded e duplicada (AP-01)
File: app.py:7; controllers.py:289
Evidence: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
Description: A `SECRET_KEY` da aplicação está escrita literalmente no código-fonte (versionada no Git) e ainda aparece uma segunda vez, copiada, dentro do payload do `/health` em `controllers.py:289`. Não há leitura de variável de ambiente em nenhum ponto do projeto — o mesmo vale para `db_path = "loja.db"` (`database.py:5`) e a porta `5000` (`app.py:88`).
Impact: Qualquer pessoa com acesso ao repositório (ou ao endpoint `/health`, que é público) obtém a chave usada para assinar sessões e cookies, podendo forjá-los. Rotacionar a chave exige alterar código e redeploy.
Recommendation: Mover toda configuração para `config/settings.py` lendo `os.environ` com defaults de desenvolvimento obviamente não-produtivos (`"dev-only-change-me"`), e remover a chave do corpo do `/health` (PB-01).

### F-02 [CRITICAL] Endpoints administrativos/destrutivos sem autenticação (AP-05)
File: app.py:47-57, 59-78
Evidence: `cursor.execute(query)` — com `query = dados.get("sql", "")` vindo direto do corpo da requisição
Description: `POST /admin/reset-db` apaga as quatro tabelas do banco e `POST /admin/query` executa SQL arbitrário enviado pelo cliente (SELECT, DROP, UPDATE — qualquer comando). Nenhum dos dois tem decorator de autenticação, verificação de papel (`tipo = 'admin'`) ou token. Pelo mesmo motivo, `DELETE /produtos/<id>`, `GET /pedidos` (todos os pedidos de todos os clientes) e `GET /relatorios/vendas` (faturamento) também são públicos.
Impact: Destruição total de dados e leitura/escrita irrestrita do banco por qualquer cliente HTTP, sem autenticação. É a falha mais grave do projeto.
Recommendation: Criar `middlewares/auth.py` com um guard de administrador, protegê-lo nas rotas sensíveis e **remover** o endpoint de SQL arbitrário — ele não tem substituto seguro (PB-05).

### F-03 [CRITICAL] God module: `controllers.py` concentra todos os domínios (AP-03)
File: controllers.py:1-292
Evidence: `from flask import request, jsonify` + `import models` + `from database import get_db`
Description: Um único arquivo de 292 linhas importa simultaneamente o objeto `request` do Flask, a camada de modelos e a conexão direta de banco, e acumula quatro responsabilidades para três agregados distintos (produto, usuário, pedido) mais relatório e health: ROUTING (parse de `request.get_json()`/`request.args`), BUSINESS (validação de faixas de preço, lista de categorias, transições de status), PRESENTATION (`jsonify` em todos os retornos) e PERSISTENCE (`cursor.execute` direto em `health_check`, linhas 266-274).
Impact: Qualquer mudança em produtos obriga a tocar no mesmo arquivo que serve usuários e pedidos; não há como testar uma regra de negócio sem subir o contexto HTTP do Flask; o arquivo é ponto de conflito permanente em merges.
Recommendation: Dividir por agregado em `controllers/produto_controller.py`, `controllers/usuario_controller.py`, `controllers/pedido_controller.py`, `controllers/relatorio_controller.py`, com as rotas migrando para blueprints em `views/` (PB-03).

### F-04 [CRITICAL] Exposição de dados sensíveis (AP-06)
File: controllers.py:276-290, 12 (e demais `str(e)`); models.py:83, 99
Evidence: `"db_path": "loja.db", "debug": True, "secret_key": "minha-chave-super-secreta-123"`
Description: Três vazamentos distintos. (1) `GET /health` devolve publicamente a secret key, o caminho do banco, a flag de debug e o "ambiente" (`controllers.py:285-289`). (2) `get_todos_usuarios` e `get_usuario_por_id` incluem o campo `senha` no dicionário retornado (`models.py:83` e `models.py:99`), que `GET /usuarios` e `GET /usuarios/<id>` serializam diretamente — as senhas de todos os usuários são públicas. (3) Todos os `except` devolvem `str(e)` ao cliente, expondo mensagens internas do SQLite (nomes de tabelas e colunas).
Impact: Comprometimento total de credenciais e da chave de assinatura sem precisar explorar nenhuma outra falha; as mensagens de erro ainda entregam o schema para quem for montar um ataque.
Recommendation: Serializar usuários sem o campo `senha`, reduzir o `/health` a `status`/`database`/contadores, e padronizar erros inesperados em 500 genérico com stack apenas no log servidor (PB-06). **Esta é uma mudança de comportamento intencional** a ser registrada na Fase 3.

### F-05 [CRITICAL] SQL Injection em 20 consultas (AP-02)
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 291-297
Evidence: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
Description: Nenhuma consulta de `models.py` usa placeholders — todas são montadas por concatenação de strings com valores vindos da requisição. O caso mais grave é `login_usuario` (`models.py:109-111`): enviar o email `admin@loja.com' --` autentica como administrador sem senha. `buscar_produtos` (`models.py:289-299`) monta a cláusula `WHERE` incrementalmente a partir de `request.args`, e `criar_produto`/`criar_usuario` injetam o corpo do POST dentro de `INSERT`. Os únicos parâmetros corretos do projeto estão no seed (`database.py:70-83`).
Impact: Bypass de autenticação, leitura de toda a base (inclusive senhas), alteração e destruição de dados a partir de qualquer endpoint público.
Recommendation: Reescrever cada query com placeholders `?` e tupla de parâmetros separada, inclusive a busca dinâmica (acumular `conditions`/`params` em listas paralelas) (PB-02).

### F-06 [CRITICAL] God module: `models.py` mistura persistência, regra de negócio e relatório (AP-03)
File: models.py:1-314
Evidence: `if faturamento > 10000: desconto = faturamento * 0.1` dentro do módulo de acesso a dados
Description: 314 linhas com CRUD de quatro tabelas (produtos, usuarios, pedidos, itens_pedido), o fluxo completo de criação de pedido com baixa de estoque (`models.py:133-169`), a política de descontos por faixa de faturamento e o cálculo de ticket médio (`models.py:235-273`) — ou seja, a camada que deveria apenas persistir decide regra de negócio. O módulo também faz o mapeamento linha→dict (apresentação) em cada função.
Impact: Impossível trocar o mecanismo de persistência ou testar a regra de desconto sem banco; a política comercial fica escondida dentro de um arquivo de SQL.
Recommendation: Separar em `models/produto_model.py`, `models/usuario_model.py`, `models/pedido_model.py` (somente consultas parametrizadas e mapeamento), movendo a regra de desconto e a orquestração do pedido para `controllers/` (PB-03).

### F-07 [CRITICAL] Senhas armazenadas e comparadas em texto puro (AP-04)
File: models.py:105-131; database.py:75-83
Evidence: `"INSERT INTO usuarios (nome, email, senha, tipo) VALUES ('" + nome + "', '" + email + "', '" + senha + "', '" + tipo + "')"`
Description: `criar_usuario` grava a senha recebida sem nenhum hash (`models.py:126-129`), o seed faz o mesmo com `admin123`/`123456`/`senha123` (`database.py:75-83`) e `login_usuario` autentica comparando a senha dentro do `WHERE` do SQL (`models.py:109-111`) em vez de verificar um hash em código.
Impact: Um dump do arquivo `loja.db` — ou um simples `GET /usuarios`, ver F-04 — entrega todas as senhas em claro, que tipicamente são reutilizadas em outros serviços.
Recommendation: Aplicar `werkzeug.security.generate_password_hash` na criação e `check_password_hash` no login (Werkzeug já é dependência transitiva do Flask, sem pacote novo), buscando o usuário por email e comparando o hash em Python (PB-04).

### F-08 [HIGH] Configuração de runtime insegura (AP-10)
File: app.py:7-9, 88
Evidence: `app.run(host="0.0.0.0", port=5000, debug=True)`
Description: Debug ligado em dois lugares (`app.config["DEBUG"] = True` na linha 8 e `debug=True` na linha 88) junto de `host="0.0.0.0"`, o que publica o console interativo do Werkzeug em todas as interfaces de rede. O `CORS(app)` da linha 9 libera qualquer origem sem restrição, e host, porta e caminho do banco são literais sem override por ambiente.
Impact: O debugger do Werkzeug exposto permite execução remota de código no servidor. O CORS irrestrito permite que qualquer site faça chamadas autenticadas à API a partir do navegador da vítima.
Recommendation: Ler `DEBUG`, `HOST`, `PORT` e `CORS_ORIGINS` de `config/settings.py` via `os.environ`, com `DEBUG` default **off** e origens restritas por default (PB-01).

### F-09 [HIGH] Acoplamento forte: sem app factory nem injeção de dependência (AP-09)
File: app.py:6-30; controllers.py:2-3; models.py:1
Evidence: `app = Flask(__name__)` executado em tempo de import, seguido de 16 `app.add_url_rule(...)`
Description: O objeto `app` é criado no import do módulo, não existe `create_app()`, e todas as camadas importam a função concreta `get_db` diretamente (`controllers.py:3`, `models.py:1`), sem ponto único de composição. As rotas são registradas por 16 chamadas manuais de `add_url_rule` em vez de blueprints por domínio.
Impact: Impossível instanciar a aplicação com configuração de teste ou banco em memória; nenhum teste unitário pode substituir a conexão por um dublê; registrar uma rota nova exige editar o arquivo central.
Recommendation: Introduzir `src/app.py` com `create_app()` como composition root, blueprints por agregado registrados ali, e a conexão obtida de uma factory em vez de um singleton global (PB-08).

### F-10 [HIGH] Regra de negócio e persistência na camada de rota/controller (AP-07)
File: app.py:48-78; controllers.py:24-62, 64-96, 188-220, 237-255, 264-292
Evidence: `print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))`
Description: As rotas inline de `app.py` (`/admin/reset-db`, `/admin/query`) executam SQL cru direto no arquivo de rotas. Em `controllers.py`, `criar_produto` tem 39 linhas de regra (faixas de preço/estoque, comprimento de nome, lista de categorias válidas), `criar_pedido` dispara os efeitos colaterais de notificação (email/SMS/push, linhas 208-210), `atualizar_status_pedido` decide notificações por transição de status (linhas 247-250) e `health_check` abre cursor e roda quatro queries (linhas 266-274).
Impact: As regras de negócio só são exercitáveis via HTTP; a lógica de notificação está colada ao handler e não pode ser reaproveitada nem desligada; o arquivo de rotas conhece o schema do banco.
Recommendation: Rotas finas em `views/` apenas fazendo parse/serialização, regras em `controllers/`, efeitos de infraestrutura em `services/notificacao_service.py` e consultas em `models/` (PB-07).

### F-11 [HIGH] Login sem emissão de credencial verificável (AP-12)
File: controllers.py:167-186
Evidence: `return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200`
Description: O `POST /login` valida as credenciais e devolve apenas os dados do usuário — não emite token, sessão ou cookie assinado. Como nenhum outro endpoint verifica identidade (ver F-02), o login é puramente decorativo: o cliente pode simplesmente ignorá-lo e chamar qualquer rota.
Impact: Não existe autenticação efetiva na API; não há como atribuir um pedido ou uma ação administrativa a um usuário.
Recommendation: Emitir um token assinado com a `SECRET_KEY` (`itsdangerous`, já dependência do Flask) no login e validá-lo no middleware de auth usado pelas rotas protegidas (PB-10). Observação: emitir o token é adição compatível com o contrato atual — a resposta mantém `dados`/`sucesso`.

### F-12 [HIGH] Estado global mutável na conexão de banco (AP-08)
File: database.py:4-11
Evidence: `global db_connection` / `db_connection = sqlite3.connect(db_path, check_same_thread=False)`
Description: Uma única conexão SQLite é guardada em variável de módulo, criada sob demanda com `global` e compartilhada por todas as requisições com `check_same_thread=False`, que desliga a proteção do driver contra uso concorrente. A criação do schema e o seed acontecem como efeito colateral dessa primeira chamada (`database.py:14-84`).
Impact: Com o servidor multi-thread (padrão do Flask em produção), duas requisições simultâneas compartilham cursor e transação implícita, podendo intercalar `commit`s e corromper a baixa de estoque de pedidos concorrentes. Também impede usar um banco diferente em testes.
Recommendation: Conexão por requisição via `flask.g` + `teardown_appcontext`, com `init_db()`/`seed()` chamados explicitamente pelo `create_app()` (PB-08).

### F-13 [HIGH] Escrita multi-tabela sem transação e sem integridade referencial (AP-11)
File: models.py:133-169, 65-70; database.py:14-53
Evidence: `cursor.execute("UPDATE produtos SET estoque = estoque - " + str(item["quantidade"]) + " WHERE id = " + str(item["produto_id"]))`
Description: `criar_pedido` insere o pedido, insere N itens e debita o estoque de N produtos, com um único `commit` ao final e **sem `rollback`** em caso de exceção no meio do laço — se o terceiro item falhar, o pedido e os dois primeiros itens permanecem na transação pendente da conexão global e podem ser gravados pelo próximo `commit` de outra requisição. A verificação de estoque (linha 144) é feita antes do laço de escrita, caracterizando check-then-act: duas requisições simultâneas podem aprovar a mesma unidade e deixar o estoque negativo. Nenhuma tabela declara `FOREIGN KEY` (`database.py:36-53`), então `deletar_produto` (`models.py:65-70`) remove um produto deixando `itens_pedido` órfãos — é exatamente o que produz o `"Desconhecido"` em `models.py:196`.
Impact: Pedidos parcialmente gravados, estoque negativo sob concorrência e histórico de pedidos com itens irrecuperáveis.
Recommendation: Envolver o fluxo em `with db:` (transação) com `rollback` em erro, usar `UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?` verificando `rowcount` para a baixa atômica, e declarar as `FOREIGN KEY` no schema (PB-09).

### F-14 [MEDIUM] Tratamento de erro espalhado e duplicado em 17 handlers (AP-15)
File: controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292; app.py:77-78
Evidence: `except Exception as e: return jsonify({"erro": str(e)}), 500`
Description: O mesmo bloco `try/except Exception` com retorno de `str(e)` e status 500 aparece em todos os 17 handlers, sem nenhum `@app.errorhandler` registrado. Erros de domínio (produto não encontrado, estoque insuficiente) são representados ora por `return ... 404` espalhado pelos controllers, ora por um dicionário `{"erro": ...}` inspecionado com `if "erro" in resultado` (`controllers.py:205`), misturando canal de erro com canal de dados.
Impact: Um `TypeError` de validação vira 500 em vez de 400 (ver F-15); mudar o formato do corpo de erro exige editar 17 lugares; mensagens internas vazam (ver F-04).
Recommendation: Hierarquia `AppError` (`NotFoundError`, `ValidationError`, `ConflictError`) em `errors.py`, levantada pelos controllers, e um `middlewares/error_handler.py` único que mapeia para status e formata o corpo (PB-13).

### F-15 [MEDIUM] Validação de entrada ausente ou inconsistente (AP-14)
File: controllers.py:24-96, 146-165, 188-216, 237-243
Evidence: `if preco < 0:` — sem verificar que `preco` é numérico
Description: Vários furos concretos: `preco`/`estoque` são comparados com `0` sem checagem de tipo, então `{"preco": "abc"}` levanta `TypeError` e retorna 500 em vez de 400 (`controllers.py:43-46`, `87-90`); `atualizar_status_pedido` e `login` chamam `dados.get(...)` sem verificar se `request.get_json()` retornou `None`, gerando 500 em corpo vazio (`controllers.py:170`, `240`); `criar_pedido` acessa `item["produto_id"]`/`item["quantidade"]` sem validar a estrutura de cada item (`models.py:140`, `144`); `criar_usuario` não valida formato de email nem unicidade (não há `UNIQUE` na coluna, `database.py:30`), permitindo cadastros duplicados; `atualizar_status_pedido` não verifica se o pedido existe antes do `UPDATE`, retornando sucesso para IDs inexistentes.
Impact: Entradas inválidas viram erro 500 em vez de 400, emails duplicados quebram o login e atualizações silenciosas mascaram bugs no cliente.
Recommendation: Centralizar as validações em funções de validação por agregado, checando presença, tipo e faixa, e levantando `ValidationError` (PB-12).

### F-16 [MEDIUM] Validação duplicada entre criar e atualizar produto (AP-16)
File: controllers.py:28-54, 72-90
Evidence: `if "nome" not in dados: return jsonify({"erro": "Nome é obrigatório"}), 400` (repetido nas linhas 30-31 e 74-75)
Description: `criar_produto` e `atualizar_produto` repetem o mesmo bloco de validação de campos obrigatórios, preço e estoque — mas com regras divergentes: o `criar` ainda valida comprimento do nome (linhas 47-50) e lista de categorias (linhas 52-54), e o `atualizar` não valida nenhum dos dois.
Impact: Um `PUT` consegue gravar um produto com nome de 1 caractere ou categoria inexistente, estado que o `POST` recusa — a base fica com dados que a aplicação considera inválidos.
Recommendation: Extrair uma única função `validar_produto(dados)` usada pelos dois casos de uso (PB-14).

### F-17 [MEDIUM] N+1 queries na listagem de pedidos e no relatório (AP-13)
File: models.py:139-166, 177-199, 209-231, 239-254
Evidence: `cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))` dentro de um laço aninhado
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem uma query de itens por pedido e mais uma query de nome por item — `GET /pedidos` com 100 pedidos de 3 itens dispara 1 + 100 + 300 = 401 consultas. Em `criar_pedido`, o `SELECT` do produto é refeito dentro do segundo laço (`models.py:155`) embora o mesmo dado já tenha sido lido no primeiro (`models.py:140`). `relatorio_vendas` roda cinco queries de agregação separadas (`models.py:239-254`) onde um `GROUP BY status` com `COUNT`/`SUM` resolveria tudo.
Impact: Latência crescendo linearmente com o volume de pedidos no endpoint de listagem — que, por F-02, é público e sem paginação.
Recommendation: Carregar itens e nomes com um `JOIN` único filtrado por `pedido_id IN (...)` e agrupar em memória; consolidar o relatório em uma consulta com `GROUP BY` (PB-11).

### F-18 [MEDIUM] Mapeamento linha→dict e carga de pedidos duplicados (AP-16)
File: models.py:12-21, 31-40, 304-313; models.py:79-86, 95-102; models.py:171-201, 203-233
Evidence: o bloco de 8 chaves `{"id": ..., "nome": ..., ..., "criado_em": ...}` de produto aparece idêntico três vezes
Description: O mapeamento de linha de `produtos` para dicionário está copiado em `get_todos_produtos`, `get_produto_por_id` e `buscar_produtos`; o de `usuarios` em `get_todos_usuarios` e `get_usuario_por_id`; e `get_pedidos_usuario` e `get_todos_pedidos` são 30 linhas praticamente idênticas, diferindo apenas pelo `WHERE usuario_id`.
Impact: Adicionar uma coluna exige editar três funções e esquecer uma produz respostas inconsistentes entre endpoints — foi exatamente assim que o campo `senha` ficou em dois serializadores de usuário (F-04).
Recommendation: Uma função de serialização por entidade (`_row_to_produto`, `_row_to_usuario`) e uma única função de carga de pedidos com filtro opcional de usuário (PB-14).

### F-19 [LOW] `print` usado como log operacional (AP-22)
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Evidence: `print("ENVIANDO SMS: Seu pedido foi recebido!")`
Description: 19 chamadas de `print` fazem papel de log, sem níveis, timestamp ou destino configurável. Parte delas simula efeitos de infraestrutura que não existem (email/SMS/push em `controllers.py:208-210`, notificações de status em 248 e 250) e outras registram dados de usuário em stdout (`controllers.py:161`, `179`, `182` imprimem o email de quem faz login).
Impact: Sem níveis não há como silenciar ruído nem elevar erros em produção; emails em stdout são PII em log não estruturado.
Recommendation: Substituir por `logging` configurado no app factory, e mover as "notificações" para um `services/notificacao_service.py` explícito (PB-19).

### F-20 [LOW] Números e strings mágicos de regra de negócio (AP-19)
File: controllers.py:47, 49, 52, 242; models.py:256-262
Evidence: `if faturamento > 10000: desconto = faturamento * 0.1`
Description: As faixas de desconto e seus percentuais (`10000`/`0.1`, `5000`/`0.05`, `1000`/`0.02`) estão inline no relatório; os limites de nome (`2` e `200`), a lista de categorias válidas e a lista de status permitidos são literais duplicados entre `controllers.py:52` e `controllers.py:242` e o schema do banco.
Impact: Mudar a política comercial exige caçar literais em dois arquivos; a lista de status no controller pode divergir do default `'pendente'` do schema sem ninguém notar.
Recommendation: Declarar `CATEGORIAS_VALIDAS`, `STATUS_VALIDOS` e `FAIXAS_DESCONTO` como constantes nomeadas em um módulo de constantes do domínio (PB-17).

### F-21 [LOW] Nomenclatura ruim: shadowing de `id`, `cursor2`/`cursor3` (AP-20)
File: controllers.py:14, 56, 64, 98; models.py:24, 54, 65, 89, 187, 191, 219, 223
Evidence: `def get_produto_por_id(id):` / `cursor3 = db.cursor()`
Description: Oito funções usam `id` como nome de parâmetro ou variável local, sombreando o built-in do Python; os cursores auxiliares dos laços aninhados são numerados (`cursor2`, `cursor3`) em vez de nomeados pelo que consultam.
Impact: Leitura prejudicada e risco de bug silencioso se alguém precisar do `id()` built-in no escopo. Nota: `id` aparece apenas como nome interno — o contrato da API (chave `"id"` no JSON e `<int:id>` na URL) não muda.
Recommendation: Renomear para `produto_id`/`usuario_id` e para `cursor_itens`/`cursor_produto` (PB-18).

### F-22 [LOW] Imports não utilizados (AP-21)
File: database.py:2; models.py:2
Evidence: `import os` (database.py:2) e `import sqlite3` (models.py:2)
Description: `database.py` importa `os` sem nenhuma referência no arquivo, e `models.py` importa `sqlite3` embora todo o acesso passe por `get_db()` — confirmei por busca que nenhum dos dois nomes é usado.
Impact: Ruído que sugere dependências inexistentes; no caso do `os` em `database.py`, dá a falsa impressão de que o caminho do banco é lido do ambiente.
Recommendation: Remover ambos durante a reorganização dos módulos (PB-18).

### F-23 [LOW] Condicional truthy descarta filtro de preço igual a zero (AP-23)
File: models.py:294, 296
Evidence: `if preco_min:` / `if preco_max:`
Description: Os filtros usam teste de verdade em vez de comparação com `None`, então `?preco_max=0` é tratado como "sem filtro" — a busca devolve o catálogo inteiro em vez de nada. O mesmo padrão aparece em `controllers.py:118-121`, onde `float()` só é aplicado se o valor for truthy.
Impact: Resultado silenciosamente errado para um valor de entrada legítimo.
Recommendation: Comparar explicitamente com `None` ao decidir se o filtro se aplica (PB-18).

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| — | — | Nenhuma API depreciada detectada para Python 3.13 + Flask 3.1.1. Não há `datetime.utcnow()`, `@app.before_first_request`, `flask.json.JSONEncoder`, `app.json_encoder` nem SQLAlchemy legado no projeto; os timestamps são gerados pelo `CURRENT_TIMESTAMP` do SQLite (`database.py:23, 33, 42`), sem adaptadores `sqlite3` de data depreciados em 3.12. |

## Architecture Notes
- Current architecture: MONOLITH — quatro arquivos planos sem pastas de camada; `app.py` acumula config, registro de rotas e SQL cru; `controllers.py` mistura parse HTTP, regra de negócio, notificação e consulta direta; `models.py` mistura persistência, serialização e política comercial; todas as camadas importam a mesma conexão global.
- Proposed target: reestruturação completa para o layout MVC de referência Flask, com `app.py` na raiz preservando `python app.py` e o código em `src/`: `src/app.py` (`create_app()` como composition root), `src/config/settings.py` (todas as configurações via `os.environ`), `src/database.py` (conexão por requisição + `init_db`/`seed`, sem global mutável), `src/models/` (um módulo por agregado — produto, usuário, pedido — só com SQL parametrizado, transações e mapeamento), `src/controllers/` (casos de uso, validação de regra, política de desconto, levantando erros de domínio), `src/views/` (blueprints finos com parse e serialização, sem SQL), `src/middlewares/` (`error_handler.py` central e `auth.py` para as rotas administrativas), `src/services/` (hash de senha, emissão de token, notificações) e `src/errors.py` (hierarquia `AppError`).

================================
Total: 23 findings
================================
