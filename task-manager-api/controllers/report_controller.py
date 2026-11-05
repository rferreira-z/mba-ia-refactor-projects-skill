"""Casos de uso de relatórios — agregações sem acesso direto ao ORM."""
from datetime import timedelta

from config.constants import (
    HIGH_PRIORITY_THRESHOLD,
    MAX_PRIORITY,
    MIN_PRIORITY,
    PRIORITY_LABELS,
    RECENT_ACTIVITY_DAYS,
    STATUS_DONE,
    TASK_STATUSES,
)
from controllers.task_controller import completion_rate
from errors import NotFoundError
from models.base import now_utc
from models.category import Category
from models.task import Task
from models.user import User


def summary():
    now = now_utc()
    status_counts = Task.status_counts()
    priority_counts = Task.priority_counts()
    recent_window = now - timedelta(days=RECENT_ACTIVITY_DAYS)
    totals_by_user = Task.totals_by_user()

    overdue_tasks = Task.list_overdue(now)

    return {
        'generated_at': str(now),
        'overview': {
            'total_tasks': sum(status_counts.values()),
            'total_users': len(User.list_all()),
            'total_categories': len(Category.list_all()),
        },
        'tasks_by_status': {status: status_counts.get(status, 0) for status in TASK_STATUSES},
        'tasks_by_priority': {
            PRIORITY_LABELS[priority]: priority_counts.get(priority, 0)
            for priority in range(MIN_PRIORITY, MAX_PRIORITY + 1)
        },
        'overdue': {
            'count': len(overdue_tasks),
            'tasks': [
                {
                    'id': task.id,
                    'title': task.title,
                    'due_date': str(task.due_date),
                    'days_overdue': (now - task.due_date).days,
                }
                for task in overdue_tasks
            ],
        },
        'recent_activity': {
            'tasks_created_last_7_days': Task.count_created_since(recent_window),
            'tasks_completed_last_7_days': Task.count_completed_since(recent_window),
        },
        'user_productivity': [
            _user_productivity(user, *totals_by_user.get(user.id, (0, 0)))
            for user in User.list_all()
        ],
    }


def _user_productivity(user, total, completed):
    return {
        'user_id': user.id,
        'user_name': user.name,
        'total_tasks': total,
        'completed_tasks': completed,
        'completion_rate': completion_rate(completed, total),
    }


def user_report(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')

    now = now_utc()
    tasks = Task.list_by_user(user_id)
    statistics = {status: 0 for status in TASK_STATUSES}
    statistics.update({'overdue': 0, 'high_priority': 0})

    for task in tasks:
        if task.status in statistics:
            statistics[task.status] += 1
        if task.priority is not None and task.priority <= HIGH_PRIORITY_THRESHOLD:
            statistics['high_priority'] += 1
        if task.is_overdue(now):
            statistics['overdue'] += 1

    total = len(tasks)
    statistics['total_tasks'] = total
    statistics['completion_rate'] = completion_rate(statistics[STATUS_DONE], total)

    return {
        'user': {'id': user.id, 'name': user.name, 'email': user.email},
        'statistics': statistics,
    }
