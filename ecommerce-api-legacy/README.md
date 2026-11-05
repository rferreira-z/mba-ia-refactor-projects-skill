# ecommerce-api-legacy

LMS API (com fluxo de checkout) em Node.js/Express usada como entrada do desafio `refactor-arch`.
Refatorada para uma arquitetura MVC em camadas (`models/`, `views/`, `controllers/`, `config/`,
`middlewares/`, `services/`).

## Como rodar

```bash
npm install
npm start
```

A aplicação sobe em `http://localhost:3000`. O banco SQLite é em memória e já carrega seeds automaticamente no boot.

Exemplos de requisições estão em `api.http`.

## Configuração

Todos os parâmetros vêm de variáveis de ambiente, com defaults de desenvolvimento.
Veja `.env.example` para a lista completa.

| Variável | Default | Descrição |
|---|---|---|
| `PORT` | `3000` | Porta HTTP |
| `DATABASE_FILE` | `:memory:` | Arquivo SQLite (em memória por padrão) |
| `LOG_LEVEL` | `info` | `error` \| `warn` \| `info` \| `debug` |
| `ADMIN_TOKEN` | *(vazio)* | Credencial das rotas administrativas |
| `PAYMENT_GATEWAY_KEY` | *(vazio)* | Chave do gateway de pagamento |

Com `NODE_ENV=production`, `ADMIN_TOKEN` e `PAYMENT_GATEWAY_KEY` passam a ser obrigatórias e a
aplicação falha no boot se estiverem ausentes.

## Rotas administrativas

`GET /api/admin/financial-report` e `DELETE /api/users/:id` exigem o header `X-Admin-Token`
com o valor de `ADMIN_TOKEN`. Sem a variável configurada, ambas respondem `403`.

```bash
ADMIN_TOKEN=um-token-qualquer npm start
curl -H 'X-Admin-Token: um-token-qualquer' http://localhost:3000/api/admin/financial-report
```

## Estrutura

```text
src/
├── app.js                      # entry point
├── createApp.js                # composition root (injeção de dependências)
├── errors.js                   # hierarquia de erros de domínio
├── config/                     # settings (env) + constantes de negócio
├── database/connection.js      # SQLite promisificado, transações, schema e seed
├── models/                     # persistência (SQL parametrizado)
├── controllers/                # casos de uso e validação
├── views/                      # routers Express (HTTP in/out)
├── middlewares/                # errorHandler, asyncHandler, guard admin
└── services/                   # paymentGateway, passwordHasher, logger
```
