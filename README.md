# Refatoração Arquitetural Automatizada com Skills — `refactor-arch`

Entrega do desafio **"Criação de Skills — Refatoração Arquitetural Automatizada"** (MBA — módulo
Desenvolvimento de Software e Aplicações com IA). O enunciado original está em
[`CHALLENGE.md`](CHALLENGE.md).

A skill [`refactor-arch`](code-smells-project/.claude/skills/refactor-arch/SKILL.md) para
**Claude Code** audita qualquer backend, gera um relatório de severidades com `arquivo:linha` e,
**após confirmação humana**, refatora o projeto para MVC e valida que a aplicação continua de pé.
Ela foi executada sem alterações nos três projetos legados: 2 em Python/Flask e 1 em Node.js/Express.

| | code-smells-project | ecommerce-api-legacy | task-manager-api |
|---|---|---|---|
| Stack | Python + Flask 3.1 | Node.js + Express 4 | Python + Flask 3.0 + SQLAlchemy |
| Findings (C/H/M/L) | 7 / 6 / 5 / 5 | 5 / 5 / 5 / 4 | 7 / 7 / 5 / 5 |
| Relatório | [audit-project-1](reports/audit-project-1.md) | [audit-project-2](reports/audit-project-2.md) | [audit-project-3](reports/audit-project-3.md) |
| App após refatoração | ✅ boot + 34/34 endpoints | ✅ boot + 10/10 endpoints | ✅ boot + 45/45 endpoints |

### Mapa do repositório

```text
├── README.md                       # este documento
├── CHALLENGE.md                    # enunciado original do desafio
├── code-smells-project/            # Projeto 1 — refatorado (skill em .claude/skills/refactor-arch/)
├── ecommerce-api-legacy/           # Projeto 2 — refatorado (cópia da skill)
├── task-manager-api/               # Projeto 3 — refatorado (cópia da skill)
│   └── .refactor-arch/             # (em cada projeto) spec, baseline e resultado da validação da skill
├── reports/audit-project-{1,2,3}.md   # saída da Fase 2
├── scripts/                        # validação independente: smoke.py, specs/, baseline/, extract_transcript.py
└── docs/
    ├── evidence/                   # transcrições das execuções e logs de smoke (antes/depois)
    └── iterations/                 # relatório da iteração 1 da skill (antes do ajuste)
```

## A) Análise Manual

Análise feita lendo todo o código dos três projetos **antes** de escrever a skill, e confirmada
executando os endpoints originais (`scripts/smoke.py`, saídas em `docs/evidence/project-*-baseline.txt`).
A severidade segue a escala do desafio (CRITICAL → LOW, baseada em MVC/SOLID).

### Projeto 1 — `code-smells-project` (Python 3 / Flask 3.1.1 — API de E-commerce)

Monólito em 4 arquivos (`app.py`, `controllers.py`, `models.py`, `database.py`, ~780 linhas), sem
camadas: SQL, regras de negócio, roteamento e configuração misturados.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **SQL Injection** em praticamente todas as queries (concatenação de strings) | `models.py:28, 48-49, 58-60, 68, 92, 110, 127-128, 140, 149-150, 155-165, 174, 188, 192, 220, 224, 280, 291-297` | Confirmado no baseline: `POST /login` com email `admin@loja.com' --` **autentica sem senha** (200) e `GET /produtos/busca?q=' OR 1=1 --` derruba a query (500). Leitura/escrita arbitrária do banco. |
| 2 | CRITICAL | **Endpoint que executa SQL arbitrário e reset do banco sem autenticação** | `app.py:47-57` (`/admin/reset-db`), `app.py:59-78` (`/admin/query`) | Qualquer cliente apaga todas as tabelas ou executa `DROP`/`UPDATE` livremente. |
| 3 | CRITICAL | **Credenciais hardcoded e vazadas na API** | `app.py:7` (`SECRET_KEY`), `controllers.py:285-289` (`/health` devolve `secret_key`, `db_path`, `debug`) | A chave que assina sessões está no código **e** é publicada por um endpoint público. |
| 4 | CRITICAL | **Senhas em texto puro**, comparadas no SQL e devolvidas pela API | `database.py:76-78`, `models.py:109-111, 126-129`, `models.py:83, 99` (`"senha": row["senha"]`) | `GET /usuarios` lista as senhas de todos os usuários. |
| 5 | CRITICAL | **God module** — `models.py` concentra CRUD, regras e relatórios de 4 domínios; `app.py` mistura roteamento, admin e boot | `models.py:1-314`, `app.py:1-88` | Impossível testar isoladamente; qualquer mudança afeta tudo (viola SRP). |
| 6 | HIGH | **Debug ligado e bind em todas as interfaces** | `app.py:8`, `app.py:88` | O debugger do Werkzeug permite execução remota de código se exposto. |
| 7 | HIGH | **Estado global mutável**: conexão SQLite global compartilhada entre threads | `database.py:4-11` (`global db_connection`, `check_same_thread=False`) | Acoplamento forte (sem DI), condições de corrida, impossível trocar o banco em testes. |
| 8 | HIGH | **Regra de negócio e efeitos colaterais fora do lugar**: faixas de desconto no "model", notificações fake no controller, criação de pedido sem transação explícita | `models.py:256-262`, `models.py:133-169`, `controllers.py:208-210, 247-250` | Mistura de camadas; pedido pode ficar inconsistente se uma das escritas falhar. |
| 9 | MEDIUM | **N+1 queries** ao listar pedidos (1 query por pedido + 1 por item) | `models.py:171-201`, `models.py:203-233` | Cresce linearmente com o volume; duas funções quase idênticas. |
| 10 | MEDIUM | **Tratamento de erro duplicado e vazando internals**: `except Exception as e: return jsonify({"erro": str(e)}), 500` em todos os handlers | `controllers.py:10-12, 21-22, 60-62, 95-96, ...` (18 ocorrências) | Sem handler central; mensagem de exceção (SQL, stack) vai para o cliente. |
| 11 | MEDIUM | **Validação ausente/inconsistente** | `controllers.py:43-50` (`preco` string → 500), `controllers.py:81-90` (update não valida categoria/nome), `controllers.py:169-170, 239-240` (`dados` `None` → 500) | Entradas inválidas viram erro 500 em vez de 400. |
| 12 | MEDIUM | **Duplicação** do mapeamento row→dict e das listagens de pedidos | `models.py:12-21, 31-40, 304-313`, `models.py:171-233` | Manutenção multiplicada; bugs corrigidos em um lugar e não no outro. |
| 13 | LOW | **Magic numbers/strings** (faixas de desconto, limites de nome, listas de status/categorias inline) | `models.py:257-262`, `controllers.py:47-52, 242` | Regras de negócio escondidas em literais. |
| 14 | LOW | **`print` como log** | `controllers.py:8, 57, 106, 161, 179, 182, 208-210, 219`, `app.py:56, 83-86` | Sem níveis, sem destino configurável; loga e-mails de usuários. |
| 15 | LOW | **Imports não usados / nomes ruins** | `models.py:2` (`sqlite3`), `database.py:2` (`os`), parâmetro `id` sombreando builtin (`models.py:24, 54, 65, 89`) | Ruído e confusão. |

APIs deprecated: nenhuma relevante encontrada para Python 3.13 + Flask 3.1.

### Projeto 2 — `ecommerce-api-legacy` (Node.js / Express 4.18 — LMS com checkout)

Três arquivos (`src/app.js`, `src/AppManager.js`, `src/utils.js`, ~180 linhas), SQLite em memória.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **Credenciais hardcoded** (senha do banco, chave *live* do gateway de pagamento, usuário SMTP) | `src/utils.js:1-7` | Segredos de produção versionados no Git. |
| 2 | CRITICAL | **Número do cartão e chave do gateway impressos no log** | `src/AppManager.js:45` | Violação direta de PCI-DSS; vazamento em qualquer agregador de logs. |
| 3 | CRITICAL | **"Criptografia" caseira de senha** (base64 truncado repetido) e senha padrão `123456` | `src/utils.js:17-23`, `src/AppManager.js:68`, seed com senha pura `src/AppManager.js:18` | Hash determinístico, sem sal, com colisões triviais — equivalente a texto puro. |
| 4 | CRITICAL | **God class `AppManager`**: conexão, schema, seed, rotas, regra de pagamento e relatório na mesma classe | `src/AppManager.js:1-141` | Nenhuma separação de camadas; impossível testar o checkout sem HTTP + banco. |
| 5 | HIGH | **Estado global mutável** exportado (`globalCache`, `totalRevenue`) | `src/utils.js:9-10, 25` | `totalRevenue` é exportado por valor (nunca atualiza) — bug latente; cache global compartilhado entre requests. |
| 6 | HIGH | **Integridade referencial quebrada e escrita sem transação**: delete de usuário deixa matrículas/pagamentos órfãos; checkout grava matrícula + pagamento + auditoria sem transação | `src/AppManager.js:131-137`, `src/AppManager.js:50-61` | A própria resposta admite "ficaram sujos no banco"; falha no meio deixa matrícula sem pagamento. |
| 7 | HIGH | **Rotas administrativas sem autenticação** (relatório financeiro com nomes e valores, delete de usuário) | `src/AppManager.js:80`, `src/AppManager.js:131` | Qualquer um lê dados financeiros ou apaga usuários. |
| 8 | HIGH | **Acoplamento sem DI**: a classe cria o próprio banco; regra de aprovação de pagamento dentro da rota | `src/AppManager.js:5-8`, `src/AppManager.js:46` | Impossível injetar banco/gateway de teste. |
| 9 | MEDIUM | **N+1 no relatório financeiro** (1 + C + 2·E queries) com contadores manuais | `src/AppManager.js:83-128` | Escala mal e é frágil (contadores `pending--`). |
| 10 | MEDIUM | **Callback hell** (5 níveis no checkout) | `src/AppManager.js:37-77`, `src/AppManager.js:83-128` | Legibilidade e tratamento de erro ruins. |
| 11 | MEDIUM | **Erros ignorados** (callbacks não checam `err`; sem middleware de erro) | `src/AppManager.js:57, 92, 104, 106, 133` | `enrollments.length` explode se a query falhar; delete responde sucesso mesmo com erro. |
| 12 | MEDIUM | **Validação insuficiente** (senha opcional, `c_id`/cartão sem formato) | `src/AppManager.js:29-35` | Dados inválidos chegam ao banco/gateway. |
| 13 | LOW | **Nomes crípticos** (`u`, `e`, `p`, `cid`, `cc`, `badCrypto`, `AppManager`, config em `utils.js`) | `src/AppManager.js:29-33`, `src/utils.js:17` | Código difícil de ler. |
| 14 | LOW | **Magic numbers/strings** (`10000`, prefixo `"4"`, `'PAID'`/`'DENIED'`, porta `3000`) | `src/utils.js:6, 19`, `src/AppManager.js:46` | Regras implícitas. |
| 15 | LOW | **`console.log` como log** e import não usado (`totalRevenue`) | `src/utils.js:13`, `src/app.js:13`, `src/AppManager.js:2` | Sem níveis, sem controle. |

APIs deprecated: nenhuma no código (Express 4 + `express.json()` já é o padrão moderno); o estilo
callback do `sqlite3` é legado e foi tratado via promisify.

### Projeto 3 — `task-manager-api` (Python 3 / Flask 3.0 + Flask-SQLAlchemy 3.1 — Task Manager)

Já possui `models/`, `routes/`, `services/`, `utils/` (~1.150 linhas), mas as rotas concentram regra
de negócio e queries, não há controllers, config nem tratamento de erro central.

| # | Severidade | Problema | Local | Por que é relevante |
|---|---|---|---|---|
| 1 | CRITICAL | **Segredos hardcoded** (`SECRET_KEY`, senha SMTP) | `app.py:13`, `services/notification_service.py:7-10` | Credenciais versionadas. |
| 2 | CRITICAL | **Senhas com MD5 sem sal** | `models/user.py:27-32` | MD5 é quebrado por rainbow tables em segundos. |
| 3 | CRITICAL | **Hash da senha devolvido pela API** (`to_dict` inclui `password`) | `models/user.py:16-25` → `routes/user_routes.py:33, 85, 129, 209` | Vazamento em `GET /users/<id>`, `POST/PUT /users` e no `/login`. |
| 4 | HIGH | **Token fake e previsível** (`'fake-jwt-token-' + id`) e nenhuma rota protegida | `routes/user_routes.py:207-211` | Qualquer um forja um "token"; deletar usuários não exige autenticação. |
| 5 | HIGH | **Regra de negócio e queries nas rotas** (sem camada de controller) | `routes/task_routes.py:11-63`, `routes/report_routes.py:12-101`, `routes/user_routes.py:134-151` | Rotas de 30–90 linhas; difícil testar e reutilizar. |
| 6 | HIGH | **Debug ligado + `0.0.0.0`** | `app.py:34` | Debugger remoto exposto. |
| 7 | HIGH | **Sem app factory / composição no import** (`db.create_all()` no import, seed importa o app) | `app.py:9-31`, `seed.py:2` | Acoplamento: impossível criar app com outra config para testes. |
| 8 | MEDIUM | **N+1 queries** | `routes/task_routes.py:41-57`, `routes/user_routes.py:22`, `routes/report_routes.py:19-28, 55-56, 161-163` | `GET /tasks` faz 1 + 2N queries; o relatório faz 9 COUNTs + 1 por usuário. |
| 9 | MEDIUM | **APIs deprecated**: `datetime.utcnow()` (deprecated no Python 3.12+, ~30 usos) e `Model.query.get()` (API legada no SQLAlchemy 2.0, 16 usos) | ex.: `models/task.py:15-16, 52`, `routes/task_routes.py:31, 42, 51, 67`, `routes/report_routes.py:35, 105` | Emitem `DeprecationWarning` (visível ao rodar o seed); serão removidas. Substituir por `datetime.now(timezone.utc)` e `db.session.get()`. |
| 10 | MEDIUM | **Lógica duplicada**: regra de "atrasada" copiada 6× apesar de existir `Task.is_overdue()`; validação duplicada e `utils/helpers.process_task_data` nunca usado | `routes/task_routes.py:30-39, 71-80, 283-287`, `routes/user_routes.py:171-180`, `routes/report_routes.py:33-43, 132-135`, `models/task.py:50-60` | Divergência de regras ao longo do tempo. |
| 11 | MEDIUM | **`except:` genérico e sem handler central** | `routes/task_routes.py:62, 137, 204, 236`, `routes/user_routes.py:130, 149`, `routes/report_routes.py:186, 207, 221` | Engole erros (inclusive `KeyboardInterrupt`); `PUT /categories/<id>` sem corpo gera 500. |
| 12 | MEDIUM | **Validação de tipos ausente** (`priority` string → 500; `color` não validada apesar de `is_valid_color` existir) | `routes/task_routes.py:113, 182`, `routes/report_routes.py:180` | 500 em vez de 400. |
| 13 | LOW | **Imports não usados** | `app.py:7`, `routes/task_routes.py:7`, `routes/user_routes.py:6`, `routes/report_routes.py:8`, `models/task.py:3`, `utils/helpers.py:3-7` | Ruído. |
| 14 | LOW | **Magic numbers/strings** (status, roles, 1–5, 3/200, 4, 7 dias) inline, enquanto constantes em `utils/helpers.py:110-116` não são usadas | `routes/task_routes.py:96-114`, `routes/user_routes.py:64, 71, 115, 120`, `routes/report_routes.py:45` | Regras espalhadas. |
| 15 | LOW | **Booleanos verbosos / `type(x) == list` / `print` como log** | `models/task.py:38-60`, `models/user.py:34-38`, `routes/task_routes.py:141, 149, 210` | Legibilidade. |

## B) Construção da Skill

### Estrutura

```text
.claude/skills/refactor-arch/
├── SKILL.md                              # o "prompt": 3 fases, regras, gate de confirmação, formatos de saída
├── references/
│   ├── project-analysis.md               # Análise de projeto (Fase 1)
│   ├── anti-patterns-catalog.md          # Catálogo de anti-patterns (Fase 2)
│   ├── report-template.md                # Template do relatório (Fase 2)
│   ├── mvc-guidelines.md                 # Guidelines de arquitetura MVC (Fases 2 e 3)
│   ├── refactoring-playbook.md           # Playbook de refatoração (Fase 3)
│   └── validation-protocol.md            # Protocolo de validação (Fase 3)
└── scripts/
    ├── scan_antipatterns.py              # scanner regex de candidatos (stdlib only)
    └── endpoint_smoke.py                 # smoke test de endpoints com baseline/compare (stdlib only)
```

| Área de conhecimento exigida | Arquivo |
|---|---|
| Análise de projeto | `references/project-analysis.md` — tabelas de detecção de linguagem, framework, banco, entry point, domínio e classificação `MONOLITH` / `PARTIALLY LAYERED` / `LAYERED` |
| Catálogo de anti-patterns | `references/anti-patterns-catalog.md` — 23 anti-patterns (6 CRITICAL, 6 HIGH, 6 MEDIUM, 5 LOW) com sinais de detecção por linguagem |
| Template de relatório | `references/report-template.md` — formato do relatório, regras de ordenação/contagem e exemplo bom × ruim |
| Guidelines de arquitetura | `references/mvc-guidelines.md` — responsabilidades MUST / MUST NOT por camada, layouts Flask e Express, estratégia por nível de organização |
| Playbook de refatoração | `references/refactoring-playbook.md` — 19 transformações (PB-01…PB-19) com código antes/depois em Python e JavaScript |

### Decisões de design

1. **`SKILL.md` curto e procedural; conhecimento nos references.** O `SKILL.md` só diz *o que fazer
   e em que ordem*, e manda ler cada reference **no início da fase que precisa dele** (progressive
   disclosure). Isso mantém o contexto enxuto: a Fase 1 não carrega o playbook.
2. **Formatos de saída fixos.** Os blocos `PHASE 1`, `ARCHITECTURE AUDIT REPORT` e `PHASE 3` estão
   escritos literalmente no `SKILL.md` / template, para que a saída seja comparável entre projetos.
3. **Gate de confirmação explícito.** A Fase 2 termina com `Proceed with refactoring (Phase 3)? [y/n]`
   e um `STOP` em negrito; o único arquivo que a skill pode escrever antes da resposta é o próprio
   relatório. Qualquer resposta diferente de "sim" encerra.
4. **`disable-model-invocation: true` + `allowed-tools`.** A skill reescreve o projeto inteiro, então
   só roda quando chamada explicitamente via `/refactor-arch`; `allowed-tools` libera as ferramentas
   necessárias (inclusive em modo headless `claude -p`).
5. **Argumentos.** `/refactor-arch [caminho-do-relatório] [--audit-only]` — usado para gravar direto em
   `reports/audit-project-N.md`; `--audit-only` permite usar só a auditoria.
6. **Evidência acima de opinião.** Toda finding exige `arquivo:linha` relido, um trecho de `Evidence`,
   o ID do catálogo (`AP-xx`) e o padrão de correção (`PB-xx`) — rastreabilidade catálogo → relatório
   → playbook.
7. **Validação por baseline (characterization test).** Antes de alterar qualquer arquivo, a Fase 3
   sobe a aplicação **original**, grava as respostas de todos os endpoints (`.refactor-arch/baseline.json`)
   e, depois da refatoração, roda o mesmo spec com `--compare`. Status diferentes do baseline falham;
   chaves JSON que mudaram são listadas e precisam ser justificadas como correção de segurança.
   O campo `expect` permite fixar o status *correto* quando o baseline estava errado (ex.: login com
   SQL injection deve virar 401).
8. **Scripts determinísticos só com a stdlib.** O scanner dá candidatos rápidos com linha exata
   (e é rodado de novo no fim para o "zero anti-patterns remaining"); o agente confirma ou descarta cada
   hit lendo o código. Problemas estruturais (God class, regra de negócio na rota, falta de transação,
   duplicação) só são achados lendo — o `SKILL.md` exige ler todos os arquivos por inteiro.

### Anti-patterns do catálogo e por quê

| ID | Anti-pattern | Sev. | Motivo da inclusão |
|---|---|---|---|
| AP-01 | Credenciais/segredos hardcoded | CRITICAL | Presente nos 3 projetos (`SECRET_KEY`, `pk_live_…`, senha SMTP) |
| AP-02 | SQL Injection | CRITICAL | 24 queries concatenadas no projeto 1, com bypass de login comprovado |
| AP-03 | God class / God module | CRITICAL | `models.py` (P1) e `AppManager` (P2) |
| AP-04 | Armazenamento inseguro de senha | CRITICAL | texto puro (P1), base64 caseiro (P2), MD5 (P3) |
| AP-05 | Endpoints admin/destrutivos sem proteção | CRITICAL | `/admin/query` executa SQL arbitrário (P1) |
| AP-06 | Exposição de dados sensíveis | CRITICAL/HIGH | `/health` com secret, senha em respostas, cartão no log |
| AP-07 | Regra de negócio na rota | HIGH | violação central de MVC (P1, P3) |
| AP-08 | Estado global mutável | HIGH | conexão global (P1), `globalCache` (P2) |
| AP-09 | Acoplamento sem DI | HIGH | ausência de app factory nos 3 |
| AP-10 | Config de runtime insegura | HIGH | `debug=True` + `0.0.0.0` |
| AP-11 | Falta de transação / integridade | HIGH | checkout e delete órfão (P2), pedido (P1) |
| AP-12 | Token fake/previsível | HIGH | `fake-jwt-token-<id>` (P3) |
| AP-13 | N+1 queries | MEDIUM | listagens de pedidos, relatório financeiro, `/tasks` |
| AP-14 | Validação ausente | MEDIUM | 500 em vez de 400 em vários endpoints |
| AP-15 | Erros espalhados/engolidos | MEDIUM | `except:` e `str(e)` para o cliente |
| AP-16 | Duplicação | MEDIUM | regra de "overdue" copiada 6× (P3) |
| AP-17 | **APIs deprecated** | MEDIUM | `datetime.utcnow()`, `Query.get()`, `new Buffer()`, `body-parser`… com tabela de substitutos por stack |
| AP-18 | Callback hell | MEDIUM | checkout com 5 níveis (P2) |
| AP-19 | Magic numbers/strings | LOW | faixas de desconto, prefixo de cartão |
| AP-20 | Nomes ruins | LOW | `u`, `e`, `cc`, `badCrypto` |
| AP-21 | Imports/código morto | LOW | `import os, sys, json` não usados |
| AP-22 | `print`/`console.log` como log | LOW | todos os projetos |
| AP-23 | Booleanos verbosos | LOW | `if x: return True else: return False` |

### Como a skill é agnóstica de tecnologia

- O `SKILL.md` não menciona Flask nem Express: ele manda **detectar a stack primeiro** e usar só as
  linhas correspondentes das tabelas por linguagem dos references.
- Os sinais de detecção do catálogo e os exemplos do playbook vêm em Python **e** JavaScript (com
  dicas para FastAPI, Django, Go, Spring etc. na análise), e a tabela de deprecated APIs é por stack.
- As camadas MVC são definidas por **responsabilidade** (MUST / MUST NOT), com layouts de referência
  por stack e uma **estratégia por nível de organização**: reestruturação completa para monólitos,
  evolução *in place* para projetos parcialmente organizados (mantendo `routes/` como camada View),
  correções pontuais para projetos já em camadas.
- Os scripts usam só a biblioteca padrão do Python e falam HTTP, então validam qualquer backend.
- Prova prática: a mesma pasta, copiada sem alterações, rodou nos 3 projetos (2 Flask com níveis de
  organização diferentes + 1 Express).

### Desafios encontrados e como resolvi

| Desafio | Solução |
|---|---|
| **Iteração 1:** o relatório do projeto 1 propôs `repositories/ schemas/ infra/` em vez de MVC, porque a Fase 2 não lia as guidelines | A Fase 2 passou a ler `mvc-guidelines.md` e o `SKILL.md` exige as pastas `models/`, `views/`/`routes/`, `controllers/`, `config/`, `middlewares/` (relatório da iteração 1 guardado em `docs/iterations/`) |
| Scanner perdia `app.config["SECRET_KEY"] = "..."` e marcava qualquer string "admin" como rota admin | Ajuste das regex (`\]?\s*[:=]`, AP-05 só em declarações de rota), testadas nos 3 projetos |
| Porta 5000 ocupada pelo AirPlay do macOS e 3000 por outro processo | O protocolo de validação manda checar a porta com `lsof` e sobrescrever via `--port`/`PORT`; para o Express original (porta fixa) uso de um *harness* que importa os módulos originais |
| Como provar que "endpoints continuam respondendo" sem testes no projeto | Baseline gravado **antes** da refatoração + `--compare` depois; mudanças intencionais são listadas |
| Correções de segurança mudam respostas (senha não é mais devolvida, admin exige token) | Regra 4 do `SKILL.md`: só mudanças que fecham falhas da Fase 2, sempre listadas em "Intentional Behaviour Changes" |
| `datetime.utcnow()` → `datetime.now(timezone.utc)` quebra comparações com colunas *naive* do SQLite | Playbook PB-15 orienta um helper `utcnow_naive()` |
| Confirmação da Fase 2 em modo não interativo | Execução em duas chamadas: `claude -p "/refactor-arch …"` para na pergunta; `claude -p "y" --resume <session>` continua a mesma sessão |

## C) Resultados

A skill foi executada com o Claude Code 2.1.236 em modo headless, em **duas chamadas por projeto na
mesma sessão**: `claude -p "/refactor-arch ../reports/audit-project-N.md"` (Fases 1–2, que param na
pergunta de confirmação) e, após revisar o relatório, `claude -p "y …" --resume <sessão>` (Fase 3).
As transcrições completas (texto + cada chamada de ferramenta) estão em `docs/evidence/`.

### Resumo das auditorias

| Projeto | Stack detectada | Arquitetura (Fase 1) | CRITICAL | HIGH | MEDIUM | LOW | Total |
|---|---|---|---|---|---|---|---|
| 1 — code-smells-project | Python 3.13 + Flask 3.1.1 | MONOLITH | 7 | 6 | 5 | 5 | **23** |
| 2 — ecommerce-api-legacy | Node.js 24 + Express ^4.18.2 | MONOLITH | 5 | 5 | 5 | 4 | **19** |
| 3 — task-manager-api | Python 3.13 + Flask 3.0 + Flask-SQLAlchemy 3.1 | PARTIALLY LAYERED | 7 | 7 | 5 | 5 | **24** |

Relatórios completos: [`reports/audit-project-1.md`](reports/audit-project-1.md),
[`reports/audit-project-2.md`](reports/audit-project-2.md),
[`reports/audit-project-3.md`](reports/audit-project-3.md).

**Cobertura da análise manual:** os 15 problemas documentados manualmente em cada projeto aparecem
nos relatórios da skill (3/3 projetos, 15/15) — ex.: SQL Injection com bypass de login (P1),
cartão no log (P2), MD5 e `datetime.utcnow()`/`Query.get()` deprecated (P3). A skill achou também
pontos que não listei, como o filtro de preço que ignora `0` (P1, F-23), a ordem não determinística
do relatório financeiro (P2) e a escalada de privilégio no `POST /users` com `role: admin` (P3).

### Antes × depois

**Projeto 1 — code-smells-project** (monólito → reestruturação completa em `src/`)

```text
ANTES (4 arquivos, ~780 linhas)          DEPOIS (34 arquivos .py, ~1.390 linhas)
app.py          rotas + config + SQL     app.py                      entry point (python app.py preservado)
controllers.py  292 ln, todos domínios   src/app.py                  create_app() — composition root
models.py       314 ln, SQL + regras     src/config/{settings,constants}.py
database.py     conexão global + seed    src/database.py             conexão por request (flask.g) + schema/seed
                                         src/models/{produto,usuario,pedido}_model.py
                                         src/controllers/{produto,usuario,pedido,relatorio,sistema,admin}_controller.py
                                         src/controllers/validators.py
                                         src/views/{produto,usuario,pedido,relatorio,sistema,admin}_routes.py
                                         src/middlewares/{error_handler,auth}.py
                                         src/services/{password,token,notificacao}_service.py
                                         src/errors.py, .env.example
```

**Projeto 2 — ecommerce-api-legacy** (god class → reestruturação completa)

```text
ANTES (3 arquivos, ~180 linhas)          DEPOIS (25 arquivos .js, ~770 linhas)
src/app.js         boot                  src/app.js            entry point (npm start preservado)
src/AppManager.js  141 ln: DB+schema+    src/createApp.js      composition root
                   seed+rotas+pagamento  src/config/{settings,constants}.js
src/utils.js       config com segredos   src/database/connection.js   sqlite3 promisificado + transações
                   + estado global       src/models/{user,course,enrollment,payment,auditLog,report}Model.js
                   + badCrypto           src/controllers/{checkout,report,user}Controller.js + validators.js
                                         src/views/{checkout,report,user}Routes.js
                                         src/middlewares/{errorHandler,asyncHandler,requireAdminToken}.js
                                         src/services/{paymentGateway,passwordHasher,logger}.js
                                         src/errors.js, .env.example
```

**Projeto 3 — task-manager-api** (parcialmente organizado → evolução *in place*)

```text
ANTES                                    DEPOIS
app.py        config inline + app global app.py          create_app() + entry point
models/       entidades (MD5, utcnow)    config/         settings.py, constants.py              (NOVO)
routes/       211–299 ln, regra + ORM    controllers/    task, user, auth, category, report + validators  (NOVO)
services/     notificação órfã, SMTP     middlewares/    error_handler.py, auth.py              (NOVO)
              hardcoded                  models/         + base.py (now_utc), queries/repositório nas entidades
utils/        helpers.py (código morto)  routes/         views finas (≤ 67 ln) + serializers.py, health/auth/category extraídos
seed.py       importa app global         services/       password_hasher, token_service, notification (injetado)
                                         errors.py, .env.example;  utils/ removido;  seed.py usa a factory
```

### Checklist de validação

| Item | P1 | P2 | P3 |
|---|---|---|---|
| **Fase 1** — Linguagem detectada corretamente | ✅ Python 3.13 | ✅ JavaScript (Node 24) | ✅ Python 3.13 |
| Framework detectado corretamente | ✅ Flask 3.1.1 | ✅ Express ^4.18.2 | ✅ Flask 3.0 + SQLAlchemy |
| Domínio descrito corretamente | ✅ E-commerce | ✅ LMS com checkout | ✅ Task Manager |
| Nº de arquivos condiz com a realidade | ✅ 4 | ✅ 3 | ✅ 15 (3 `__init__` vazios) |
| **Fase 2** — Relatório segue o template | ✅ | ✅ | ✅ |
| Cada finding tem arquivo e linhas exatos | ✅ | ✅ | ✅ |
| Ordenado CRITICAL → LOW | ✅ | ✅ | ✅ |
| Mínimo de 5 findings | ✅ 23 | ✅ 19 | ✅ 24 |
| Detecção de APIs deprecated | ✅ verificado, nenhuma aplicável | ✅ verificado, nenhuma aplicável (callback sqlite3 tratado como legado) | ✅ `utcnow` ×24, `Query.get` ×15 |
| Pausa e pede confirmação antes da Fase 3 | ✅ | ✅ | ✅ (`git status` limpo após a Fase 2) |
| **Fase 3** — Estrutura MVC | ✅ | ✅ | ✅ |
| Config extraída (sem hardcoded) | ✅ `src/config/settings.py` | ✅ `src/config/settings.js` | ✅ `config/settings.py` |
| Models abstraem dados | ✅ | ✅ | ✅ |
| Views/Routes separadas | ✅ `src/views/` | ✅ `src/views/` | ✅ `routes/` |
| Controllers concentram o fluxo | ✅ | ✅ | ✅ |
| Error handling centralizado | ✅ | ✅ | ✅ |
| Entry point claro | ✅ `app.py` | ✅ `src/app.js` | ✅ `app.py` |
| Aplicação inicia sem erros | ✅ | ✅ | ✅ |
| Endpoints originais respondem | ✅ 34/34 | ✅ 10/10 | ✅ 45/45 |

### Evidências de execução

Validação **independente** da skill: um spec próprio por projeto (`scripts/specs/`) executado contra
o código **original** (baseline, `docs/evidence/project-N-baseline.txt`) e contra o **refatorado**
(`docs/evidence/project-N-after.txt`), com `--compare` no baseline. Além disso, a própria skill rodou
seu smoke test interno (49/49, 9/9 e 72/72 requisições — ver `*/.refactor-arch/`).

Baseline do projeto 1 (código original) — duas falhas que **provam** o SQL Injection:

```text
  ✗ 500 GET    /produtos/busca?q=%27%20OR%201%3D1%20--  search sql injection probe
  ✗ 200 POST   /login                                   login sql injection probe (expected 401)
31/33 requests OK
```

Projeto 1 após a refatoração:

```text
 * Serving Flask app 'src.app'
 * Debug mode: off
 * Running on http://127.0.0.1:5301
  ✓ 200 GET    /health                                  health  keys +[] -['ambiente', 'db_path', 'debug', 'secret_key']
  ✓ 200 GET    /produtos/busca?q=%27%20OR%201%3D1%20--  search sql injection probe
  ✓ 401 POST   /login                                   login sql injection probe
  ✓ 403 POST   /admin/query                             admin query without token
  ...
34/34 requests OK
```

Projeto 2 após a refatoração (log estruturado, cartão mascarado):

```text
{"level":"info","message":"server.started","context":{"port":3302,"env":"development"}}
{"level":"info","message":"payment.charge","context":{"card":"****4444","amount":497,"status":"PAID","gatewayConfigured":false}}
  ✓ 403 GET    /api/admin/financial-report              financial report without admin token
  ✓ 200 DELETE /api/users/1                             delete user
10/10 requests OK
```

Projeto 3 após a refatoração (seed sem `DeprecationWarning`):

```text
Seed concluído com sucesso!  3 usuários / 4 categorias / 10 tasks
 * Debug mode: off
  ✓ 200 GET    /users/1                                 get user  keys +[] -['password']
  ✓ 401 POST   /tasks                                   create task anonymous
  ✓ 401 DELETE /users/1                                 delete user anonymous
45/45 requests OK
```

### Mudanças intencionais de comportamento

A regra 4 do `SKILL.md` só permite mudar o contrato para fechar falhas da Fase 2, sempre listando
a mudança. Principais:

- **P1:** `senha` saiu de `/usuarios`; `/health` não expõe mais `secret_key`/`db_path`/`debug`;
  `/admin/*` exige `X-Admin-Token` e `/admin/query` aceita só um `SELECT`; entradas inválidas que davam
  500 agora dão 400; e-mail duplicado dá 409.
- **P2:** relatório financeiro e `DELETE /api/users/:id` exigem `X-Admin-Token`; o delete passou a
  remover matrículas e pagamentos em transação; checkout de usuário novo sem senha dá 400 (antes
  criava o usuário com `123456`).
- **P3:** `password` saiu de todas as respostas; o token do `/login` é assinado (itsdangerous) e
  **passa a ser exigido** (`Authorization: Bearer` ou `X-Admin-Token`) em escritas, dados de usuário
  e relatórios — anônimo recebe 401. Leituras públicas (`/`, `/health`, `GET /tasks*`,
  `GET /categories`), `POST /login` e `POST /users` continuam abertas.

### Observações sobre o comportamento em stacks diferentes

- **Detecção de stack** foi correta nos 3 sem ajuste: versões vieram do manifesto e do runtime
  instalado (`Express ^4.18.2 (instalado: 4.22.1)`).
- **Adaptação ao nível de organização funcionou:** nos monólitos (P1, P2) a skill reestruturou tudo
  e apagou os god modules; no P3 manteve `models/` e `routes/` (a camada View), adicionou só o que
  faltava e desfez o `utils/`.
- **Express exigiu padrões próprios** que o playbook cobre: promisify do `sqlite3`, `asyncHandler`
  (Express 4 não captura promises rejeitadas), fila de transações na conexão compartilhada e
  `ORDER BY` para tornar o relatório determinístico.
- **Flask + SQLAlchemy:** a troca de `utcnow()` foi feita com um `now_utc()` *naive*, como orienta o
  playbook, para não quebrar comparações com as colunas existentes.
- **Postura de segurança variou entre execuções.** No P3 a skill decidiu proteger todas as
  escritas com autenticação. A decisão é justificada pela finding F-07 e está documentada, mas é a
  mudança de contrato mais forte dos três projetos. P1 e P2 protegeram só as rotas administrativas.
- **Honestidade nas pendências:** a skill marcou itens como DEFERRED em vez de forçar (paginação
  no P3 mudaria o formato das respostas). Ela também corrigiu duas afirmações do próprio relatório
  depois de verificar em execução (P3, F-11/F-17) e avisou que as chaves já expostas no histórico do
  Git precisam ser rotacionadas (P2).
- **Custo/tempo** (Claude Code headless): Fases 1–2 ≈ US$ 1,3–1,9 por projeto; Fase 3 ≈ US$ 3,9
  (P2), 7,1 (P1) e 8,6 (P3), com 45–74 turnos e 8–14 min cada (Fases 1–2: 4–6 min). Total das execuções finais ≈ US$ 24, mais US$ 1,75 da iteração 1. A Fase 3 domina o custo por causa
  do ciclo baseline → refatora → valida → corrige.

## D) Como Executar

### Pré-requisitos

- [Claude Code](https://docs.anthropic.com/en/docs/claude-code/overview) instalado e autenticado (`claude --version`; usado 2.1.236)
- Python 3.10+ (usado 3.13) e Node.js 18+ (usado 24)
- Dependências de cada projeto:

```bash
cd code-smells-project && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd task-manager-api   && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt && cd ..
cd ecommerce-api-legacy && npm install && cd ..
```

### Executando a skill

Interativo (recomendado — você revisa o relatório e responde `y`):

```bash
cd code-smells-project && claude      # dentro do Claude Code:
/refactor-arch ../reports/audit-project-1.md
```

Headless (como foi executado neste repositório — duas chamadas na mesma sessão):

```bash
cd code-smells-project
claude -p "/refactor-arch ../reports/audit-project-1.md" \
  --allowedTools "Read Grep Glob Bash Edit Write" --output-format stream-json --verbose > run1.jsonl
# revisar reports/audit-project-1.md, depois:
claude -p "y" --resume <session_id de run1.jsonl> \
  --allowedTools "Read Grep Glob Bash Edit Write" --output-format stream-json --verbose > run2.jsonl
python3 ../scripts/extract_transcript.py run2.jsonl     # transcrição legível
```

Repita em `ecommerce-api-legacy` (relatório `audit-project-2.md`) e `task-manager-api`
(`audit-project-3.md`). A skill é a mesma pasta copiada nos três projetos. Para só auditar:
`/refactor-arch --audit-only`.

### Validando a refatoração

Validação independente da skill — o mesmo spec usado no baseline do código original. O
`ADMIN_TOKEN` habilita as rotas protegidas (os specs enviam `X-Admin-Token: smoke-admin-token`):

```bash
# Projeto 1
cd code-smells-project && rm -f loja.db
PORT=5301 ADMIN_TOKEN=smoke-admin-token .venv/bin/python app.py &
python3 ../scripts/smoke.py ../scripts/specs/project-1.json http://127.0.0.1:5301 \
  --compare ../scripts/baseline/project-1.json

# Projeto 2
cd ../ecommerce-api-legacy
PORT=3302 ADMIN_TOKEN=smoke-admin-token npm start &
python3 ../scripts/smoke.py ../scripts/specs/project-2.json http://127.0.0.1:3302 \
  --compare ../scripts/baseline/project-2.json

# Projeto 3
cd ../task-manager-api && rm -rf instance && .venv/bin/python seed.py
PORT=5303 ADMIN_TOKEN=smoke-admin-token .venv/bin/python app.py &
python3 ../scripts/smoke.py ../scripts/specs/project-3.json http://127.0.0.1:5303 \
  --compare ../scripts/baseline/project-3.json
```

`✓` = mesmo status do baseline (ou o status `expect` fixado para correções de segurança, ex.: login
com SQL injection → 401). A saída também lista as chaves JSON que mudaram em relação ao original. O
código original pode ser reproduzido com `git checkout 6d1ce62 -- <projeto>`; para o Express
original, que tem porta fixa, use `node scripts/baseline-harness-project-2.js "$PWD/ecommerce-api-legacy"`.

### Ordem sugerida

1. Ler os relatórios em `reports/` (resultado da Fase 2).
2. Rodar a validação acima nos três projetos.
3. Para reexecutar a skill do zero: `git checkout 6d1ce62 -- code-smells-project` (idem para os outros)
   e seguir "Executando a skill".
