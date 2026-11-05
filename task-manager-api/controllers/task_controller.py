"""Casos de uso de tasks. Sem Flask, sem SQL — orquestra validação e models."""
from config.constants import DEFAULT_PRIORITY, STATUS_DONE, STATUS_PENDING, TASK_STATUSES
from controllers import validators
from errors import NotFoundError
from models.base import now_utc
from models.category import Category
from models.task import Task
from models.user import User


def _get_task_or_404(task_id):
    task = Task.get_by_id(task_id)
    if not task:
        raise NotFoundError('Task não encontrada')
    return task


def _resolve_user(user_id):
    if user_id is None:
        return None
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def _resolve_category(category_id):
    if category_id is None:
        return None
    category = Category.get_by_id(category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_tasks():
    return Task.list_all(with_relations=True)


def get_task(task_id):
    return _get_task_or_404(task_id)


def create_task(data, notifier=None):
    validators.ensure_payload(data)

    fields = {
        'title': validators.validate_title(data.get('title')),
        'description': data.get('description', ''),
        'status': validators.validate_status(data.get('status', STATUS_PENDING)),
        'priority': validators.validate_priority(data.get('priority', DEFAULT_PRIORITY)),
        'user_id': data.get('user_id'),
        'category_id': data.get('category_id'),
    }

    user = _resolve_user(fields['user_id'])
    _resolve_category(fields['category_id'])

    if data.get('due_date'):
        fields['due_date'] = validators.validate_due_date(
            data['due_date'], 'Formato de data inválido. Use YYYY-MM-DD'
        )

    tags = validators.validate_tags(data.get('tags'))
    task = Task.create(**fields)
    if tags:
        task.set_tags(tags)
        Task.save()

    if user and notifier:
        notifier.notify_task_assigned(user, task)
    return task


def update_task(task_id, data):
    task = _get_task_or_404(task_id)
    validators.ensure_payload(data)

    if 'title' in data:
        task.title = validators.validate_title(data['title'])
    if 'description' in data:
        task.description = data['description']
    if 'status' in data:
        task.status = validators.validate_status(data['status'])
    if 'priority' in data:
        task.priority = validators.validate_priority(data['priority'])

    if 'user_id' in data:
        _resolve_user(data['user_id'])
        task.user_id = data['user_id']
    if 'category_id' in data:
        _resolve_category(data['category_id'])
        task.category_id = data['category_id']

    if 'due_date' in data:
        task.due_date = validators.validate_due_date(data['due_date']) if data['due_date'] else None
    if 'tags' in data:
        task.set_tags(validators.validate_tags(data['tags']))

    Task.save()
    return task


def delete_task(task_id):
    Task.delete(_get_task_or_404(task_id))


def search_tasks(text=None, status=None, priority=None, user_id=None):
    return Task.search(
        text=text or None,
        status=status or None,
        priority=validators.validate_optional_int(priority, 'Prioridade inválida'),
        user_id=validators.validate_optional_int(user_id, 'ID de usuário inválido'),
    )


def task_stats():
    now = now_utc()
    counts = Task.status_counts()
    total = sum(counts.values())
    done = counts.get(STATUS_DONE, 0)

    stats = {status: counts.get(status, 0) for status in TASK_STATUSES}
    stats['total'] = total
    stats['overdue'] = Task.count_overdue(now)
    stats['completion_rate'] = completion_rate(done, total)
    return stats


def completion_rate(done, total):
    """Regra de taxa de conclusão — única definição, usada por tasks e relatórios."""
    return round((done / total) * 100, 2) if total > 0 else 0
