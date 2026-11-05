"""Serialização das respostas HTTP — uma única definição por formato.

Campos sensíveis (hash de senha) nunca entram em nenhum serializer.
"""

# Campos públicos de usuário: `password` fica deliberadamente de fora
USER_PUBLIC_FIELDS = ('id', 'name', 'email', 'role', 'active', 'created_at')


def serialize_task(task):
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'user_id': task.user_id,
        'category_id': task.category_id,
        'created_at': str(task.created_at),
        'updated_at': str(task.updated_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'tags': task.tag_list(),
    }


def serialize_task_with_overdue(task, now=None):
    data = serialize_task(task)
    data['overdue'] = task.is_overdue(now)
    return data


def serialize_task_listing(task, now=None):
    """Formato de `GET /tasks`: inclui atraso e os nomes das relações."""
    data = serialize_task_with_overdue(task, now)
    data['user_name'] = task.user.name if task.user else None
    data['category_name'] = task.category.name if task.category else None
    return data


def serialize_task_summary(task, now=None):
    """Formato reduzido de `GET /users/<id>/tasks`."""
    return {
        'id': task.id,
        'title': task.title,
        'description': task.description,
        'status': task.status,
        'priority': task.priority,
        'created_at': str(task.created_at),
        'due_date': str(task.due_date) if task.due_date else None,
        'overdue': task.is_overdue(now),
    }


def serialize_user(user):
    data = {field: getattr(user, field) for field in USER_PUBLIC_FIELDS}
    data['created_at'] = str(user.created_at)
    return data


def serialize_user_with_task_count(user, task_count):
    data = serialize_user(user)
    data['task_count'] = task_count
    return data


def serialize_category(category):
    return {
        'id': category.id,
        'name': category.name,
        'description': category.description,
        'color': category.color,
        'created_at': str(category.created_at),
    }


def serialize_category_with_task_count(category, task_count):
    data = serialize_category(category)
    data['task_count'] = task_count
    return data
