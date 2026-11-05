Phase 3. Lendo as referências necessárias.

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/references/refactoring-playbook.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/references/validation-protocol.md

> [tool] Read: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.claude/skills/refactor-arch/scripts/endpoint_smoke.py

> [tool] Bash: lsof -iTCP:3202 -sTCP:LISTEN; echo "exit=$? (1 = porta livre)"

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.refactor-arch/endpoints.json

> [tool] Write: /private/tmp/claude-501/-Users-rff-Documents-projects-personal-mba-challenges-ai-skill-challenge-ecommerce-api-legacy/006a829f-e740-48a8-9d82-bbcd3e384cb4/scrat

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy SCRATCH=/private/tmp/claude-501/-Users-rff-Documents-projects-p

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy python3 .claude/skills/refactor-arch/scripts/endpoint_smoke.py 

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy cat .refactor-arch/baseline.json echo "=== server log ===" SCRA

Baseline capturado (inclusive a evidência ao vivo de F-15: as duas chamadas consecutivas ao relatório devolveram o array em **ordens diferentes**). Aplicando a estratura MONOLITH → reestruturação completa.

```text
Target tree
ecommerce-api-legacy/
├── package.json                        # "npm start" inalterado
├── .env.example                        # variáveis, sem valores reais
└── src/
    ├── app.js                          # ENTRY POINT
    ├── createApp.js                    # COMPOSITION ROOT
    ├── errors.js                        # hierarquia AppError
    ├── config/settings.js              # CONFIG (process.env)
    ├── config/constants.js             # CONFIG (constantes de negócio)
    ├── database/connection.js          # INFRA (promisify + transaction + schema/seed)
    ├── models/userModel.js             # MODEL
    ├── models/courseModel.js           # MODEL
    ├── models/enrollmentModel.js       # MODEL
    ├── models/paymentModel.js          # MODEL
    ├── models/auditLogModel.js         # MODEL
    ├── models/reportModel.js           # MODEL (JOIN único)
    ├── controllers/checkoutController.js   # CONTROLLER
    ├── controllers/reportController.js     # CONTROLLER
    ├── controllers/userController.js       # CONTROLLER
    ├── controllers/validators.js           # CONTROLLER (validação centralizada)
    ├── views/checkoutRoutes.js         # VIEW
    ├── views/reportRoutes.js           # VIEW
    ├── views/userRoutes.js             # VIEW
    ├── middlewares/asyncHandler.js     # MIDDLEWARE
    ├── middlewares/errorHandler.js     # MIDDLEWARE
    ├── middlewares/requireAdminToken.js# MIDDLEWARE
    ├── services/paymentGateway.js      # SERVICE
    ├── services/passwordHasher.js      # SERVICE
    └── services/logger.js              # SERVICE
```

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/config/settings.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/config/constants.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/errors.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/services/logger.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/services/passwordHasher.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/services/paymentGateway.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/database/connection.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/models/userModel.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/models/courseModel.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/models/enrollmentModel.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/models/paymentModel.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/models/auditLogModel.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/models/reportModel.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/controllers/validators.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/controllers/checkoutController.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/controllers/reportController.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/controllers/userController.js

Agora middlewares, views e composition root.

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/middlewares/asyncHandler.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/middlewares/errorHandler.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/middlewares/requireAdminToken.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/views/checkoutRoutes.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/views/reportRoutes.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/views/userRoutes.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/createApp.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/src/app.js

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/.env.example

> [tool] Bash: rm -f src/AppManager.js src/utils.js && find src -type f | sort

Agora validação: syntax check, boot e smoke.

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy for f in $(find src -name '*.js'); do node --check "$f" || echo

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy SCRATCH=/private/tmp/claude-501/-Users-rff-Documents-projects-p

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy python3 .claude/skills/refactor-arch/scripts/endpoint_smoke.py 

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy python3 - <<'PY' import json b={r["name"]:r for r in json.load(

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy python3 - <<'PY' import json b=[r for r in json.load(open(".ref

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy python3 .claude/skills/refactor-arch/scripts/scan_antipatterns.

> [tool] Write: /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy/README.md

> [tool] Bash: cd /Users/rff/Documents/projects/personal/mba-challenges/ai-skill-challenge/ecommerce-api-legacy kill 12416 2>/dev/null; sleep 1 lsof -iTCP:3202 -sTCP:LISTEN &&

```text
================================
PHASE 3: REFACTORING COMPLETE
================================
## New Project Structure
ecommerce-api-legacy/
├── package.json                          # inalterado — `npm start` preserva o comando original
├── .env.example                          # NOVO — variáveis de ambiente, sem valores reais
├── README.md                             # atualizado: config por env + header admin
└── src/
    ├── app.js                            # ENTRY POINT — chama a factory e faz listen
    ├── createApp.js                      # COMPOSITION ROOT — única wiring de dependências
    ├── errors.js                          # ERRORS — AppError/Validation/PaymentDeclined/Forbidden/NotFound
    ├── config/
    │   ├── settings.js                   # CONFIG — process.env + validação em produção
    │   └── constants.js                  # CONFIG — constantes de negócio e mensagens do contrato
    ├── database/
    │   └── connection.js                 # INFRA — sqlite3 promisificado, transações, schema + seed
    ├── models/                           # MODEL — persistência, SQL parametrizado, sem Express
    │   ├── userModel.js                  #   inclui deleteWithDependents (cascata transacional)
    │   ├── courseModel.js
    │   ├── enrollmentModel.js
    │   ├── paymentModel.js
    │   ├── auditLogModel.js
    │   └── reportModel.js                #   JOIN único do relatório financeiro
    ├── controllers/                      # CONTROLLER — casos de uso, sem req/res
    │   ├── checkoutController.js
    │   ├── reportController.js
    │   ├── userController.js
    │   └── validators.js                 #   validação centralizada de payload
    ├── views/                            # VIEW — express.Router(), HTTP in/out apenas
    │   ├── checkoutRoutes.js
    │   ├── reportRoutes.js
    │   └── userRoutes.js
    ├── middlewares/                      # MIDDLEWARE
    │   ├── errorHandler.js               #   (err, req, res, next) — único tradutor erro→HTTP
    │   ├── asyncHandler.js
    │   └── requireAdminToken.js          #   guard das rotas admin/destrutiva
    └── services/                         # SERVICE — infraestrutura externa
        ├── paymentGateway.js             #   regra de aprovação + log mascarado
        ├── passwordHasher.js             #   crypto.scrypt salgado (stdlib)
        └── logger.js                     #   logger com níveis (stdlib)

Removidos: src/AppManager.js (god class, 141 linhas), src/utils.js (config + estado global).
25 arquivos, ~800 linhas. Nenhuma dependência nova: só `express`, `sqlite3` e a stdlib.

## Findings Resolution
F-01 [CRITICAL] God class concentrando toda a aplicação — FIXED: AppManager.js deletado; responsabilidades separadas em 6 models, 3 controllers + validators, 3 views, 3 middlewares, 3 services, config e database; createApp.js é o único composition root.
F-02 [CRITICAL] Número de cartão e chave de pagamento em log — FIXED: log movido para services/paymentGateway.js, que registra apenas `****4444` (maskCardNumber) e um booleano `gatewayConfigured`; o PAN completo e a chave nunca são serializados.
F-03 [CRITICAL] Endpoints administrativo e destrutivo sem autenticação — FIXED: middlewares/requireAdminToken.js exige o header `X-Admin-Token` comparado com `crypto.timingSafeEqual` contra `ADMIN_TOKEN`; aplicado em `GET /api/admin/financial-report` e `DELETE /api/users/:id`; sem a variável configurada, ambas negam (padrão seguro).
F-04 [CRITICAL] Credenciais e chave de produção hardcoded — FIXED: utils.js deletado; config/settings.js lê tudo de `process.env` com defaults de desenvolvimento; `dbUser`/`dbPass`/`smtpUser` (código morto) eliminados; `.env.example` adicionado. As chaves já expostas no histórico do Git precisam ser rotacionadas fora do código.
F-05 [CRITICAL] Armazenamento inseguro de senhas — FIXED: `badCrypto` removido; services/passwordHasher.js usa `crypto.scrypt` com sal de 16 bytes por usuário, formato `scrypt$salt$key`, verificação com `timingSafeEqual`; o seed passa pela mesma função; o default `"123456"` foi eliminado — senha é obrigatória para criar usuário.
F-06 [HIGH] Regra de negócio dentro das rotas — FIXED: as 3 views somam 12 linhas de handler; a decisão de pagamento está em paymentGateway.js, o fluxo de checkout em checkoutController.js e as queries nos models.
F-07 [HIGH] Acoplamento forte, sem injeção de dependência — FIXED: `createConnection(settings)` cria a conexão e ela é injetada nos models; models → controllers → views são injetados em createApp.js; nada é instanciado no escopo de módulo.
F-08 [HIGH] Escrita multi-passo sem transação e exclusão com órfãos — FIXED: `db.transaction()` (BEGIN IMMEDIATE/COMMIT/ROLLBACK, com fila para serializar transações na conexão compartilhada) envolve matrícula+pagamento+auditoria; `deleteWithDependents` apaga pagamentos → matrículas → usuário atomicamente. Verificado em execução: após o DELETE, o curso Docker devolve `revenue: 0, students: []` em vez de linhas órfãs.
F-09 [HIGH] Estado global mutável — FIXED: `globalCache` e `totalRevenue` removidos (não tinham leitor); o efeito observável virou `logger.info('checkout.completed', ...)`.
F-10 [HIGH] Configuração de runtime sem override por ambiente — FIXED: `PORT`, `DATABASE_FILE`, `LOG_LEVEL`, `ADMIN_TOKEN`, `PAYMENT_GATEWAY_KEY` vêm do ambiente; `assertProductionSettings()` derruba o boot em `NODE_ENV=production` sem token/chave.
F-11 [MEDIUM] N+1 de queries no relatório financeiro — FIXED: `1 + C + 2·M` queries → 1 query com três `LEFT JOIN` em reportModel.js; a agregação de receita (só `PAID`) ficou no reportController. Conteúdo do relatório verificado idêntico ao baseline.
F-12 [MEDIUM] Validação de entrada ausente/inconsistente — FIXED: controllers/validators.js valida presença, tipo e formato (e-mail por regex, `c_id` inteiro, `card` 12–19 dígitos com normalização de espaços/hífens), eliminando o `TypeError` de `cc.startsWith` e o falso 400 para `c_id: 0`; `validateUserId` rejeita id não-inteiro. DEFERIDO dentro deste finding: `DELETE` de usuário inexistente continua devolvendo 200 (preservação de contrato — virar 404 seria mudança sem motivação de segurança).
F-13 [MEDIUM] Erros engolidos e tratamento espalhado — FIXED: errors.js + middlewares/errorHandler.js como único tradutor erro→HTTP; asyncHandler encaminha rejeições (Express 4 não captura); nenhum `err` é ignorado — a camada promisificada rejeita; erros inesperados logam stack e devolvem 500 genérico.
F-14 [MEDIUM] API sqlite3 callback-only aninhada nos handlers — FIXED: `util.promisify` em database/connection.js para `get`/`all`/`exec`/`close` e wrapper manual em `run` preservando `lastID`/`changes`; todos os repositórios são `async`.
F-15 [MEDIUM] Callback hell e contadores manuais de conclusão — FIXED: 4 níveis de callbacks e o alias `self` substituídos por `async/await`; `coursesPending`/`enrPending` eliminados pela query agregada; a ordenação do relatório passou a ser determinística (`ORDER BY c.id, e.id, p.id`).
F-16 [LOW] Magic numbers / magic strings — FIXED: `APPROVED_CARD_PREFIX`, `PAYMENT_STATUS`, `ADMIN_TOKEN_HEADER`, `UNKNOWN_STUDENT` e `MESSAGES` em config/constants.js; parâmetros do scrypt nomeados em passwordHasher.js; porta em config.
F-17 [LOW] Nomenclatura ruim / enganosa — FIXED: `u/e/p/cid/cc` → `name/email/password/courseId/cardNumber` via destructuring renomeado no validator, preservando os nomes de campo do wire (`usr`, `eml`, `pwd`, `c_id`, `card`); `AppManager`/`utils`/`badCrypto` substituídos por módulos nomeados pelo papel.
F-18 [LOW] Código morto e exports não utilizados — FIXED: `totalRevenue`, `globalCache`, `dbUser`, `dbPass`, `smtpUser` eliminados junto com utils.js.
F-19 [LOW] `console.log` usado como logging — FIXED: services/logger.js com níveis (`error`/`warn`/`info`/`debug`), saída JSON com timestamp, nível via `LOG_LEVEL`; nenhum `console.log` resta na aplicação.

## Intentional Behaviour Changes
- `GET /api/admin/financial-report` sem `X-Admin-Token`: era 200 com o faturamento e a lista de alunos; agora 403 `"Acesso administrativo negado"` (corrige F-03).
- `DELETE /api/users/:id` sem `X-Admin-Token`: era 200 e apagava o usuário; agora 403 sem efeito (corrige F-03).
- `DELETE /api/users/:id` com token: continua 200 text/plain, mas o texto passou de `"Usuário deletado, mas as matrículas e pagamentos ficaram sujos no banco."` para `"Usuário deletado, junto com suas matrículas e pagamentos."` — a frase anterior descrevia o bug corrigido em F-08.
- `POST /api/checkout` com e-mail novo e sem `pwd`: era 200 criando o usuário com a senha padrão `"123456"`; agora 400 `"Bad Request"` (corrige F-05).
- `POST /api/checkout` com `card` não numérico: era 500/crash do processo (`TypeError` em `cc.startsWith`); agora 400 `"Bad Request"` (corrige F-12).
- `GET /api/admin/financial-report`: a ordem do array deixou de ser não determinística (duas chamadas consecutivas ao app original devolveram ordens diferentes) e passou a ser por id de curso. Conteúdo verificado idêntico ao baseline.
- Comportamento preservado de propósito: o cadastro implícito no checkout continua criando o usuário antes da decisão do pagamento, e o `DELETE` de usuário inexistente continua devolvendo 200.

## Validation
  ✓ Application boots without errors (`PORT=3202 ADMIN_TOKEN=... npm start` → `server.started`, sem stack trace; `node --check` OK nos 25 arquivos)
  ✓ All endpoints respond correctly (9/9 smoke requests, exit 0; corpos idênticos ao baseline exceto as mudanças intencionais acima)
  ✓ No catalog anti-patterns remaining (scanner: 2 hits, all reviewed — ambos falsos positivos: `ADMIN_TOKEN_HEADER: 'X-Admin-Token'` é o nome do header HTTP, não um segredo; o INSERT em loop em `connection.js:77` é o seed de 2 cursos fixos dentro de uma transação no boot, não um N+1 por requisição)
================================
```

Processo encerrado, porta 3202 liberada, sem artefatos de runtime. Evidências mantidas em `.refactor-arch/` (`endpoints.json`, `baseline.json`, `after.json`).

Uma pendência fora do código: a chave `pk_live_1234567890abcdef` e a senha `senha_super_secreta_prod_123` permanecem no histórico do Git — removê-las do fonte não as invalida, então convém rotacioná-las.

<!-- session_id=006a829f-e740-48a8-9d82-bbcd3e384cb4 turns=45 cost_usd=3.8675070000000007 -->
