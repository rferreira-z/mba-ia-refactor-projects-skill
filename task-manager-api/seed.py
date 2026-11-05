"""Script para popular o banco com dados iniciais."""
import logging
from datetime import timedelta

from app import create_app
from database import db
from models.base import now_utc
from models.category import Category
from models.task import Task
from models.user import User

logger = logging.getLogger(__name__)

USERS = [
    {'name': 'João Silva', 'email': 'joao@email.com', 'password': '1234', 'role': 'admin'},
    {'name': 'Maria Santos', 'email': 'maria@email.com', 'password': 'abcd', 'role': 'user'},
    {'name': 'Pedro Oliveira', 'email': 'pedro@email.com', 'password': 'pass', 'role': 'manager'},
]

CATEGORIES = [
    {'name': 'Backend', 'description': 'Tarefas de backend', 'color': '#3498db'},
    {'name': 'Frontend', 'description': 'Tarefas de frontend', 'color': '#2ecc71'},
    {'name': 'DevOps', 'description': 'Tarefas de infraestrutura', 'color': '#e74c3c'},
    {'name': 'Bug', 'description': 'Correção de bugs', 'color': '#e67e22'},
]


def _tasks(now, users, categories):
    return [
        {'title': 'Implementar autenticação JWT', 'description': 'Adicionar autenticação real com JWT', 'status': 'pending', 'priority': 1, 'user_id': users[0].id, 'category_id': categories[0].id, 'due_date': now - timedelta(days=3)},
        {'title': 'Criar tela de login', 'description': 'Tela de login responsiva', 'status': 'in_progress', 'priority': 2, 'user_id': users[1].id, 'category_id': categories[1].id, 'due_date': now + timedelta(days=5)},
        {'title': 'Configurar CI/CD', 'description': 'Pipeline com GitHub Actions', 'status': 'done', 'priority': 2, 'user_id': users[2].id, 'category_id': categories[2].id, 'tags': 'devops,ci,github'},
        {'title': 'Corrigir bug no filtro de busca', 'description': 'Filtro não funciona com caracteres especiais', 'status': 'pending', 'priority': 1, 'user_id': users[0].id, 'category_id': categories[3].id, 'due_date': now - timedelta(days=1)},
        {'title': 'Adicionar paginação na API', 'description': 'Endpoints retornam todos os registros', 'status': 'pending', 'priority': 3, 'user_id': users[0].id, 'category_id': categories[0].id, 'due_date': now + timedelta(days=10)},
        {'title': 'Escrever testes unitários', 'description': 'Cobertura mínima de 80%', 'status': 'pending', 'priority': 2, 'user_id': users[1].id, 'category_id': categories[0].id},
        {'title': 'Documentar API com Swagger', 'description': 'Gerar documentação automática', 'status': 'cancelled', 'priority': 4, 'user_id': users[2].id, 'category_id': categories[0].id},
        {'title': 'Refatorar models', 'description': 'Melhorar organização dos models', 'status': 'in_progress', 'priority': 3, 'user_id': users[1].id, 'category_id': categories[0].id, 'tags': 'refactor,tech-debt'},
        {'title': 'Configurar monitoramento', 'description': 'Prometheus + Grafana', 'status': 'pending', 'priority': 4, 'user_id': users[2].id, 'category_id': categories[2].id, 'due_date': now + timedelta(days=20)},
        {'title': 'Melhorar validações de input', 'description': 'Usar marshmallow ou pydantic', 'status': 'pending', 'priority': 3, 'user_id': users[0].id, 'category_id': categories[0].id, 'tags': 'improvement,validation'},
    ]


def seed_data():
    app = create_app()
    with app.app_context():
        # Limpa tasks primeiro: respeita as chaves estrangeiras agora ativas
        db.session.execute(db.delete(Task))
        db.session.execute(db.delete(User))
        db.session.execute(db.delete(Category))
        db.session.commit()

        users = []
        for data in USERS:
            user = User(name=data['name'], email=data['email'], role=data['role'])
            user.set_password(data['password'])
            db.session.add(user)
            users.append(user)

        categories = [Category(**data) for data in CATEGORIES]
        db.session.add_all(categories)
        db.session.commit()

        db.session.add_all(Task(**fields) for fields in _tasks(now_utc(), users, categories))
        db.session.commit()

        print('Seed concluído com sucesso!')
        print(f'  {len(users)} usuários')
        print(f'  {len(categories)} categorias')
        print(f'  {Task.count_all()} tasks')


if __name__ == '__main__':
    seed_data()
