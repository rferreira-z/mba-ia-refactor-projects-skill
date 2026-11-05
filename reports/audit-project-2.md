================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js v24.22.1, CommonJS) + Express ^4.18.2 (instalado 4.22.1) + sqlite3 ^5.1.6
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 4

| # | Severity | Anti-pattern | Location |
|---|---|---|---|
| F-01 | CRITICAL | God class concentrando toda a aplicação | `src/AppManager.js:1-141` |
| F-02 | CRITICAL | Número de cartão e chave de pagamento em log | `src/AppManager.js:45` |
| F-03 | CRITICAL | Endpoints administrativo e destrutivo sem autenticação | `src/AppManager.js:80, 131` |
| F-04 | CRITICAL | Credenciais e chave de produção hardcoded | `src/utils.js:1-7` |
| F-05 | CRITICAL | Armazenamento inseguro de senhas | `src/utils.js:17-23`; `src/AppManager.js:18, 68` |
| F-06 | HIGH | Regra de negócio dentro das rotas (fat route) | `src/AppManager.js:28-137` |
| F-07 | HIGH | Acoplamento forte, sem injeção de dependência | `src/AppManager.js:7, 25-26`; `src/app.js:5-10` |
| F-08 | HIGH | Escrita multi-passo sem transação e exclusão com órfãos | `src/AppManager.js:50-63, 131-137` |
| F-09 | HIGH | Estado global mutável | `src/utils.js:9-15, 25` |
| F-10 | HIGH | Configuração de runtime sem override por ambiente | `src/utils.js:1-7` |
| F-11 | MEDIUM | N+1 de queries no relatório financeiro | `src/AppManager.js:83-127` |
| F-12 | MEDIUM | Validação de entrada ausente/inconsistente | `src/AppManager.js:35, 68, 132` |
| F-13 | MEDIUM | Erros engolidos e tratamento espalhado | `src/AppManager.js:57, 92, 104, 106, 133` |
| F-14 | MEDIUM | API sqlite3 callback-only aninhada nos handlers | `src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133` |
| F-15 | MEDIUM | Callback hell e contadores manuais de conclusão | `src/AppManager.js:37-77, 89-127` |
| F-16 | LOW | Magic numbers / magic strings | `src/AppManager.js:46`; `src/utils.js:6, 19, 20, 22` |
| F-17 | LOW | Nomenclatura ruim / enganosa | `src/AppManager.js:4, 29-33`; `src/utils.js:17` |
| F-18 | LOW | Código morto e exports não utilizados | `src/AppManager.js:2`; `src/utils.js:2, 5, 10, 25` |
| F-19 | LOW | `console.log` usado como logging | `src/app.js:13`; `src/utils.js:13` |

## Findings

### F-01 [CRITICAL] God class concentrando toda a aplicação (AP-03)
File: src/AppManager.js:1-141
Evidence: `class AppManager { ... initDb() { ... } setupRoutes(app) { ... } }`
Description: Uma única classe de 141 linhas acumula cinco responsabilidades: CONFIG/INFRA (abre a conexão sqlite3 na linha 7), PERSISTENCE (DDL, seed e 11 queries SQL), ROUTING (declara os 3 endpoints nas linhas 28, 80 e 131), BUSINESS (decisão de aprovação de pagamento na linha 46, criação implícita de usuário na linha 66, agregação de receita na linha 109) e PRESENTATION (monta status HTTP e corpos de resposta em 10 pontos). Não existe nenhuma pasta de camada no projeto.
Impact: Impossível testar qualquer regra isoladamente — qualquer teste precisa subir Express e SQLite juntos; qualquer mudança de persistência força tocar nas rotas; o arquivo é um ponto único de conflito em qualquer evolução.
Recommendation: Decompor em `models/` (repositórios por agregado: user, course, enrollment, payment, auditLog), `controllers/` (casos de uso checkout, relatório financeiro, exclusão de usuário), `views/` (`express.Router()` finos), `config/`, `middlewares/` e `database/connection.js`, com `createApp.js` como composition root (PB-03).

### F-02 [CRITICAL] Número de cartão e chave de pagamento em log (AP-06)
File: src/AppManager.js:45
Evidence: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`);`
Description: O PAN completo enviado pelo cliente e a chave de produção do gateway (`pk_live_...`) são escritos em texto puro no stdout a cada checkout.
Impact: Vazamento de dado de cartão (violação direta de PCI-DSS) e da chave do gateway para qualquer pessoa com acesso aos logs do processo, do container ou do agregador de logs.
Recommendation: Remover por completo o log do PAN e da chave; isolar o gateway em `services/paymentGateway.js` que receba apenas os últimos 4 dígitos para fins de rastreio, e logar somente um identificador de transação (PB-06).

### F-03 [CRITICAL] Endpoints administrativo e destrutivo sem autenticação (AP-05)
File: src/AppManager.js:80, 131
Evidence: `app.get('/api/admin/financial-report', (req, res) => {` / `app.delete('/api/users/:id', (req, res) => {`
Description: `GET /api/admin/financial-report` expõe receita por curso e nome + pagamento de cada aluno sem qualquer middleware de autenticação ou autorização. `DELETE /api/users/:id` apaga qualquer usuário por ID, sem autenticação, sem checagem de propriedade e sem verificar se o ID existe. A aplicação não possui nenhum mecanismo de autenticação em lugar nenhum.
Impact: Qualquer pessoa com acesso de rede lê o faturamento completo e a base de alunos (PII), e pode apagar toda a tabela de usuários iterando IDs. Severidade CRITICAL pela rota destrutiva sem proteção.
Recommendation: Criar `middlewares/auth.js` com um guard aplicado às rotas `admin` e à exclusão, e mover a decisão de autorização para o controller (PB-05). Enquanto não houver um mecanismo de identidade, no mínimo exigir uma chave administrativa vinda de config/env.

### F-04 [CRITICAL] Credenciais e chave de produção hardcoded (AP-01)
File: src/utils.js:1-7
Evidence: `dbPass: "senha_super_secreta_prod_123",` / `paymentGatewayKey: "pk_live_1234567890abcdef",`
Description: O objeto `config` carrega literalmente usuário e senha de banco, a chave live do gateway de pagamento, o usuário SMTP e a porta — tudo versionado no repositório. Nenhum valor é lido de `process.env`.
Impact: Qualquer pessoa com acesso ao repositório (ou ao histórico do Git) obtém credenciais de produção; a rotação dessas chaves exige novo deploy; o mesmo código não pode rodar em dois ambientes.
Recommendation: Substituir por `config/settings.js` lendo `process.env` com defaults explicitamente não-produtivos (`"dev-only-change-me"`), falhando no boot se uma variável obrigatória faltar em produção. Rotacionar as chaves expostas (PB-01).

### F-05 [CRITICAL] Armazenamento inseguro de senhas (AP-04)
File: src/utils.js:17-23; src/AppManager.js:18, 68
Evidence: `hash += Buffer.from(pwd).toString('base64').substring(0, 2);` / `return hash.substring(0, 10);`
Description: `badCrypto` não é hashing: concatena 10.000 vezes os mesmos 2 primeiros caracteres do base64 da senha e devolve os 10 primeiros caracteres — ou seja, a saída depende apenas dos 2 primeiros caracteres do base64 do input, sem sal, de forma trivialmente reversível. Além disso o seed na linha 18 grava a senha `'123'` em texto puro, e a linha 68 aplica um default fixo `"123456"` quando o campo `pwd` não é enviado.
Impact: Todas as senhas do sistema são recuperáveis em segundos; o espaço de saída colapsa a algumas dezenas de valores, permitindo colisões em massa.
Recommendation: Remover `badCrypto` e criar `services/passwordHasher.js` usando `crypto.scrypt` (stdlib, sem nova dependência) com sal aleatório por usuário; rejeitar o cadastro quando a senha não for informada em vez de aplicar um default (PB-04).

### F-06 [HIGH] Regra de negócio dentro das rotas (fat route) (AP-07)
File: src/AppManager.js:28-137
Evidence: `let status = cc.startsWith("4") ? "PAID" : "DENIED";`
Description: Os três handlers somam 108 das 141 linhas do arquivo e executam, dentro do callback de rota, SQL direto, a regra de aprovação de pagamento (linha 46), o cadastro implícito de usuário no checkout (linhas 66-72), a escrita da trilha de auditoria (linha 57) e a agregação de receita do relatório (linha 109). O handler de checkout sozinho tem 50 linhas.
Impact: Nenhuma regra de negócio pode ser exercitada sem uma requisição HTTP; a lógica de aprovação de pagamento não é reutilizável nem auditável; mudanças de contrato HTTP e mudanças de regra colidem no mesmo bloco.
Recommendation: Views apenas parseiam a entrada e chamam uma função de controller; a decisão de pagamento vai para `services/paymentGateway.js`, o fluxo de checkout para `controllers/checkoutController.js` e as queries para os repositórios em `models/` (PB-07).

### F-07 [HIGH] Acoplamento forte, sem injeção de dependência (AP-09)
File: src/AppManager.js:7, 25-26; src/app.js:5-10
Evidence: `this.db = new sqlite3.Database(':memory:');` / `const manager = new AppManager(); manager.initDb(); manager.setupRoutes(app);`
Description: `AppManager` instancia sua própria conexão de banco no construtor, não há factory de aplicação (`createApp()`), e `src/app.js` cria o app Express, inicializa o banco e sobe o servidor no escopo de módulo — tudo executa no `require`. O truque `const self = this` na linha 26 existe só para contornar o rebind de `this` nos callbacks do sqlite3.
Impact: Impossível substituir o banco por um dublê em teste ou apontar para um arquivo SQLite em outro ambiente; importar o módulo já abre conexão e escuta porta.
Recommendation: Extrair `database/connection.js` como factory, passar a conexão por parâmetro aos repositórios, criar `createApp.js` como composition root e deixar `src/app.js` apenas chamando a factory e `listen` (PB-08).

### F-08 [HIGH] Escrita multi-passo sem transação e exclusão com órfãos (AP-11)
File: src/AppManager.js:50-63, 131-137
Evidence: `this.db.run("INSERT INTO enrollments ...")` → `INSERT INTO payments ...` → `INSERT INTO audit_logs ...` (encadeados, sem `BEGIN`)
Description: O checkout faz até quatro escritas independentes (usuário, matrícula, pagamento, auditoria) sem `BEGIN`/`COMMIT`: se o `INSERT` de `payments` falhar (linha 55), a matrícula da linha 50 já está persistida e o cliente recebe 500 tendo ficado matriculado sem pagamento registrado. Em `DELETE /api/users/:id` o usuário é removido enquanto `enrollments` e `payments` continuam referenciando o `user_id` inexistente — a própria resposta da linha 135 admite isso.
Impact: Corrupção de dados financeiros: matrículas sem pagamento e pagamentos órfãos que o relatório financeiro passa a reportar como aluno `'Unknown'` (linha 113).
Recommendation: Envolver o fluxo de checkout em transação explícita no model (`BEGIN IMMEDIATE` / `COMMIT` / `ROLLBACK`) e tratar a exclusão de usuário como operação transacional em cascata (ou bloqueá-la quando houver matrículas), decidida no controller (PB-09).

### F-09 [HIGH] Estado global mutável (AP-08)
File: src/utils.js:9-15, 25
Evidence: `let globalCache = {};` / `let totalRevenue = 0;` / `globalCache[key] = data;`
Description: `globalCache` é um objeto de módulo mutado por `logAndCache` a cada checkout (chamado em AppManager.js:59) e exportado por referência; `totalRevenue` é exportado como primitivo, de modo que qualquer consumidor recebe uma cópia congelada em 0 — um contador que nunca poderia funcionar.
Impact: Cache compartilhado entre todas as requisições, sem limite de tamanho nem expiração (vazamento de memória conforme o número de usuários cresce) e com acoplamento invisível entre partes do sistema; estado não isolável em teste.
Recommendation: Eliminar o cache global; se o comportamento for necessário, encapsular em um serviço com ciclo de vida explícito criado no composition root. Remover `totalRevenue` (PB-08).

### F-10 [HIGH] Configuração de runtime sem override por ambiente (AP-10)
File: src/utils.js:1-7
Evidence: `port: 3000`
Description: Porta, credenciais e endpoints de infraestrutura são literais no código, sem leitura de `process.env` e sem validação no boot. Não há separação entre configuração de desenvolvimento e de produção.
Impact: A mesma imagem/artefato não pode ser promovida entre ambientes; qualquer ajuste operacional exige alteração de código e novo deploy.
Recommendation: `config/settings.js` lendo `process.env.PORT` e demais variáveis com defaults de desenvolvimento seguros e validação de obrigatoriedade na inicialização (PB-01).

### F-11 [MEDIUM] N+1 de queries no relatório financeiro (AP-13)
File: src/AppManager.js:83-127
Evidence: `courses.forEach(c => { this.db.all("SELECT * FROM enrollments WHERE course_id = ?", ... this.db.get("SELECT name, email FROM users WHERE id = ?", ... this.db.get("SELECT amount, status FROM payments WHERE enrollment_id = ?", ...`
Description: Para `C` cursos e `M` matrículas, o endpoint executa `1 + C + 2·M` queries: uma por curso para buscar matrículas (linha 92) e mais duas por matrícula, para usuário (linha 104) e pagamento (linha 106), ambas dentro de `forEach` aninhados. Nenhum `JOIN` ou agregação é usado.
Impact: Latência do relatório cresce linearmente com a base de alunos; em um endpoint administrativo sem paginação isso satura a conexão SQLite conforme o catálogo cresce.
Recommendation: Substituir por uma única query com `JOIN` entre `courses`, `enrollments`, `users` e `payments` (com agregação de receita via `SUM` filtrado por `status = 'PAID'`), encapsulada em um método do model de relatório (PB-11).

### F-12 [MEDIUM] Validação de entrada ausente/inconsistente (AP-14)
File: src/AppManager.js:35, 68, 132
Evidence: `if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");`
Description: A checagem só testa presença por truthiness: `c_id` com valor `0` é rejeitado indevidamente, e qualquer tipo é aceito (`c_id: "abc"`, `card: 123` — este último faz `cc.startsWith` lançar `TypeError` na linha 46 e derrubar o processo por exceção não capturada em callback). `pwd` não é exigido e cai num default fixo (linha 68). O formato do e-mail nunca é validado. Em `DELETE /api/users/:id` (linha 132) o `id` é usado cru, sem validar que é um inteiro, e a rota responde sucesso mesmo quando nenhuma linha é afetada.
Impact: Respostas 400 incorretas, crash do processo com payload malformado e exclusões silenciosamente no-op que o cliente interpreta como sucesso.
Recommendation: Centralizar a validação de cada payload em uma função dedicada chamada pela view antes do controller, verificando presença, tipo e formato, e lançando `ValidationError` tratado pelo middleware de erro (PB-12).

### F-13 [MEDIUM] Erros engolidos e tratamento espalhado (AP-15)
File: src/AppManager.js:57, 92, 104, 106, 133
Evidence: `this.db.run("INSERT INTO audit_logs ...", [...], (err) => { logAndCache(...); res.status(200).json({ msg: "Sucesso", ... }); });`
Description: Cinco callbacks recebem `err` e nunca o consultam: a falha ao gravar a auditoria (linha 57) retorna 200 de sucesso; no relatório, erros em `enrollments` (linha 92), `users` (linha 104) e `payments` (linha 106) são ignorados — no caso da linha 92, `enrollments` vem `undefined` e `enrollments.length` lança `TypeError` dentro de um callback assíncrono, derrubando o processo. Na linha 133 o erro da exclusão é descartado e a rota responde sucesso. Não existe middleware de erro Express `(err, req, res, next)`, e os formatos de resposta de erro misturam texto puro (`res.send("Erro DB")`) com JSON.
Impact: Falhas silenciosas de persistência vendidas ao cliente como sucesso, crash do processo e contrato de erro inconsistente entre endpoints.
Recommendation: Hierarquia de erros de domínio em `errors.js`, `middlewares/errorHandler.js` único formatando `{ erro: ... }` com o status correto, `middlewares/asyncHandler.js` para propagar rejeições, e repositórios que rejeitam a promise em vez de ignorar `err` (PB-13).

### F-14 [MEDIUM] API sqlite3 callback-only aninhada nos handlers (AP-17)
File: src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133
Evidence: `this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [cid], (err, course) => {`
Description: As 11 chamadas ao driver usam exclusivamente o estilo callback do `sqlite3`, diretamente dentro dos handlers de rota, o que impede `async/await`, `try/catch` e qualquer propagação de erro para o Express. É o padrão legado listado no catálogo para `Node sqlite3`.
Impact: Erros assíncronos não alcançam o middleware de erro do Express; o código fica preso ao encadeamento manual descrito em F-15.
Recommendation: Promisificar `run`/`get`/`all` com `util.promisify` em `database/connection.js` (preservando o acesso a `this.lastID` via wrapper dedicado) e escrever repositórios `async` (PB-15).

### F-15 [MEDIUM] Callback hell e contadores manuais de conclusão (AP-18)
File: src/AppManager.js:37-77, 89-127
Evidence: `enrPending--; if (enrPending === 0) { report.push(courseData); coursesPending--; if (coursesPending === 0) res.json(report); }`
Description: O checkout aninha até 4 níveis de callbacks (linhas 37 → 40 → 50 → 54 → 57), exigindo o alias `self` da linha 26 porque `function(err)` nas linhas 50/54 rebinda `this` para a statement do sqlite3. O relatório financeiro coordena paralelismo com os contadores manuais `coursesPending` e `enrPending`, de forma que a ordem de `report` depende da ordem de conclusão das queries — a resposta não é determinística — e, se qualquer callback falhar, o contador nunca zera e a requisição fica pendurada até o timeout do cliente.
Impact: Resposta com ordenação não determinística, requisições que nunca terminam em caso de erro, e fluxo praticamente impossível de alterar com segurança.
Recommendation: Converter para `async/await` sobre a camada promisificada de F-14, substituindo os contadores por uma única query agregada (F-11) e deixando a ordenação explícita no model (PB-16).

### F-16 [LOW] Magic numbers / magic strings (AP-19)
File: src/AppManager.js:46; src/utils.js:6, 19, 20, 22
Evidence: `let status = cc.startsWith("4") ? "PAID" : "DENIED";` / `for(let i = 0; i < 10000; i++)`
Description: A regra de aprovação de pagamento está codificada como o literal `"4"` sem nomeação, e os status `"PAID"`/`"DENIED"` são strings repetidas sem constante (reaparecem em AppManager.js:48 e :108). Em `utils.js`, `10000`, `substring(0, 2)` e `substring(0, 10)` não têm significado documentado, assim como a porta `3000`.
Impact: Mudar a regra de bandeira ou um valor de status exige caçar literais espalhados, com risco de divergência entre escrita e leitura.
Recommendation: Extrair `PAYMENT_STATUS` e a regra de bandeira para constantes do `services/paymentGateway.js`, e mover a porta para config (PB-17).

### F-17 [LOW] Nomenclatura ruim / enganosa (AP-20)
File: src/AppManager.js:4, 29-33; src/utils.js:17
Evidence: `let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd; let cid = req.body.c_id; let cc = req.body.card;`
Description: Cinco variáveis de uma letra/abreviação opaca no handler mais longo do arquivo — `e` inclusive colide conceitualmente com o `err` dos callbacks aninhados logo abaixo. `AppManager` não descreve nada, `utils.js` abriga configuração (não utilitários) e `badCrypto` admite no nome que não serve ao propósito. Os nomes de campo do payload (`usr`, `eml`, `pwd`, `c_id`, `card`) fazem parte do contrato público e devem ser preservados na deserialização.
Impact: Leitura e revisão do fluxo mais crítico do sistema exigem esforço desproporcional.
Recommendation: Renomear variáveis internas para `name`, `email`, `password`, `courseId`, `cardNumber`, dissolver `utils.js` nas camadas corretas e nomear os módulos pelo papel (`passwordHasher`, `settings`) — mantendo os nomes dos campos JSON intactos (PB-18).

### F-18 [LOW] Código morto e exports não utilizados (AP-21)
File: src/AppManager.js:2; src/utils.js:2, 5, 10, 25
Evidence: `const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');`
Description: `totalRevenue` é importado em AppManager.js:2 e nunca referenciado no arquivo; `dbUser` (utils.js:2), `dbPass` (utils.js:3) e `smtpUser` (utils.js:5) são definidos mas nunca lidos em lugar algum do projeto; `globalCache` e `totalRevenue` são exportados na linha 25 sem nenhum consumidor externo.
Impact: Sugere integrações (banco externo, envio de e-mail) que não existem, além de manter credenciais no repositório sem qualquer função — amplificando F-04.
Recommendation: Remover os símbolos não utilizados junto com a dissolução de `utils.js` (PB-18).

### F-19 [LOW] `console.log` usado como logging (AP-22)
File: src/app.js:13; src/utils.js:13
Evidence: `console.log(\`[LOG] Salvando no cache: ${key}\`);`
Description: Logs operacionais escritos com `console.log`, sem nível, timestamp ou contexto estruturado. O log de AppManager.js:45 é tratado separadamente em F-02 por vazar dado sensível.
Impact: Logs não filtráveis por severidade e não correlacionáveis por requisição em produção.
Recommendation: Centralizar em um logger simples com níveis (`middlewares/requestLogger.js` + helper), usando a stdlib — sem introduzir nova dependência (PB-19).

## Deprecated APIs
| Location | Deprecated API | Modern replacement |
|---|---|---|
| `src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133` | API callback-only do `sqlite3` aninhada nos handlers | wrapper promisificado (`util.promisify`) + funções `async` de repositório |

Nenhum outro item da tabela AP-17 se aplica: não há `new Buffer()` (o código usa `Buffer.from` em utils.js:20), `url.parse()`, `fs.exists()`, `crypto.createCipher()`, `util.isArray()`, `body-parser`, `req.param()`, `res.send(status)`, `res.json(status, obj)` nem `app.del()` — o projeto já usa `express.json()` (app.js:6) e `app.delete()` (AppManager.js:131).

Verificações que **não** geraram finding: AP-02 (SQL injection) — todas as 11 queries usam placeholders `?` com array de parâmetros separado; AP-12 (token de autenticação falso) — não existe endpoint de autenticação no projeto, a ausência total de autenticação está coberta em F-03; AP-16 (lógica duplicada) — a repetição de respostas de erro ad-hoc é tratada em F-13, cuja correção a elimina; AP-23 (lógica booleana verbosa) — não encontrado.

## Architecture Notes
- Current architecture: MONOLITH — `src/AppManager.js` mistura routing, regra de negócio, persistência, apresentação e infraestrutura em uma única classe de 141 linhas, com as rotas ligadas diretamente ao driver SQLite; não existe nenhuma pasta de camada.
- Proposed target: layout MVC de referência para Node/Express (mvc-guidelines §"Reference layouts"), com reestruturação completa (estratégia `MONOLITH`):

```text
ecommerce-api-legacy/
├── package.json                      # "npm start" preservado
└── src/
    ├── app.js                        # entry point: createApp() + listen (comando original intacto)
    ├── createApp.js                  # composition root: config, conexão, serviços, views, middlewares
    ├── config/settings.js            # process.env com defaults de desenvolvimento
    ├── database/connection.js        # abre o SQLite, run/get/all promisificados, schema + seed
    ├── models/userModel.js           # repositórios: SQL parametrizado e mapeamento linha↔objeto
    ├── models/courseModel.js
    ├── models/enrollmentModel.js
    ├── models/paymentModel.js
    ├── models/auditLogModel.js
    ├── models/reportModel.js         # consulta agregada do relatório financeiro (resolve o N+1)
    ├── controllers/checkoutController.js
    ├── controllers/reportController.js
    ├── controllers/userController.js
    ├── views/checkoutRoutes.js       # express.Router(), handlers finos
    ├── views/reportRoutes.js
    ├── views/userRoutes.js
    ├── middlewares/errorHandler.js   # (err, req, res, next) — formato de erro único
    ├── middlewares/asyncHandler.js
    ├── middlewares/auth.js           # guard das rotas admin e destrutiva
    ├── services/paymentGateway.js    # regra de aprovação, sem log de PAN/chave
    ├── services/passwordHasher.js    # crypto.scrypt com sal (stdlib)
    └── errors.js                     # hierarquia AppError
```

`src/AppManager.js` e `src/utils.js` serão removidos após as rotas passarem a ser servidas pelas novas camadas.

================================
Total: 19 findings
================================
