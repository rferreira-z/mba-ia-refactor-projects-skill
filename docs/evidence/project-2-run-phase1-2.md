I'll start Phase 1 — project analysis.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/references/project-analysis.md

> [tool] Bash: ls -la && git rev-parse --show-toplevel

> [tool] Bash: find src -type f | sort && echo "---" && find . -type f \( -name '*.js' -o -name '*.ts' -o -name '*.mjs' -o -name '*.sql' \) -not -path './node_modules/*' -not 

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/package.json

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/README.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/api.http

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/app.js

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/AppManager.js

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/utils.js

> [tool] Bash: node --version; npm ls express sqlite3 --depth=0 2>/dev/null | head -20

```text
================================
PHASE 1: PROJECT ANALYSIS
================================
Language:      JavaScript (Node.js) — runtime local v24.22.1, CommonJS
Framework:     Express ^4.18.2 (instalado: 4.22.1)
Dependencies:  express ^4.18.2, sqlite3 ^5.1.6
Domain:        LMS com checkout — usuários (users), cursos (courses), matrículas (enrollments), pagamentos (payments) e trilha de auditoria (audit_logs)
Architecture:  MONOLITH — AppManager.js (141 linhas) acumula ROUTING + BUSINESS + PERSISTENCE + PRESENTATION + INFRA; utils.js acumula CONFIG + INFRA; não há pastas de camada
Source files:  3 files analyzed (~180 lines)
Entry point:   src/app.js (npm start → node src/app.js)
DB:            SQLite em memória (:memory:, driver sqlite3 cru) — tables: users, courses, enrollments, payments, audit_logs
Endpoints:     3 routes (src/AppManager.js:28, :80, :131)
================================
```

Rotas mapeadas:
- `POST /api/checkout` → `src/AppManager.js:28`
- `GET /api/admin/financial-report` → `src/AppManager.js:80`
- `DELETE /api/users/:id` → `src/AppManager.js:131`

Agora Phase 2 — auditoria.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/references/anti-patterns-catalog.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/references/report-template.md

> [tool] Bash: python3 /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/scripts/scan_antipatterns.py 

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/references/mvc-guidelines.md

Verifiquei cada hit do scanner lendo os 3 arquivos na íntegra. Confirmo que **AP-02 (SQL injection) não existe** — todas as queries usam placeholders `?`. Montando o relatório.

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/reports/audit-project-2.md

```text
================================
ARCHITECTURE AUDIT REPORT
================================
Project: ecommerce-api-legacy
Stack:   JavaScript (Node.js v24.22.1, CommonJS) + Express ^4.18.2 (instalado 4.22.1) + sqlite3 ^5.1.6
Files:   3 analyzed | ~180 lines of code
Date:    2026-11-05

## Summary
CRITICAL: 5 | HIGH: 5 | MEDIUM: 5 | LOW: 4
```

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
Recommendation: Decompor em `models/`, `controllers/`, `views/`, `config/`, `middlewares/` e `database/connection.js`, com `createApp.js` como composition root (PB-03).

### F-02 [CRITICAL] Número de cartão e chave de pagamento em log (AP-06)
File: src/AppManager.js:45
Evidence: `console.log(\`Processando cartão ${cc} na chave ${config.paymentGatewayKey}\`);`
Description: O PAN completo enviado pelo cliente e a chave de produção do gateway (`pk_live_...`) são escritos em texto puro no stdout a cada checkout.
Impact: Vazamento de dado de cartão (violação direta de PCI-DSS) e da chave do gateway para qualquer pessoa com acesso aos logs.
Recommendation: Remover o log do PAN e da chave; isolar o gateway em `services/paymentGateway.js` (PB-06).

### F-03 [CRITICAL] Endpoints administrativo e destrutivo sem autenticação (AP-05)
File: src/AppManager.js:80, 131
Evidence: `app.get('/api/admin/financial-report', ...)` / `app.delete('/api/users/:id', ...)`
Description: O relatório financeiro expõe receita por curso e nome + pagamento de cada aluno sem autenticação. `DELETE /api/users/:id` apaga qualquer usuário por ID, sem autenticação nem checagem de propriedade. Não existe autenticação em lugar nenhum da aplicação.
Impact: Qualquer pessoa com acesso de rede lê o faturamento e a base de alunos (PII), e pode apagar a tabela de usuários iterando IDs.
Recommendation: `middlewares/auth.js` aplicado às rotas admin e destrutiva, com a chave vinda de config/env (PB-05).

### F-04 [CRITICAL] Credenciais e chave de produção hardcoded (AP-01)
File: src/utils.js:1-7
Evidence: `dbPass: "senha_super_secreta_prod_123",` / `paymentGatewayKey: "pk_live_1234567890abcdef",`
Description: O objeto `config` carrega usuário e senha de banco, chave live do gateway, usuário SMTP e porta — tudo versionado. Nenhum valor vem de `process.env`.
Impact: Credenciais de produção acessíveis no repositório e no histórico do Git; rotação exige novo deploy.
Recommendation: `config/settings.js` lendo `process.env` com defaults não-produtivos; rotacionar as chaves expostas (PB-01).

### F-05 [CRITICAL] Armazenamento inseguro de senhas (AP-04)
File: src/utils.js:17-23; src/AppManager.js:18, 68
Evidence: `hash += Buffer.from(pwd).toString('base64').substring(0, 2);` / `return hash.substring(0, 10);`
Description: `badCrypto` concatena 10.000 vezes os mesmos 2 primeiros caracteres do base64 da senha e devolve 10 caracteres — a saída depende apenas dos 2 primeiros caracteres do input, sem sal. O seed grava `'123'` em texto puro e a linha 68 aplica default fixo `"123456"`.
Impact: Senhas recuperáveis em segundos; espaço de saída colapsa a algumas dezenas de valores.
Recommendation: `services/passwordHasher.js` com `crypto.scrypt` e sal por usuário; rejeitar cadastro sem senha (PB-04).

### F-06 [HIGH] Regra de negócio dentro das rotas (fat route) (AP-07)
File: src/AppManager.js:28-137
Evidence: `let status = cc.startsWith("4") ? "PAID" : "DENIED";`
Description: Os três handlers somam 108 das 141 linhas e executam SQL direto, regra de aprovação de pagamento (46), cadastro implícito de usuário (66-72), auditoria (57) e agregação de receita (109). O checkout sozinho tem 50 linhas.
Impact: Nenhuma regra testável sem HTTP; lógica de pagamento não reutilizável nem auditável.
Recommendation: Views finas → controller; decisão de pagamento em `services/`; queries em `models/` (PB-07).

### F-07 [HIGH] Acoplamento forte, sem injeção de dependência (AP-09)
File: src/AppManager.js:7, 25-26; src/app.js:5-10
Evidence: `this.db = new sqlite3.Database(':memory:');`
Description: `AppManager` instancia sua própria conexão no construtor, não há `createApp()`, e `src/app.js` cria app, inicializa banco e sobe servidor no escopo de módulo. O alias `const self = this` existe só para contornar o rebind de `this` nos callbacks do sqlite3.
Impact: Impossível substituir o banco em teste ou apontar para outro ambiente; `require` já abre conexão e escuta porta.
Recommendation: `database/connection.js` como factory + `createApp.js` como composition root (PB-08).

### F-08 [HIGH] Escrita multi-passo sem transação e exclusão com órfãos (AP-11)
File: src/AppManager.js:50-63, 131-137
Evidence: `INSERT INTO enrollments` → `INSERT INTO payments` → `INSERT INTO audit_logs` encadeados, sem `BEGIN`
Description: Até quatro escritas independentes sem transação: se `payments` falhar (55), a matrícula da linha 50 já está persistida e o cliente recebe 500 estando matriculado sem pagamento. No `DELETE`, `enrollments` e `payments` ficam apontando para `user_id` inexistente — a própria resposta da linha 135 admite isso.
Impact: Corrupção de dados financeiros; o relatório passa a reportar aluno `'Unknown'` (linha 113).
Recommendation: Transação explícita no checkout e exclusão em cascata (ou bloqueio) decidida no controller (PB-09).

### F-09 [HIGH] Estado global mutável (AP-08)
File: src/utils.js:9-15, 25
Evidence: `let globalCache = {};` / `let totalRevenue = 0;`
Description: `globalCache` é mutado a cada checkout e exportado por referência; `totalRevenue` é exportado como primitivo, logo qualquer consumidor recebe uma cópia congelada em 0 — contador que nunca poderia funcionar.
Impact: Cache compartilhado entre requisições, sem limite nem expiração (vazamento de memória); estado não isolável em teste.
Recommendation: Eliminar o cache global; encapsular em serviço com ciclo de vida explícito, se necessário (PB-08).

### F-10 [HIGH] Configuração de runtime sem override por ambiente (AP-10)
File: src/utils.js:1-7
Evidence: `port: 3000`
Description: Porta, credenciais e endpoints de infraestrutura são literais, sem `process.env` nem validação no boot.
Impact: O mesmo artefato não pode ser promovido entre ambientes; ajuste operacional exige deploy.
Recommendation: `config/settings.js` com `process.env.PORT` e validação de obrigatoriedade na inicialização (PB-01).

### F-11 [MEDIUM] N+1 de queries no relatório financeiro (AP-13)
File: src/AppManager.js:83-127
Evidence: queries dentro de `courses.forEach` → `enrollments.forEach`
Description: Para `C` cursos e `M` matrículas são executadas `1 + C + 2·M` queries (linhas 92, 104, 106). Nenhum `JOIN` ou agregação.
Impact: Latência cresce linearmente com a base de alunos, em endpoint sem paginação.
Recommendation: Query única com `JOIN` e `SUM` filtrado por `status = 'PAID'`, encapsulada em um model de relatório (PB-11).

### F-12 [MEDIUM] Validação de entrada ausente/inconsistente (AP-14)
File: src/AppManager.js:35, 68, 132
Evidence: `if (!u || !e || !cid || !cc) return res.status(400).send("Bad Request");`
Description: Checagem só por truthiness: `c_id: 0` é rejeitado indevidamente e qualquer tipo é aceito — `card: 123` faz `cc.startsWith` lançar `TypeError` na linha 46 e derrubar o processo. `pwd` não é exigido (default fixo na 68), e-mail nunca validado, `id` do DELETE usado cru com resposta de sucesso mesmo sem linha afetada.
Impact: 400 incorretos, crash do processo com payload malformado, exclusões no-op vendidas como sucesso.
Recommendation: Validação centralizada por payload lançando `ValidationError` tratado pelo middleware (PB-12).

### F-13 [MEDIUM] Erros engolidos e tratamento espalhado (AP-15)
File: src/AppManager.js:57, 92, 104, 106, 133
Evidence: callback de `audit_logs` recebe `err`, ignora e responde `res.status(200).json({ msg: "Sucesso" })`
Description: Cinco callbacks recebem `err` e nunca o consultam. Na linha 92, `enrollments` vem `undefined` em caso de erro e `enrollments.length` lança `TypeError` em callback assíncrono, derrubando o processo. Não há middleware de erro Express, e os formatos misturam texto puro com JSON.
Impact: Falhas de persistência vendidas como sucesso, crash do processo, contrato de erro inconsistente.
Recommendation: `errors.js` + `middlewares/errorHandler.js` + `asyncHandler.js`; repositórios que rejeitam em vez de ignorar `err` (PB-13).

### F-14 [MEDIUM] API sqlite3 callback-only aninhada nos handlers (AP-17)
File: src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133
Evidence: `this.db.get("SELECT * FROM courses WHERE id = ? AND active = 1", [cid], (err, course) => {`
Description: As 11 chamadas ao driver usam só o estilo callback, dentro dos handlers, impedindo `async/await` e propagação de erro ao Express. É o padrão legado listado em AP-17 para `Node sqlite3`.
Impact: Erros assíncronos não alcançam o middleware de erro; o código fica preso ao encadeamento manual de F-15.
Recommendation: Promisificar `run`/`get`/`all` em `database/connection.js` (preservando `this.lastID` via wrapper) e escrever repositórios `async` (PB-15).

### F-15 [MEDIUM] Callback hell e contadores manuais de conclusão (AP-18)
File: src/AppManager.js:37-77, 89-127
Evidence: `enrPending--; if (enrPending === 0) { report.push(courseData); coursesPending--; if (coursesPending === 0) res.json(report); }`
Description: O checkout aninha 4 níveis de callbacks (37→40→50→54→57), exigindo o alias `self` porque `function(err)` rebinda `this`. O relatório coordena paralelismo com contadores manuais: a ordem de `report` depende da ordem de conclusão das queries (resposta não determinística) e, se um callback falhar, o contador nunca zera e a requisição fica pendurada.
Impact: Ordenação não determinística, requisições que nunca terminam em erro, fluxo impossível de alterar com segurança.
Recommendation: `async/await` sobre a camada promisificada, contadores substituídos pela query agregada de F-11 (PB-16).

### F-16 [LOW] Magic numbers / magic strings (AP-19)
File: src/AppManager.js:46; src/utils.js:6, 19, 20, 22
Evidence: `cc.startsWith("4") ? "PAID" : "DENIED"` / `for(let i = 0; i < 10000; i++)`
Description: Regra de bandeira como literal `"4"`; status `"PAID"`/`"DENIED"` repetidos sem constante (também em 48 e 108); `10000`, `substring(0, 2)`, `substring(0, 10)` e a porta `3000` sem significado documentado.
Impact: Mudar regra ou status exige caçar literais espalhados, com risco de divergência.
Recommendation: Constantes `PAYMENT_STATUS` e regra de bandeira em `services/paymentGateway.js`; porta em config (PB-17).

### F-17 [LOW] Nomenclatura ruim / enganosa (AP-20)
File: src/AppManager.js:4, 29-33; src/utils.js:17
Evidence: `let u = req.body.usr; let e = req.body.eml; let p = req.body.pwd; let cid = req.body.c_id; let cc = req.body.card;`
Description: Cinco variáveis opacas no handler mais longo — `e` colide conceitualmente com o `err` dos callbacks logo abaixo. `AppManager` não descreve nada, `utils.js` abriga configuração e `badCrypto` admite no nome que não serve. Os nomes de campo do payload são contrato público e serão preservados.
Impact: Revisão do fluxo mais crítico exige esforço desproporcional.
Recommendation: Renomear variáveis internas; nomear módulos pelo papel, mantendo o wire format intacto (PB-18).

### F-18 [LOW] Código morto e exports não utilizados (AP-21)
File: src/AppManager.js:2; src/utils.js:2, 5, 10, 25
Evidence: `const { config, logAndCache, badCrypto, totalRevenue } = require('./utils');`
Description: `totalRevenue` é importado e nunca referenciado; `dbUser`, `dbPass` e `smtpUser` nunca são lidos em lugar algum; `globalCache` e `totalRevenue` são exportados sem consumidor.
Impact: Sugere integrações inexistentes e mantém credenciais no repositório sem função — amplifica F-04.
Recommendation: Remover junto com a dissolução de `utils.js` (PB-18).

### F-19 [LOW] `console.log` usado como logging (AP-22)
File: src/app.js:13; src/utils.js:13
Evidence: `console.log(\`[LOG] Salvando no cache: ${key}\`);`
Description: Logs operacionais sem nível, timestamp ou contexto. O log da linha 45 é tratado em F-02 por vazar dado sensível.
Impact: Logs não filtráveis por severidade nem correlacionáveis por requisição.
Recommendation: Logger com níveis usando a stdlib, sem nova dependência (PB-19).

## Deprecated APIs

| Location | Deprecated API | Modern replacement |
|---|---|---|
| `src/AppManager.js:37, 40, 50, 54, 57, 69, 83, 92, 104, 106, 133` | API callback-only do `sqlite3` aninhada nos handlers | wrapper promisificado (`util.promisify`) + repositórios `async` |

Nenhum outro item de AP-17 se aplica: não há `new Buffer()` (usa `Buffer.from`), `url.parse()`, `fs.exists()`, `crypto.createCipher()`, `util.isArray()`, `body-parser`, `req.param()`, `res.send(status)`, `res.json(status, obj)` nem `app.del()` — o projeto já usa `express.json()` e `app.delete()`.

Verificações que **não** geraram finding: **AP-02** — todas as 11 queries usam placeholders `?`; **AP-12** — não há endpoint de autenticação (a ausência total está em F-03); **AP-16** — a repetição de respostas de erro é resolvida por F-13; **AP-23** — não encontrado.

## Architecture Notes
- **Current architecture:** MONOLITH — `src/AppManager.js` mistura routing, negócio, persistência, apresentação e infra em uma classe de 141 linhas; nenhuma pasta de camada existe.
- **Proposed target:** layout MVC de referência para Node/Express, reestruturação completa (`models/`, `views/`, `controllers/`, `config/`, `middlewares/`, `services/`, `database/`, `createApp.js` como composition root, `src/app.js` preservando `npm start`). `AppManager.js` e `utils.js` serão removidos.

```text
================================
Total: 19 findings
================================

Report saved to /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/reports/audit-project-2.md
Phase 2 complete. Proceed with refactoring (Phase 3)? [y/n]
```

<!-- session_id=006a829f-e740-48a8-9d82-bbcd3e384cb4 turns=16 cost_usd=1.2678285000000002 -->
