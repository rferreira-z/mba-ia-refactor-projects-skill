================================
ARCHITECTURE AUDIT REPORT
================================
Project: task-manager-api
Stack:   Python 3.13 + Flask 3.0.0 / Flask-SQLAlchemy 3.1.1
Files:   15 analyzed | ~1158 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 7 | HIGH: 7 | MEDIUM: 5 | LOW: 5

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | Segredos hard-coded (SECRET_KEY e senha SMTP) | `app.py:13`; `services/notification_service.py:7-10` |
| F-02 | CRITICAL | Hash de senha exposto nas respostas da API | `models/user.py:16-25`; `routes/user_routes.py:33,85-86,129,209` |
| F-03 | CRITICAL | Armazenamento inseguro de senha (MD5 sem salt) | `models/user.py:27-32` |
| F-04 | CRITICAL | God module: relatórios + CRUD de categorias + persistência | `routes/report_routes.py:1-223` |
| F-05 | CRITICAL | God module: rotas + regra de negócio + ORM + serialização | `routes/task_routes.py:1-299` |
| F-06 | CRITICAL | God module: rotas + autenticação + ORM + serialização | `routes/user_routes.py:1-211` |
| F-07 | CRITICAL | Endpoints destrutivos e de escrita sem autenticação | `routes/report_routes.py:167-223`; `routes/task_routes.py:85-238`; `routes/user_routes.py:42-151` |
| F-08 | HIGH | Configuração de runtime insegura (debug, 0.0.0.0, CORS aberto) | `app.py:11-16,34` |
| F-09 | HIGH | Sem app factory; acoplamento forte e efeitos no import | `app.py:9-31`; `seed.py:2` |
| F-10 | HIGH | Regra de negócio dentro das rotas (fat routes) | `routes/report_routes.py:13-101,104-155` |
| F-11 | HIGH | Integridade referencial quebrada ao deletar categoria/usuário | `routes/report_routes.py:211-223`; `routes/user_routes.py:140-151` |
| F-12 | HIGH | Regra de negócio dentro das rotas (fat routes) | `routes/task_routes.py:12-63,85-154,156-223,240-299` |
| F-13 | HIGH | Regra de negócio dentro das rotas (fat routes) | `routes/user_routes.py:43-90,92-132,153-183,185-211` |
| F-14 | HIGH | Token de autenticação falso e previsível | `routes/user_routes.py:207-211` |
| F-15 | MEDIUM | APIs depreciadas (`datetime.utcnow`, `Model.query.get`) | `models/category.py:11`; `models/task.py:15-16,52`; `models/user.py:14`; `routes/*`; `seed.py:66-74`; `services/notification_service.py:35`; `utils/helpers.py:38` |
| F-16 | MEDIUM | Lógica duplicada (regra de atraso, serialização, validação) | `models/task.py:23-60`; `routes/task_routes.py:17-39,71-80,96-114,166-184,284-287`; `routes/user_routes.py:162-180`; `routes/report_routes.py:33-37,119-135` |
| F-17 | MEDIUM | N+1 queries e listagens sem paginação | `routes/report_routes.py:53-68,157-165`; `routes/task_routes.py:14-57,281-287`; `routes/user_routes.py:12-25,35-38` |
| F-18 | MEDIUM | Tratamento de erro espalhado e engolido (`except:` nu) | `routes/report_routes.py:186,207,221`; `routes/task_routes.py:62-63,137,204,236`; `routes/user_routes.py:130,149`; `utils/helpers.py:46,49,88` |
| F-19 | MEDIUM | Validação ausente/inconsistente (quebra com tipo errado) | `routes/report_routes.py:196-202`; `routes/task_routes.py:96-114,166-184,260-264`; `routes/user_routes.py:102-103,114-116,191-195` |
| F-20 | LOW | Imports não usados e código morto | `app.py:7`; `models/task.py:3`; `routes/report_routes.py:7-8`; `routes/task_routes.py:7`; `routes/user_routes.py:6`; `services/notification_service.py:1-48`; `utils/helpers.py:3-7,19-116` |
| F-21 | LOW | Magic numbers / magic strings | `models/task.py:11-12,39,47`; `routes/task_routes.py:96-114,177,182`; `routes/user_routes.py:64,71,115,120`; `app.py:34` |
| F-22 | LOW | Lógica booleana verbosa e `type() ==` | `models/task.py:38-60`; `models/user.py:34-38`; `routes/task_routes.py:141,210`; `utils/helpers.py:103` |
| F-23 | LOW | Nomes pobres (variáveis de uma letra) | `routes/report_routes.py:33-68,119-135,161-164`; `routes/task_routes.py:16-59,268-287`; `routes/user_routes.py:14-24,37,141,161-181`; `seed.py:16-91` |
| F-24 | LOW | `print` usado como log | `routes/task_routes.py:149,153,219,234`; `routes/user_routes.py:83,89,147`; `services/notification_service.py:21,24`; `utils/helpers.py:39,41`; `seed.py:93-96` |

## Findings

### F-01 [CRITICAL] Segredos hard-coded no código-fonte (AP-01)
File: app.py:13; services/notification_service.py:7-10
Evidence: `app.config['SECRET_KEY'] = 'super-secret-key-123'` / `self.email_password = 'senha123'`
Description: A chave de sessão do Flask e as credenciais SMTP (host, usuário e senha do `taskmanager@gmail.com`) estão literais no código versionado. Não há leitura de variáveis de ambiente, apesar de `python-dotenv` estar declarado em `requirements.txt` e nunca ser usado.
Impact: Qualquer pessoa com acesso ao repositório pode forjar cookies/sessões assinadas e usar a conta de e-mail. Rotacionar o segredo exige novo deploy de código.
Recommendation: Mover toda configuração para `config/settings.py` lendo `os.environ` com defaults de desenvolvimento obviamente não-produtivos (`dev-only-change-me`); nunca manter segredo literal (PB-01).

### F-02 [CRITICAL] Hash de senha exposto nas respostas da API (AP-06)
File: models/user.py:16-25; routes/user_routes.py:33, 85-86, 129, 209
Evidence: `return {'id': self.id, 'name': self.name, 'email': self.email, 'password': self.password, ...}`
Description: `User.to_dict()` inclui a coluna `password` (o hash). Esse serializer é devolvido em `GET /users/<id>`, `POST /users`, `PUT /users/<id>` e no corpo do `POST /login`, vazando o hash de qualquer usuário para qualquer cliente — sem autenticação (ver F-07).
Impact: Vazamento em massa de credenciais. Combinado com MD5 sem salt (F-03), os hashes são quebráveis offline em segundos via rainbow table.
Recommendation: Remover `password` do serializer; criar uma serialização pública na camada de view que nunca exponha campos sensíveis (PB-06). Mudança intencional de contrato a ser registrada na Fase 3.

### F-03 [CRITICAL] Armazenamento inseguro de senha — MD5 sem salt (AP-04)
File: models/user.py:27-32
Evidence: `self.password = hashlib.md5(pwd.encode()).hexdigest()`
Description: As senhas são hasheadas com MD5, algoritmo rápido, sem salt e criptograficamente quebrado. `check_password` compara hashes em texto, sem comparação de tempo constante. A validação mínima é de 4 caracteres (`routes/user_routes.py:64`), o que agrava o problema.
Impact: Comprometimento do banco = comprometimento de todas as senhas; senhas idênticas produzem hashes idênticos (identificável por inspeção).
Recommendation: Usar `werkzeug.security.generate_password_hash` / `check_password_hash` (já disponível via Flask, sem nova dependência), encapsulados num `services/password_hasher.py` (PB-04).

### F-04 [CRITICAL] God module — relatórios, CRUD de categorias e persistência no mesmo arquivo (AP-03)
File: routes/report_routes.py:1-223
Evidence: `report_bp = Blueprint('reports', __name__)` … `@report_bp.route('/categories', methods=['POST'])` … `db.session.commit()`
Description: O arquivo acumula quatro responsabilidades (ROUTING, BUSINESS, PERSISTENCE, PRESENTATION) sobre três entidades. Pior: metade dele (linhas 157-223) é CRUD de **categorias**, que não tem relação com relatórios e está registrado sob um blueprint chamado `reports`. O relatório de 90 linhas (13-101) monta agregações contando linha a linha em Python.
Impact: Impossível testar as regras de relatório sem subir Flask; mudanças em categorias e em relatórios colidem no mesmo arquivo; o nome do módulo mente sobre o conteúdo.
Recommendation: Separar em `views/category_routes.py` + `views/report_routes.py`, com `controllers/category_controller.py` e `controllers/report_controller.py`, e as consultas agregadas em `models/` (PB-03).

### F-05 [CRITICAL] God module — rotas, regras, ORM e serialização de tasks (AP-03)
File: routes/task_routes.py:1-299
Evidence: `tasks = Task.query.all()` … `if t.due_date < datetime.utcnow():` … `return jsonify(result), 200`
Description: 299 linhas com as quatro tags de responsabilidade e três entidades (`Task`, `User`, `Category`). Importa simultaneamente o objeto `request` do Flask e a sessão do ORM; os handlers montam dicionários campo a campo (17-28), aplicam regra de atraso (30-39), validam entrada (96-114) e persistem (146-154).
Impact: Nenhuma regra de task é reutilizável ou testável isoladamente; qualquer alteração de contrato HTTP arrisca quebrar regra de negócio e vice-versa.
Recommendation: Extrair para `controllers/task_controller.py` (casos de uso) e `models/task.py` (consultas), deixando a view apenas com parse/serialização (PB-03 + PB-07).

### F-06 [CRITICAL] God module — rotas, autenticação, ORM e serialização de usuários (AP-03)
File: routes/user_routes.py:1-211
Evidence: `user = User.query.get(user_id)` … `if not user.check_password(password):` … `'token': 'fake-jwt-token-' + str(user.id)`
Description: 211 linhas misturando CRUD de usuários, listagem de tasks do usuário, login/autenticação, validação de e-mail por regex inline (61, 106) e acesso direto ao ORM. O fluxo de autenticação — a parte mais sensível do sistema — vive no mesmo arquivo que o CRUD.
Impact: Regras de autenticação não auditáveis nem reutilizáveis; o `delete_user` (134-151) apaga tasks em laço dentro da rota, ou seja, decisão de cascata tomada na camada HTTP.
Recommendation: `controllers/user_controller.py` + `controllers/auth_controller.py`, consultas em `models/user.py`, views finas em `routes/` (PB-03).

### F-07 [CRITICAL] Endpoints de escrita e destrutivos totalmente sem autenticação (AP-05)
File: routes/report_routes.py:167-188, 190-209, 211-223; routes/task_routes.py:85-154, 156-223, 225-238; routes/user_routes.py:42-90, 92-132, 134-151
Evidence: `@user_bp.route('/users/<int:user_id>', methods=['DELETE'])` … `tasks = Task.query.filter_by(user_id=user_id).all()` / `for t in tasks: db.session.delete(t)`
Description: Nenhuma rota da API exige autenticação ou autorização — não existe decorator de auth, middleware nem verificação de papel, apesar de `User.role` e `User.is_admin()` existirem no modelo. Qualquer cliente anônimo pode criar usuários **com `role: "admin"`** (`routes/user_routes.py:71-78`), alterar a senha de qualquer usuário (`114-117`), e apagar usuários junto com todas as suas tasks (`134-151`). `/reports/summary` expõe produtividade individual de todos os usuários sem restrição.
Impact: Destruição total de dados e escalada de privilégio por qualquer requisição não autenticada; vazamento de dados pessoais nos relatórios.
Recommendation: Introduzir `middlewares/auth.py` com guarda de token e verificação de papel, aplicada às rotas de escrita/destrutivas e aos relatórios agregados (PB-05), apoiada em tokens reais (F-14).

### F-08 [HIGH] Configuração de runtime insegura (AP-10)
File: app.py:11-16, 34
Evidence: `app.run(debug=True, host='0.0.0.0', port=5000)` / `CORS(app)` / `app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'`
Description: O debugger do Werkzeug é ligado por padrão e a aplicação faz bind em todas as interfaces — o console interativo do debugger permite execução remota de código. `CORS(app)` libera qualquer origem, sobre uma API cujos endpoints de escrita não têm autenticação (F-07). URI do banco, host e porta são literais, sem override por ambiente.
Impact: RCE remota se exposto fora de localhost; qualquer site pode chamar a API a partir do navegador da vítima.
Recommendation: `config/settings.py` lendo `FLASK_DEBUG`, `HOST`, `PORT`, `DATABASE_URL` e `CORS_ORIGINS` do ambiente, com `debug` default **off** e origens restritas (PB-01).

### F-09 [HIGH] Sem app factory: aplicação construída no import, acoplamento forte (AP-09)
File: app.py:9-31; seed.py:2
Evidence: `app = Flask(__name__)` … `with app.app_context(): db.create_all()` / `from app import app, db`
Description: O objeto `app` e a criação do schema (`db.create_all()`, linhas 30-31) acontecem como efeito colateral do import do módulo. Não existe `create_app()`; config, CORS, blueprints e schema estão todos no nível de módulo. `seed.py` importa `app` justamente para herdar esse efeito. Toda camada importa `database.db` diretamente, sem injeção.
Impact: Impossível instanciar a aplicação com configuração de teste (banco em memória) ou importar qualquer módulo sem abrir o banco; o import de `seed.py` já cria `tasks.db`.
Recommendation: Criar `create_app(config=None)` como composition root (registro de blueprints, middlewares, extensões) e manter `app.py` fino chamando a factory, preservando `python app.py` e `python seed.py` (PB-08).

### F-10 [HIGH] Regra de negócio dentro das rotas de relatório (AP-07)
File: routes/report_routes.py:13-101, 104-155
Evidence: `overdue_count = overdue_count + 1` … `'completion_rate': round((completed / total) * 100, 2) if total > 0 else 0`
Description: `summary_report` tem 88 linhas: dispara 14+ consultas, calcula atraso, taxa de conclusão, janelas de 7 dias e produtividade por usuário dentro do handler. `user_report` repete as mesmas contagens em laço manual. Nenhuma dessas regras é acessível fora de uma requisição HTTP — e `utils.helpers.calculate_percentage` (importado na linha 7) existe exatamente para isso e nunca é chamado.
Impact: Regras de métrica não testáveis e não reutilizáveis; divergência garantida entre `/reports/summary`, `/reports/user/<id>` e `/tasks/stats`, que calculam a mesma coisa de três jeitos.
Recommendation: Mover os cálculos para `controllers/report_controller.py` e as agregações para consultas no model; a view só serializa (PB-07).

### F-11 [HIGH] Integridade referencial quebrada ao deletar categoria e usuário (AP-11)
File: routes/report_routes.py:211-223; routes/user_routes.py:134-151
Evidence: `cat = Category.query.get(cat_id)` / `db.session.delete(cat)` / `db.session.commit()`
Description: `DELETE /categories/<id>` apaga a categoria sem tratar as tasks que a referenciam — as linhas de `tasks` ficam com `category_id` apontando para uma categoria inexistente, e `GET /tasks` passa a devolver `category_name: null` sem indicar o problema. As FKs são declaradas em `models/task.py:13-14` mas sem `ondelete`, e o SQLite não aplica FK por padrão. Em `delete_user`, as tasks são removidas em laço na rota (140-142) antes do bloco `try` — a decisão de cascata vive na camada HTTP e não há limite para quantas linhas a operação toca.
Impact: Dados órfãos silenciosos; contagens de relatório divergentes; regra de cascata duplicável/esquecível em novos endpoints.
Recommendation: Declarar a cascata no model (`ondelete`/`cascade` na relationship) e executar a exclusão multi-passo numa única transação dentro do controller, com rollback em falha (PB-09).

### F-12 [HIGH] Regra de negócio dentro das rotas de task (AP-07)
File: routes/task_routes.py:12-63, 85-154, 156-223, 240-299
Evidence: `if t.due_date < datetime.utcnow(): if t.status != 'done' and t.status != 'cancelled': task_data['overdue'] = True`
Description: Os quatro handlers principais têm de 50 a 70 linhas e concentram: regra de atraso (30-39, 71-80, 284-287), validação de título/status/prioridade (96-114, 166-184), verificação de existência de usuário/categoria (116-124, 186-198), parsing de data (134-138, 200-207), conversão de tags (140-144, 209-213), montagem do filtro de busca (247-264) e cálculo de estatísticas (273-299). `Task.is_overdue()` existe em `models/task.py:50-60` e nunca é chamado.
Impact: Handlers longos e não testáveis; cada nova regra aumenta um arquivo já de 299 linhas; comportamento divergente entre criar e atualizar.
Recommendation: `controllers/task_controller.py` com casos de uso (`create_task`, `update_task`, `search_tasks`, `task_stats`), consultas em `models/task.py`, views de ≤ ~15 linhas (PB-07).

### F-13 [HIGH] Regra de negócio dentro das rotas de usuário (AP-07)
File: routes/user_routes.py:43-90, 92-132, 153-183, 185-211
Evidence: `if not re.match(r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$', email):` … `existing = User.query.filter_by(email=email).first()`
Description: Os handlers validam e-mail por regex inline, checam unicidade, validam papéis, aplicam política de senha e executam o fluxo de login (checagem de credencial, conta inativa, emissão de token) direto na rota. `utils.helpers.validate_email` existe e nunca é usado. A regra de atraso aparece de novo em 171-180.
Impact: Política de autenticação não auditável, duplicada entre criar e atualizar com limites diferentes, e impossível de reusar num futuro endpoint de signup/reset.
Recommendation: `controllers/user_controller.py` + `controllers/auth_controller.py`; validação declarada em um único lugar (PB-07 + PB-12).

### F-14 [HIGH] Token de autenticação falso e previsível (AP-12)
File: routes/user_routes.py:207-211
Evidence: `'token': 'fake-jwt-token-' + str(user.id)`
Description: `POST /login` devolve uma string previsível derivada do id do usuário, sem assinatura, expiração ou qualquer verificação possível. Nenhum endpoint valida esse token (F-07), então ele é puramente decorativo — mas comunica ao cliente que existe autenticação.
Impact: Qualquer um forja o "token" de qualquer usuário bastando adivinhar um id; falsa sensação de segurança para quem integra a API.
Recommendation: Emitir um token assinado com a secret de config (`itsdangerous`, já instalado como dependência do Flask) com expiração, e validá-lo no `middlewares/auth.py` (PB-10).

### F-15 [MEDIUM] APIs depreciadas do Python 3.13 e do SQLAlchemy 2.0 (AP-17)
File: models/category.py:11; models/task.py:15-16, 52; models/user.py:14; routes/report_routes.py:35, 42, 45, 71, 105, 133, 192, 213; routes/task_routes.py:31, 42, 51, 67, 72, 117, 122, 158, 188, 195, 215, 227, 285; routes/user_routes.py:29, 94, 136, 155, 172; seed.py:66-74; services/notification_service.py:35; utils/helpers.py:38
Evidence: `created_at = db.Column(db.DateTime, default=datetime.utcnow)` / `user = User.query.get(user_id)`
Description: `datetime.utcnow()` está depreciado desde o Python 3.12 (emite `DeprecationWarning` no 3.13 e devolve datetime *naive*, sem timezone) — aparece em 24 pontos. `Model.query.get()` é a API legada do SQLAlchemy, removida da interface recomendada no 2.0 — aparece em 15 pontos.
Impact: Quebra em versões futuras do Python/SQLAlchemy; datetimes naive comparados entre si funcionam hoje mas falham assim que qualquer valor com timezone entrar no sistema.
Recommendation: `datetime.now(timezone.utc)` (ou `lambda: datetime.now(timezone.utc)` nos defaults de coluna) e `db.session.get(Model, id)` (PB-15). Detalhe por chamada na seção Deprecated APIs.

### F-16 [MEDIUM] Lógica duplicada: regra de atraso, serialização e validação (AP-16)
File: models/task.py:23-36, 50-60; routes/task_routes.py:17-39, 71-80, 96-114, 166-184, 284-287; routes/user_routes.py:162-180; routes/report_routes.py:33-37, 119-135
Evidence: `if t.due_date < datetime.utcnow(): if t.status != 'done' and t.status != 'cancelled':`
Description: A regra "task atrasada" está escrita **seis vezes** de forma idêntica (`models/task.py:50-60` — que ninguém chama —, `task_routes.py:30-39`, `71-80`, `284-287`, `user_routes.py:171-180`, `report_routes.py:34-36`, `132-135`). A serialização de task é reimplementada campo a campo em `task_routes.py:17-28` e `user_routes.py:162-169`, mesmo existindo `Task.to_dict()`. As validações de título/status/prioridade estão duplicadas entre `create_task` (96-114) e `update_task` (166-184) — e uma terceira vez em `utils/helpers.process_task_data`, que é código morto.
Impact: Qualquer mudança de regra precisa ser replicada em seis lugares; a divergência já existe (o `update_task` não revalida título vazio, o `create_task` sim).
Recommendation: Uma única implementação de cada regra — atraso no model, serialização na view, validação no controller — e remover as cópias (PB-14).

### F-17 [MEDIUM] N+1 queries e listagens sem paginação (AP-13)
File: routes/report_routes.py:53-68, 157-165; routes/task_routes.py:14-57, 281-287; routes/user_routes.py:12-25, 35-38
Evidence: `for u in users: user_tasks = Task.query.filter_by(user_id=u.id).all()` / `cat_data['task_count'] = Task.query.filter_by(category_id=c.id).count()`
Description: `GET /tasks` dispara duas consultas por task (`User.query.get` na linha 42 e `Category.query.get` na 51) → 1 + 2N consultas. `/reports/summary` faz uma consulta por usuário (56) além de 9 `COUNT(*)` separados (19-28) que caberiam num único `GROUP BY`, e carrega **todas** as tasks em memória (30) só para contar atrasos. `GET /categories` conta tasks por categoria em laço (163). `GET /users` força lazy-load de `u.tasks` por usuário (22). Nenhum endpoint de listagem tem `limit`/`offset` — e "Adicionar paginação na API" é literalmente uma das tasks do seed.
Impact: Degradação linear com o volume; `/tasks` com 10 mil registros gera 20 mil consultas e resposta ilimitada.
Recommendation: Usar `joinedload`/`selectinload` nos relacionamentos, consolidar contagens em `GROUP BY` dentro do model e calcular atraso em SQL; adicionar paginação opcional preservando o formato de resposta atual (PB-11).

### F-18 [MEDIUM] Tratamento de erro espalhado e engolido (AP-15)
File: routes/report_routes.py:186, 207, 221; routes/task_routes.py:62-63, 137, 204, 236; routes/user_routes.py:130, 149; utils/helpers.py:46, 49, 88
Evidence: `except: return jsonify({'error': 'Erro interno'}), 500`
Description: Há 12 `except:` nus no projeto. O pior é `routes/task_routes.py:62-63`, que envolve o handler inteiro de `GET /tasks` e transforma qualquer bug (inclusive `KeyboardInterrupt`/`SystemExit`) num 500 genérico sem log. Os blocos `try/except Exception` restantes repetem o mesmo par rollback + resposta em cada handler, e `utils/helpers.py:43-50` tem um `except:` aninhado em outro `except:`. Não existe `@app.errorhandler` em lugar nenhum.
Impact: Bugs invisíveis em produção (nada é logado com stack), 12 cópias do mesmo tratamento, formatos de erro inconsistentes entre rotas.
Recommendation: Hierarquia de erros de domínio (`NotFoundError`, `ValidationError`, `ConflictError`) levantada nos controllers e um `middlewares/error_handler.py` único que mapeia para HTTP e loga stack no servidor (PB-13).

### F-19 [MEDIUM] Validação ausente ou inconsistente (AP-14)
File: routes/report_routes.py:196-202; routes/task_routes.py:96-114, 166-184, 260-264; routes/user_routes.py:102-103, 114-116, 191-195
Evidence: `if priority < 1 or priority > 5:` / `if len(data['title']) < 3:`
Description: Os campos vindos do JSON são usados sem checagem de tipo: `POST /tasks` com `"priority": "alta"` estoura `TypeError` na linha 113 (500 em vez de 400); `PUT /tasks/<id>` com `"title": null` estoura em `len(None)` (167); `GET /tasks/search?priority=abc` quebra em `int(priority)` (261). `PUT /categories/<id>` (196) chama `data['name']` sem checar se o corpo veio vazio — `request.get_json()` pode ser `None` e estourar `TypeError`. `PUT /users/<id>` aceita `name` vazio ou `None` sem validar, enquanto `POST /users` exige nome. As regras de senha diferem entre criação ("no mínimo 4 caracteres") e atualização ("muito curta") com a mesma checagem.
Impact: Erros de cliente viram 500; dados inválidos entram no banco pelo caminho de update; mensagens inconsistentes.
Recommendation: Validação única por entidade no controller (marshmallow já está em `requirements.txt` e nunca é usado, ou validadores próprios), devolvendo sempre 400 com formato uniforme (PB-12).

### F-20 [LOW] Imports não usados e código morto (AP-21)
File: app.py:7; models/task.py:3; routes/report_routes.py:7-8; routes/task_routes.py:7; routes/user_routes.py:6; services/notification_service.py:1-48; utils/helpers.py:3-7, 19-116
Evidence: `import json, os, sys, time` (task_routes.py:7, nenhum usado) / `from utils.helpers import format_date, calculate_percentage` (report_routes.py:7, nenhum chamado)
Description: Verificado por busca em todo o projeto: `os, sys, json` (app.py), `json` (models/task.py, report_routes.py), `json, os, sys, time` (task_routes.py), `hashlib, json` (user_routes.py) e `os, json, sys, math, hashlib` (utils/helpers.py) nunca são referenciados. O módulo `services/notification_service.py` inteiro é órfão — `NotificationService` nunca é importado nem instanciado. Em `utils/helpers.py`, nove das dez funções e todas as seis constantes (110-116) têm referência única (a própria definição): `validate_email`, `sanitize_string`, `generate_id`, `log_action`, `is_valid_color`, `process_task_data`, `format_date`, `calculate_percentage`. Nos models, `Task.validate_status`, `Task.validate_priority`, `Task.is_overdue` e `User.is_admin` também nunca são chamados.
Impact: ~150 linhas de código morto que o leitor precisa descartar; `utils/` sugere utilidades compartilhadas que na prática não existem.
Recommendation: Remover imports mortos; dissolver `utils/helpers.py` nas camadas corretas mantendo só o que for efetivamente usado; integrar ou remover `services/notification_service.py` (PB-18).

### F-21 [LOW] Magic numbers e magic strings (AP-19)
File: models/task.py:11-12, 39, 47; routes/task_routes.py:96, 99, 110, 113, 177, 182, 276-279; routes/user_routes.py:64, 71, 115, 120; routes/report_routes.py:24-28, 129; app.py:34
Evidence: `if status not in ['pending', 'in_progress', 'done', 'cancelled']:` / `if len(title) < 3:` / `if t.priority <= 2:`
Description: A lista de status válidos é reescrita literalmente em 6 pontos; os papéis válidos em 2; os limites de título (3/200), senha (4) e prioridade (1/5) aparecem inline em criar e atualizar; o limiar de "alta prioridade" (`<= 2`, report_routes.py:129) e o mapeamento prioridade→nome (`critical`…`minimal`, 83-89) não têm nome. A porta 5000 é literal. Ironicamente, `utils/helpers.py:110-116` define `VALID_STATUSES`, `VALID_ROLES`, `MAX_TITLE_LENGTH`, `MIN_TITLE_LENGTH`, `MIN_PASSWORD_LENGTH` — e nenhuma é usada.
Impact: Adicionar um status exige encontrar 6 lugares; divergência silenciosa quando um deles é esquecido.
Recommendation: Constantes/Enum num único módulo de domínio, referenciadas por models, controllers e validação (PB-17).

### F-22 [LOW] Lógica booleana verbosa e `type() ==` (AP-23)
File: models/task.py:38-48, 50-60; models/user.py:34-38; routes/task_routes.py:141, 210; utils/helpers.py:103
Evidence: `if self.role == 'admin': return True else: return False` / `if type(tags) == list:`
Description: `User.is_admin`, `Task.validate_status` e `Task.validate_priority` usam `if cond: return True else: return False` no lugar de `return cond`. `Task.is_overdue` (50-60) encadeia quatro níveis de `if/else` para uma expressão booleana única. `type(x) == list` é usado três vezes em vez de `isinstance(x, list)`, o que falha com subclasses de `list`.
Impact: Ruído de leitura e condicionais mais difíceis de alterar corretamente.
Recommendation: Reduzir a expressões booleanas diretas e usar `isinstance` (PB-18).

### F-23 [LOW] Nomes pobres (AP-20)
File: routes/report_routes.py:33-68, 119-135, 161-164; routes/task_routes.py:16-59, 268-287; routes/user_routes.py:14-24, 37, 141, 161-181; seed.py:16-91
Evidence: `for t in all_tasks:` / `for u in users:` / `for c in categories:` / `cat_data`, `td`, `u1`, `c1`
Description: Laços sobre coleções de domínio usam variáveis de uma letra (`t`, `u`, `c`, `p1`…`p5`), e abreviações como `cat`, `cid`/`cat_id`, `td`, `pwd`, `s` aparecem em corpos longos (o laço de `summary_report` tem 15 linhas). `utils/helpers.py` é um grab-bag que também guarda configuração (constantes), contrariando o nome. Nota: os nomes de campos JSON (`user_id`, `due_date`, `tags`…) fazem parte do contrato público e **não** devem ser renomeados.
Impact: Leitura mais lenta e maior chance de erro em blocos longos.
Recommendation: Nomes que revelam a intenção (`task`, `user`, `category`, `priority_counts`) — a extração para controllers (F-10/F-12/F-13) é a oportunidade natural (PB-18).

### F-24 [LOW] `print` usado como log (AP-22)
File: routes/task_routes.py:149, 153, 219, 234; routes/user_routes.py:83, 89, 147; services/notification_service.py:21, 24; utils/helpers.py:39, 41; seed.py:93-96
Evidence: `print(f"Task criada: {task.id} - {task.title}")` / `print(f"ERRO: {str(e)}")`
Description: Treze chamadas de `print` fazem o papel de log operacional, sem nível, timestamp estruturado ou destino configurável. `utils/helpers.log_action` (36-41) é uma tentativa de centralizar isso — e é código morto. Em `routes/user_routes.py:89` e `routes/task_routes.py:153`, a exceção é impressa em stdout em vez de logada com stack (relacionado a F-18). Os `print` de `seed.py:93-96` são saída de CLI legítima e não precisam mudar.
Impact: Sem observabilidade em produção; a saída se perde quando o processo não tem stdout capturado.
Recommendation: Usar o `logging` da biblioteca padrão (ou `app.logger`) com níveis, configurado no composition root (PB-19).

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| `models/category.py:11` | `datetime.utcnow` (default de coluna) | `lambda: datetime.now(timezone.utc)` |
| `models/task.py:15` | `datetime.utcnow` (default de coluna) | `lambda: datetime.now(timezone.utc)` |
| `models/task.py:16` | `datetime.utcnow` (default + onupdate) | `lambda: datetime.now(timezone.utc)` |
| `models/task.py:52` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `models/user.py:14` | `datetime.utcnow` (default de coluna) | `lambda: datetime.now(timezone.utc)` |
| `routes/report_routes.py:35, 42, 45, 71, 133` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `routes/report_routes.py:105` | `User.query.get(user_id)` | `db.session.get(User, user_id)` |
| `routes/report_routes.py:192, 213` | `Category.query.get(cat_id)` | `db.session.get(Category, cat_id)` |
| `routes/task_routes.py:31, 72, 215, 285` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `routes/task_routes.py:42, 117, 188` | `User.query.get(...)` | `db.session.get(User, ...)` |
| `routes/task_routes.py:51, 122, 195` | `Category.query.get(...)` | `db.session.get(Category, ...)` |
| `routes/task_routes.py:67, 158, 227` | `Task.query.get(task_id)` | `db.session.get(Task, task_id)` |
| `routes/user_routes.py:29, 94, 136, 155` | `User.query.get(user_id)` | `db.session.get(User, user_id)` |
| `routes/user_routes.py:172` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `seed.py:66, 67, 69, 70, 74` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `services/notification_service.py:35` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |
| `utils/helpers.py:38` | `datetime.utcnow()` | `datetime.now(timezone.utc)` |

Nota: `Model.query.filter_by(...).all()` (ex.: `routes/user_routes.py:35`, `routes/report_routes.py:56`) também é a API legada do SQLAlchemy; continua funcionando no 2.x e está classificada como LOW, logo não foi aberta como finding separado — será convertida para `db.session.scalars(select(...))` onde o código for tocado.

## Architecture Notes
- Current architecture: **PARTIALLY LAYERED** — as pastas `models/`, `routes/`, `services/` e `utils/` existem, mas as rotas concentram regra de negócio, consultas ORM e serialização; a configuração está inline em `app.py`; não há controllers, middlewares de erro/auth nem app factory; `services/` está órfão e `utils/` é um grab-bag com código morto.
- Proposed target: evolução **in place** (sem renomear o que já mapeia para uma camada), seguindo o layout MVC de referência para Flask:

```text
task-manager-api/
├── app.py                          # entry point fino: create_app() + app.run() (preserva `python app.py`)
├── seed.py                         # usa a factory em vez de importar o app global
├── requirements.txt
├── config/
│   └── settings.py                 # Config lida de os.environ (SECRET_KEY, DATABASE_URL, DEBUG, HOST, PORT, CORS, SMTP)
├── database.py                     # instância db (mantido)
├── errors.py                       # AppError: NotFoundError, ValidationError, ConflictError, UnauthorizedError
├── models/                         # Model: entidades + consultas/persistência
│   ├── task.py                     # + find_by_id, search, stats, is_overdue (única implementação)
│   ├── user.py                     # + find_by_email, sem password no serializer
│   └── category.py                 # + cascade declarada
├── controllers/                    # Controller: casos de uso e regras de negócio
│   ├── task_controller.py
│   ├── user_controller.py
│   ├── auth_controller.py
│   ├── category_controller.py
│   └── report_controller.py
├── routes/                         # View: Blueprints finos (parse + serialize)
│   ├── task_routes.py
│   ├── user_routes.py
│   ├── auth_routes.py
│   ├── category_routes.py          # extraído de report_routes.py
│   ├── report_routes.py
│   └── health_routes.py            # / e /health, hoje em app.py
├── middlewares/
│   ├── error_handler.py            # AppError → HTTP, log de stack, 500 genérico
│   └── auth.py                     # guarda de token + verificação de papel
└── services/
    ├── password_hasher.py          # werkzeug generate/check_password_hash
    ├── token_service.py            # itsdangerous: emissão/validação assinada
    └── notification_service.py     # credenciais vindas de config
```

`utils/helpers.py` é dissolvido: constantes de domínio vão para um módulo de constantes referenciado pelos models/controllers, validações vão para os controllers, e o código morto é removido.

================================
Total: 24 findings
================================
