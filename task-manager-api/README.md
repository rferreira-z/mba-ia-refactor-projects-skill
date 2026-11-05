# task-manager-api

API de Task Manager em Python/Flask usada como entrada do desafio `refactor-arch`. Após a refatoração, o projeto segue uma arquitetura MVC em camadas: `config/`, `models/`, `controllers/`, `routes/` (views), `middlewares/` e `services/`.

## Como rodar

```bash
pip install -r requirements.txt
python seed.py
python app.py
```

A aplicação sobe em `http://127.0.0.1:5000`. O `seed.py` popula o banco SQLite (`instance/tasks.db`) com usuários, categorias e tasks de exemplo — **rode-o antes do primeiro boot**, caso contrário os endpoints vão retornar listas vazias.

## Configuração

Toda a configuração vem de variáveis de ambiente, com defaults de desenvolvimento. Copie `.env.example` para `.env` e ajuste. Os valores que **precisam** ser definidos em produção são `SECRET_KEY` e `ADMIN_TOKEN`; `CORS_ORIGINS` já vem restrito e `FLASK_DEBUG` vem desligado.

Para mudar host/porta sem editar código: `HOST=0.0.0.0 PORT=8080 python app.py`.

## Autenticação

`POST /login` devolve um token assinado (válido por 8h por padrão), enviado nas requisições protegidas como:

```
Authorization: Bearer <token>
```

Para automação/operação existe também o token administrativo de configuração:

```
X-Admin-Token: <ADMIN_TOKEN>
```

### Quem pode o quê

| Acesso | Endpoints |
|---|---|
| Público | `GET /`, `GET /health`, `POST /login`, `POST /users` (cadastro), `GET /tasks`, `GET /tasks/<id>`, `GET /tasks/search`, `GET /tasks/stats`, `GET /categories` |
| Autenticado | `POST/PUT/DELETE /tasks`, `POST/PUT/DELETE /categories`, `GET /users`, `GET /users/<id>`, `GET /users/<id>/tasks`, `PUT /users/<id>` (o próprio usuário ou admin), `GET /reports/user/<id>` |
| Admin | `DELETE /users/<id>`, `GET /reports/summary`, definir `role`/`active` de um usuário |

O cadastro público continua aberto, mas um `role` privilegiado só é aceito quando a requisição vem de um admin — caso contrário o usuário é criado como `user`.

## Senhas

As senhas passaram a usar hash lento e salgado (`werkzeug.security`, padrão scrypt) no lugar de MD5. Bancos criados antes da refatoração têm hashes em formato antigo que não validam mais: rode `python seed.py` novamente ou redefina as senhas via `PUT /users/<id>`.
