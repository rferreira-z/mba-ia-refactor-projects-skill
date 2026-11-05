# code-smells-project

API de E-commerce em Python/Flask usada como entrada do desafio `refactor-arch`,
refatorada para uma arquitetura MVC em camadas.

## Como rodar

```bash
pip install -r requirements.txt
python app.py
```

A aplicação sobe em `http://localhost:5000`. O banco SQLite (`loja.db`) é criado
automaticamente no primeiro boot, já com produtos e usuários de exemplo.

## Configuração

Toda configuração vem de variáveis de ambiente — veja `.env.example` para a lista
completa. Os defaults servem só para desenvolvimento:

| Variável | Default | Observação |
|---|---|---|
| `SECRET_KEY` | `dev-only-change-me` | Assina os tokens de login. Defina em produção. |
| `ADMIN_TOKEN` | *(vazio)* | Sem ele, as rotas `/admin` negam todo acesso. |
| `HOST` / `PORT` | `127.0.0.1` / `5000` | |
| `FLASK_DEBUG` | `0` | Debug desligado por padrão. |
| `DATABASE_PATH` | `loja.db` | |
| `SEED_ON_STARTUP` | `1` | Popula o banco vazio com os dados de exemplo. |
| `CORS_ORIGINS` | `http://localhost:3000,http://localhost:5173` | Lista separada por vírgula. |
| `LOG_LEVEL` | `INFO` | |

As rotas administrativas aceitam `X-Admin-Token: $ADMIN_TOKEN` ou
`Authorization: Bearer <token>` de um usuário `admin` autenticado em `/login`.
`POST /admin/query` executa apenas uma consulta `SELECT` somente-leitura.

## Arquitetura

```text
app.py                      entry point (chama create_app)
src/app.py                  composition root — liga config, banco, services, models, views
src/config/                 CONFIG      settings (env) e constantes de domínio
src/models/                 MODEL       SQL parametrizado, mapeamento, transações
src/controllers/            CONTROLLER  casos de uso, validação e regras de negócio
src/views/                  VIEW        Blueprints: parse da requisição e serialização
src/middlewares/            auth (guard admin) e tratamento central de erros
src/services/               infraestrutura: hash de senha, tokens, notificações
src/errors.py               hierarquia AppError traduzida para HTTP no middleware
```

As dependências apontam em uma direção só: **View → Controller → Model → Banco**.
Models não importam Flask; controllers não tocam em `request`; views não contêm SQL.
