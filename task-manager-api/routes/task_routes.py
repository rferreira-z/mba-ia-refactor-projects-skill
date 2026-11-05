"""View de tasks: declara endpoints, lê a requisição e serializa a resposta."""
from flask import Blueprint, current_app, jsonify, request

from controllers import task_controller
from middlewares.auth import require_auth
from models.base import now_utc
from routes.serializers import (
    serialize_task,
    serialize_task_listing,
    serialize_task_with_overdue,
)

task_bp = Blueprint('tasks', __name__)


def _notifier():
    """Serviço de notificação injetado pelo composition root."""
    return current_app.extensions.get('notifier')


@task_bp.get('/tasks')
def get_tasks():
    now = now_utc()
    tasks = task_controller.list_tasks()
    return jsonify([serialize_task_listing(task, now) for task in tasks]), 200


@task_bp.get('/tasks/search')
def search_tasks():
    tasks = task_controller.search_tasks(
        text=request.args.get('q', ''),
        status=request.args.get('status', ''),
        priority=request.args.get('priority', ''),
        user_id=request.args.get('user_id', ''),
    )
    return jsonify([serialize_task(task) for task in tasks]), 200


@task_bp.get('/tasks/stats')
def task_stats():
    return jsonify(task_controller.task_stats()), 200


@task_bp.get('/tasks/<int:task_id>')
def get_task(task_id):
    return jsonify(serialize_task_with_overdue(task_controller.get_task(task_id))), 200


@task_bp.post('/tasks')
@require_auth
def create_task():
    task = task_controller.create_task(request.get_json(silent=True), notifier=_notifier())
    return jsonify(serialize_task(task)), 201


@task_bp.put('/tasks/<int:task_id>')
@require_auth
def update_task(task_id):
    task = task_controller.update_task(task_id, request.get_json(silent=True))
    return jsonify(serialize_task(task)), 200


@task_bp.delete('/tasks/<int:task_id>')
@require_auth
def delete_task(task_id):
    task_controller.delete_task(task_id)
    return jsonify({'message': 'Task deletada com sucesso'}), 200
