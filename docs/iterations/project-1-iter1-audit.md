================================
ARCHITECTURE AUDIT REPORT
================================
Project: code-smells-project
Stack:   Python 3.13 + Flask 3.1.1 (flask-cors 5.0.1), SQLite via driver `sqlite3` cru
Files:   4 analyzed | ~780 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 7 | HIGH: 6 | MEDIUM: 4 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | Hardcoded secret key | `app.py:7`; `controllers.py:289` |
| F-02 | CRITICAL | Endpoints administrativos sem autenticação (SQL arbitrário e wipe do banco) | `app.py:47-57, 59-78` |
| F-03 | CRITICAL | God modules (rotas + regra + persistência) | `controllers.py:1-292`; `models.py:1-314`; `app.py:47-78` |
| F-04 | CRITICAL | `/health` expõe secret key, flags e caminho do banco | `controllers.py:264-292` |
| F-05 | CRITICAL | Senhas em texto puro (armazenamento e login) | `database.py:75-83`; `models.py:105-120, 122-131` |
| F-06 | CRITICAL | SQL Injection em 24 consultas | `models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 289-297` |
| F-07 | CRITICAL | Campo `senha` devolvido nas respostas de usuários | `models.py:79-86, 95-102` |
| F-08 | HIGH | Acoplamento forte, sem app factory nem injeção de dependência | `app.py:1-9, 11-30`; `controllers.py:2-3`; `models.py:1` |
| F-09 | HIGH | Configuração de runtime insegura (debug, bind-all, CORS aberto) | `app.py:8, 9, 88`; `database.py:5` |
| F-10 | HIGH | Regra de negócio e efeitos colaterais dentro dos controllers | `controllers.py:43-54, 87-90, 207-210, 242-250, 264-274` |
| F-11 | HIGH | Login não emite credencial verificável; nenhuma rota é protegida | `controllers.py:167-186`; `app.py:11-30` |
| F-12 | HIGH | Conexão global mutável compartilhada entre threads | `database.py:4-11` |
| F-13 | HIGH | Escrita multi-etapa sem transação explícita e sem integridade referencial | `models.py:133-169`; `database.py:14-53`; `app.py:49-55` |
| F-14 | MEDIUM | Tratamento de erro espalhado e exceção crua devolvida ao cliente | `app.py:77-78`; `controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292` |
| F-15 | MEDIUM | Validação ausente/inconsistente de entrada | `controllers.py:43-50, 66, 87-90, 118-121, 146-165, 169-171, 237-245` |
| F-16 | MEDIUM | Lógica duplicada (validação, mapeamento row→dict, carga de pedidos) | `controllers.py:24-58, 64-96`; `models.py:10-21, 30-40, 302-313, 171-201, 203-233` |
| F-17 | MEDIUM | N+1 queries e contagens repetidas | `models.py:139-166, 177-200, 209-232, 239-254` |
| F-18 | LOW | `print` usado como log | `app.py:56, 83-86`; `controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250` |
| F-19 | LOW | Nomes ruins (`id` sombreando builtin, `cursor2/cursor3`, nomes duplicados entre camadas) | `controllers.py:14, 56, 64, 98`; `models.py:24, 43, 54, 65, 89, 187, 191, 219, 223` |
| F-20 | LOW | Magic numbers / magic strings | `controllers.py:47-54, 242`; `models.py:256-262` |
| F-21 | LOW | Imports não utilizados | `database.py:2`; `models.py:2` |

## Findings

### F-01 [CRITICAL] Hardcoded secret key (AP-01)
File: app.py:7; controllers.py:289
Evidence: `app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"`
Description: A chave de assinatura da aplicação está escrita no código-fonte e versionada no Git, e a mesma string literal aparece novamente dentro do handler `/health`. Não há leitura de variável de ambiente nem valor distinto por ambiente.
Impact: Quem tiver acesso ao repositório (ou ao endpoint `/health`, ver F-04) pode forjar sessões/cookies assinados. Rotacionar a chave exige alterar código e redeploy.
Recommendation: Mover a chave para variável de ambiente lida por um objeto de configuração (`Config.SECRET_KEY = os.environ["SECRET_KEY"]`), falhando o boot se ausente em produção, e remover o literal de ambos os pontos (PB-01).

### F-02 [CRITICAL] Endpoints administrativos sem autenticação (AP-05)
File: app.py:47-57, 59-78
Evidence: `cursor.execute(query)` — `query = dados.get("sql", "")` vindo direto do corpo da requisição em `POST /admin/query`
Description: `POST /admin/query` executa SQL arbitrário enviado pelo cliente (SELECT, DROP, UPDATE — qualquer coisa) e devolve o resultado; `POST /admin/reset-db` apaga as quatro tabelas. Nenhum dos dois tem decorator de autenticação, verificação de papel, token ou restrição de rede. Combinado com CORS liberado (F-09), qualquer página web pode dispará-los.
Impact: Comprometimento total do banco por requisição anônima: leitura de todos os usuários e senhas, alteração de preços/pedidos, destruição de dados. É a falha mais grave do projeto.
Recommendation: Remover `POST /admin/query` por completo (não há uso legítimo em uma API) e proteger `POST /admin/reset-db` com autenticação + papel `admin`, mantendo-o apenas fora de produção (PB-05).

### F-03 [CRITICAL] God modules — rotas, regra de negócio e persistência no mesmo arquivo (AP-03)
File: controllers.py:1-292; models.py:1-314; app.py:47-78
Evidence: `from flask import request, jsonify` + `from database import get_db` no mesmo módulo (`controllers.py:1-3`)
Description: `controllers.py` (292 linhas) concentra parsing de request, validação, regra de negócio, notificações simuladas, SQL cru (`health_check`, linhas 266-274) e serialização das três entidades. `models.py` (314 linhas) concentra SQL de produtos, usuários, pedidos e itens, mais a regra de desconto do relatório e a montagem dos dicionários de resposta. `app.py` acumula rotas, configuração e SQL cru nas rotas admin. Nenhum módulo tem responsabilidade única; não existem camadas de serviço, repositório ou schema.
Impact: Impossível testar regra de negócio sem subir Flask e um banco; qualquer mudança de persistência toca o mesmo arquivo que a apresentação; alto risco de regressão e conflito de merge.
Recommendation: Quebrar em camadas por entidade — `routes/` (blueprints), `services/` (regra), `repositories/` (SQL), `schemas/` (validação/serialização), `config.py` — conforme PB-03.

### F-04 [CRITICAL] `/health` expõe secret key, flags e caminho do banco (AP-06)
File: controllers.py:264-292 (especialmente 285-289)
Evidence: `"debug": True, "secret_key": "minha-chave-super-secreta-123"`
Description: O endpoint público `GET /health` devolve a secret key da aplicação, o flag de debug, o caminho do arquivo de banco (`loja.db`), o ambiente ("producao") e contagens internas — tudo sem autenticação. O campo `ambiente` ainda mente sobre a configuração real (debug ligado).
Impact: Vazamento direto do segredo de assinatura e de informação de infraestrutura útil para um atacante encadear com F-02 e F-09.
Recommendation: Reduzir `/health` a um liveness check (`{"status": "ok", "database": "connected"}` + contagens, se necessárias) e nunca serializar configuração (PB-06).

### F-05 [CRITICAL] Senhas armazenadas e comparadas em texto puro (AP-04)
File: database.py:75-83; models.py:105-120, 122-131
Evidence: `"SELECT * FROM usuarios WHERE email = '" + email + "' AND senha = '" + senha + "'"`
Description: `criar_usuario` grava a senha recebida sem qualquer hash (`models.py:126-129`), o seed insere senhas literais (`"admin123"`, `"123456"`, `"senha123"`) e o login compara a senha em texto puro dentro da própria cláusula SQL. Não há salt, hash nem comparação em tempo constante.
Impact: Um dump do `loja.db` (ou um `SELECT` via F-02) entrega todas as credenciais em claro, com reutilização provável em outros serviços dos usuários.
Recommendation: Hashear com `werkzeug.security.generate_password_hash` / `check_password_hash` (já disponível via Flask, sem nova dependência), buscar o usuário por e-mail e verificar o hash em Python (PB-04).

### F-06 [CRITICAL] SQL Injection em 24 consultas (AP-02)
File: models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155, 158-160, 164-165, 174, 188, 192, 220, 224, 280, 289-297
Evidence: `query += " AND (nome LIKE '%" + termo + "%' OR descricao LIKE '%" + termo + "%')"`
Description: Praticamente todo o acesso a dados monta SQL por concatenação de strings com valores vindos da requisição. Os vetores mais diretos são `GET /produtos/busca` (`q`, `categoria`), `POST /login` (`email`, `senha`), `POST /produtos` e `POST /usuarios` (campos texto). Nenhuma query usa placeholders `?` — exceto os `executemany` do seed em `database.py:70-83`.
Impact: Bypass de autenticação (`email = admin@loja.com' --`), leitura e escrita arbitrária de qualquer tabela, destruição de dados. Além disso, um nome de produto com aspas simples quebra o INSERT e gera erro 500.
Recommendation: Converter 100% das queries para placeholders `?` com tupla de parâmetros, construindo filtros dinâmicos como lista de cláusulas + lista de parâmetros (PB-02).

### F-07 [CRITICAL] Campo `senha` devolvido nas respostas de usuários (AP-06)
File: models.py:79-86, 95-102
Evidence: `"senha": row["senha"],`
Description: `get_todos_usuarios` e `get_usuario_por_id` montam o dicionário de resposta incluindo a senha, devolvida por `GET /usuarios` e `GET /usuarios/<id>` — rotas sem autenticação. Como as senhas são texto puro (F-05), o vazamento é da credencial real, não de um hash.
Impact: Qualquer pessoa com acesso à API obtém a lista completa de e-mails e senhas, incluindo o usuário `admin`.
Recommendation: Definir um serializer explícito de usuário sem o campo de senha (allow-list de campos) e nunca usar `SELECT *` como base da resposta (PB-06). Mudança de contrato intencional a registrar na Phase 3.

### F-08 [HIGH] Acoplamento forte, sem app factory nem injeção de dependência (AP-09)
File: app.py:1-9, 11-30; controllers.py:2-3; models.py:1
Evidence: `from database import get_db` repetido em `controllers.py:3` e `models.py:1`
Description: O objeto `app` é criado em tempo de import (`app.py:6`), os handlers importam `models` concretamente e tanto controllers quanto models chamam `get_db()` diretamente. Não existe `create_app()`, nem registro de blueprints, nem forma de injetar uma conexão/repositório alternativo.
Impact: Impossível instanciar a aplicação com configuração de teste ou banco em memória; qualquer teste unitário arrasta o módulo de banco real. Importar `controllers` já amarra o módulo ao SQLite.
Recommendation: Introduzir app factory `create_app(config)` registrando blueprints, com a conexão obtida por `flask.g`/teardown e repositórios recebendo a conexão como parâmetro (PB-08).

### F-09 [HIGH] Configuração de runtime insegura (AP-10)
File: app.py:8, 9, 88; database.py:5
Evidence: `app.run(host="0.0.0.0", port=5000, debug=True)`
Description: Debug ligado em dois pontos (`app.config["DEBUG"] = True` e `debug=True` no `run`), escuta em todas as interfaces, `CORS(app)` sem restrição de origem (`app.py:9`) e caminho do banco/porta fixos no código, sem override por ambiente (`database.py:5`, `app.py:88`).
Impact: O debugger do Werkzeug exposto em `0.0.0.0` permite execução remota de código via console interativo; CORS totalmente aberto deixa qualquer site chamar os endpoints administrativos de F-02 a partir do navegador da vítima.
Recommendation: Centralizar em `config.py` com valores por ambiente (`FLASK_DEBUG`, `HOST`, `PORT`, `DATABASE_PATH`, origens de CORS), com debug desligado por padrão (PB-01).

### F-10 [HIGH] Regra de negócio e efeitos colaterais dentro dos controllers (AP-07)
File: controllers.py:43-54, 87-90, 207-210, 242-250, 264-274
Evidence: `print("ENVIANDO EMAIL: Pedido " + str(resultado["pedido_id"]) + " criado para usuario " + str(usuario_id))`
Description: `criar_produto` carrega as regras de preço/estoque/tamanho de nome e a lista de categorias válidas (43-54); `criar_pedido` dispara três notificações simuladas após persistir (207-210); `atualizar_status_pedido` decide a máquina de estados e as notificações por status (242-250); `health_check` abre cursor e executa SQL direto (264-274). O handler deixou de ser apenas adaptação HTTP.
Impact: A regra de negócio não é reutilizável fora do ciclo request/response nem testável sem cliente HTTP; efeitos colaterais acontecem mesmo quando a transação de pedido falhou parcialmente (ver F-13).
Recommendation: Extrair `ProdutoService`, `PedidoService` e um `NotificationService` injetável; o controller passa a validar o payload, chamar o serviço e formatar a resposta (PB-07).

### F-11 [HIGH] Login não emite credencial verificável e nenhuma rota é protegida (AP-12)
File: controllers.py:167-186; app.py:11-30
Evidence: `return jsonify({"dados": usuario, "sucesso": True, "mensagem": "Login OK"}), 200`
Description: `POST /login` apenas devolve os dados do usuário: não cria sessão, não emite token, não grava nada. Consequentemente, nenhuma rota consegue (nem tenta) verificar identidade — `GET /usuarios`, `DELETE /produtos/<id>`, `PUT /pedidos/<id>/status`, `GET /relatorios/vendas` e as rotas admin são todas anônimas. `GET /pedidos/usuario/<id>` também não valida propriedade do recurso.
Impact: O login é decorativo; qualquer cliente executa operações destrutivas e lê dados de qualquer usuário. O campo `tipo: "admin"` existe no modelo mas nunca é consultado.
Recommendation: Emitir um token assinado (`itsdangerous`, já dependência transitiva do Flask) ou sessão do Flask, e aplicar decorators `@login_required` / `@admin_required` nas rotas sensíveis (PB-10).

### F-12 [HIGH] Conexão global mutável compartilhada entre threads (AP-08)
File: database.py:4-11
Evidence: `global db_connection` / `sqlite3.connect(db_path, check_same_thread=False)`
Description: Uma única conexão SQLite é guardada em variável global de módulo, criada na primeira chamada e reutilizada por todas as requisições, com a proteção de thread do driver explicitamente desativada. Cursores são abertos sobre essa conexão compartilhada em todas as camadas.
Impact: Condições de corrida entre requisições concorrentes; uma transação deixada aberta por um handler (F-13) é commitada ou abortada por outro; o estado global impede isolamento entre testes.
Recommendation: Conexão por requisição via `flask.g` com `teardown_appcontext` fechando ao final, encapsulada em um módulo de infraestrutura sem estado global (PB-08).

### F-13 [HIGH] Escrita multi-etapa sem transação explícita e sem integridade referencial (AP-11)
File: models.py:133-169; database.py:14-53; app.py:49-55
Evidence: `cursor.execute("UPDATE produtos SET estoque = estoque - " + str(item["quantidade"]) + " WHERE id = " + str(item["produto_id"]))`
Description: `criar_pedido` valida estoque em um laço, insere o pedido, insere cada item e decrementa estoque, commitando só no fim — sem `try/except` com `rollback()`. Se qualquer passo falhar, a transação fica aberta na conexão global (F-12) e pode ser commitada pela próxima requisição. A verificação de estoque (139-146) e o decremento (163-166) são check-then-act, sujeitos a corrida: dois pedidos simultâneos podem zerar o estoque abaixo de zero. O schema (`database.py:14-53`) não declara nenhuma `FOREIGN KEY`, então `deletar_produto` e `POST /admin/reset-db` deixam `itens_pedido` apontando para produtos inexistentes.
Impact: Pedidos parcialmente gravados, estoque negativo, itens órfãos e relatórios financeiros incorretos.
Recommendation: Envolver a operação em transação explícita com `rollback()` em erro, tornar o decremento atômico (`UPDATE ... SET estoque = estoque - ? WHERE id = ? AND estoque >= ?` verificando `rowcount`) e declarar `FOREIGN KEY` com `PRAGMA foreign_keys = ON` (PB-09).

### F-14 [MEDIUM] Tratamento de erro espalhado e exceção crua devolvida ao cliente (AP-15)
File: app.py:77-78; controllers.py:10-12, 21-22, 60-62, 95-96, 108-109, 125-126, 133-134, 143-144, 164-165, 185-186, 218-220, 226-227, 234-235, 254-255, 261-262, 291-292
Evidence: `except Exception as e: return jsonify({"erro": str(e)}), 500`
Description: Os 17 handlers repetem o mesmo `try/except Exception` genérico e devolvem a mensagem crua da exceção. Não existe `@app.errorhandler`, não há distinção entre erro de validação (400) e falha inesperada (500), e erros de SQL chegam ao cliente com nomes de tabelas e colunas.
Impact: Vazamento de detalhes internos, ruído de código (quase 20% do arquivo é boilerplate de erro) e mascaramento de bugs — tudo vira 500 com texto imprevisível.
Recommendation: Hierarquia de exceções de domínio (`ValidationError`, `NotFoundError`, `ConflictError`) + handlers centralizados `@app.errorhandler` devolvendo payload padronizado e logando o stack trace do lado do servidor (PB-13).

### F-15 [MEDIUM] Validação ausente ou inconsistente de entrada (AP-14)
File: controllers.py:43-50, 66, 87-90, 118-121, 146-165, 169-171, 237-245
Evidence: `if preco < 0:` — sem checagem de tipo; `preco: "abc"` levanta `TypeError` → 500
Description: Os campos são usados sem validação de tipo: `preco`/`estoque` como string quebram as comparações; `request.get_json()` pode ser `None` em `atualizar_produto` (66), `login` (169) e `atualizar_status_pedido` (239), produzindo `AttributeError`. `atualizar_produto` omite as validações de tamanho de nome e de categoria que `criar_produto` aplica (43-54 vs 87-90). `criar_usuario` não valida formato de e-mail, força de senha nem duplicidade. `buscar_produtos` converte `preco_min`/`preco_max` com `float()` sem tratar `ValueError`, e usa `if preco_min:` — um filtro `preco_min=0` é silenciosamente ignorado. `atualizar_status_pedido` valida o status mas não verifica se o pedido existe (retorna 200 para IDs inexistentes).
Impact: Respostas 500 em entradas inválidas de cliente, dados inconsistentes gravados e comportamento diferente entre criar e atualizar o mesmo recurso.
Recommendation: Camada de schemas por entidade, compartilhada entre create/update, validando presença, tipo e faixa antes de chegar ao serviço, e traduzindo falhas em 400 (PB-12).

### F-16 [MEDIUM] Lógica duplicada (AP-16)
File: controllers.py:24-58, 64-96; models.py:10-21, 30-40, 302-313, 171-201, 203-233
Evidence: bloco `{"id": row["id"], "nome": row["nome"], ... "criado_em": row["criado_em"]}` repetido em 3 funções de produto
Description: Três blocos idênticos de mapeamento row→dict de produto (`models.py:12-21, 31-40, 304-313`) e dois de usuário (`79-86, 95-102`); `get_pedidos_usuario` (171-201) e `get_todos_pedidos` (203-233) são o mesmo laço aninhado diferindo apenas no `WHERE`; o bloco de validação de `criar_produto` (28-54) reaparece em `atualizar_produto` (72-90) já divergente (ver F-15).
Impact: Toda mudança de campo exige editar de 2 a 3 lugares; as cópias já divergiram, o que é a origem do F-15.
Recommendation: Um serializer por entidade e uma única função de listagem de pedidos parametrizada pelo filtro; validação compartilhada por schema (PB-14).

### F-17 [MEDIUM] N+1 queries e contagens repetidas (AP-13)
File: models.py:139-166, 177-200, 209-232, 239-254
Evidence: `cursor3.execute("SELECT nome FROM produtos WHERE id = " + str(item["produto_id"]))` dentro de laço aninhado
Description: `get_pedidos_usuario` e `get_todos_pedidos` fazem 1 query por pedido para os itens e mais 1 query por item para o nome do produto — `GET /pedidos` é uma listagem sem paginação, então o custo cresce sem limite. `criar_pedido` consulta o mesmo produto duas vezes (139-146 e 155) e executa 3 queries por item. `relatorio_vendas` dispara 5 consultas de agregação separadas (239-254) que cabem em um único `GROUP BY`.
Impact: Latência crescente com o volume de pedidos e carga desnecessária no banco; `GET /pedidos` degrada linearmente com o total de itens do sistema.
Recommendation: Substituir os laços por `JOIN` (pedidos + itens + produtos) com agrupamento em memória, reaproveitar o produto já carregado em `criar_pedido` e consolidar o relatório em uma agregação única (PB-11).

### F-18 [LOW] `print` usado como log (AP-22)
File: app.py:56, 83-86; controllers.py:8, 11, 57, 61, 106, 161, 179, 182, 208-210, 219, 248, 250
Evidence: `print("Login bem-sucedido: " + email)`
Description: 18 chamadas de `print` fazem papel de log operacional, sem níveis, timestamp, correlação de requisição ou destino configurável. Parte delas registra e-mail de usuário em claro (`controllers.py:161, 179, 182`) e outras simulam efeitos colaterais de negócio (208-210, 248-250, tratados em F-10).
Impact: Impossível ajustar verbosidade por ambiente ou enviar logs para um coletor; dados pessoais vão para stdout sem controle.
Recommendation: Usar `logging` com logger por módulo e níveis (`info`/`warning`/`error`), configurado na app factory (PB-19).

### F-19 [LOW] Nomes ruins (AP-20)
File: controllers.py:14, 56, 64, 98; models.py:24, 43, 54, 65, 89, 187, 191, 219, 223
Evidence: `def buscar_produto(id):` / `cursor2 = db.cursor()` / `cursor3 = db.cursor()`
Description: O parâmetro `id` sombreia o builtin em 8 funções; `cursor2`/`cursor3` numeram em vez de descrever (`cursor_itens`, `cursor_produto`); funções de camadas diferentes têm nomes idênticos (`controllers.criar_produto` vs `models.criar_produto`, `controllers.buscar_produtos` vs `models.buscar_produtos`), o que torna ambíguo qualquer stack trace ou busca no código.
Impact: Leitura e depuração mais lentas; risco de import errado entre camadas.
Recommendation: Renomear para `produto_id`/`usuario_id`, nomear cursores pelo propósito e diferenciar as camadas (`ProdutoService.criar` vs `ProdutoRepository.inserir`) — a reestruturação da Phase 3 já resolve a colisão (PB-18).

### F-20 [LOW] Magic numbers / magic strings (AP-19)
File: controllers.py:47-54, 242; models.py:256-262
Evidence: `if faturamento > 10000: desconto = faturamento * 0.1`
Description: As faixas de desconto do relatório (10000/0.1, 5000/0.05, 1000/0.02) estão inline na função de persistência; os limites de nome (2 e 200) e a lista de categorias válidas estão inline no controller; a lista de status válidos (`"pendente"`, `"aprovado"`, ...) é repetida como literal em `controllers.py:242` e espalhada em strings SQL (`models.py:150, 247, 250, 253`).
Impact: Regra de negócio invisível para quem lê a camada errada; mudar uma faixa ou adicionar um status exige caçar literais em vários arquivos.
Recommendation: Constantes/`Enum` nomeadas em um módulo de domínio (`FAIXAS_DESCONTO`, `CATEGORIAS_VALIDAS`, `StatusPedido`, `NOME_MIN`/`NOME_MAX`) usadas por todas as camadas (PB-17).

### F-21 [LOW] Imports não utilizados (AP-21)
File: database.py:2; models.py:2
Evidence: `import sqlite3` em `models.py` — o símbolo não é referenciado em nenhuma das 314 linhas
Description: `models.py:2` importa `sqlite3` sem usá-lo e `database.py:2` importa `os` sem usá-lo (verificado por busca em ambos os arquivos).
Impact: Ruído e sinal falso de que `models.py` fala diretamente com o driver.
Recommendation: Remover os dois imports; o `os` passa a ser realmente necessário no novo `config.py` para ler variáveis de ambiente (PB-18).

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| — | — | — |

Nenhuma API depreciada foi detectada para Python 3.13 + Flask 3.1.1. Verificações feitas explicitamente: `datetime.utcnow()` não é usado (os timestamps vêm de `CURRENT_TIMESTAMP` do SQLite, `database.py:23, 33, 42`); `@app.before_first_request`, `flask.json.JSONEncoder` e `app.json_encoder` (removidos no Flask 2.3) não aparecem; `app.add_url_rule` (`app.py:11-30`) é API corrente, não depreciada; os adaptadores de data do `sqlite3` depreciados em Python 3.12 não são usados. Observação não-depreciativa: `app.run()` em `app.py:88` é servidor de desenvolvimento e não deve ser usado em produção (ver F-09).

## Architecture Notes
- Current architecture: MONOLITH — não existem pastas de camada; a divisão `controllers.py` / `models.py` é apenas nominal: `app.py` mistura rotas, configuração e SQL cru, `controllers.py` mistura HTTP, validação, regra e notificação, `models.py` mistura SQL, regra de desconto e serialização.
- Proposed target: MVC em camadas com app factory — `app.py` (entry point) → `create_app()` registrando blueprints; `config.py` (configuração por ambiente, sem segredos no código); `routes/` (produtos, usuarios, pedidos, relatorios, health, admin) apenas adaptando HTTP; `services/` com a regra de negócio e transações; `repositories/` com todo o SQL parametrizado; `schemas/` para validação de entrada e serialização de saída (sem `senha`); `infra/` para conexão por requisição, logging e notificações; tratamento de erro centralizado por `@app.errorhandler`. Comandos de execução (`pip install -r requirements.txt && python app.py`, porta 5000) e o contrato de todos os 19 endpoints preservados.

================================
Total: 21 findings
================================
