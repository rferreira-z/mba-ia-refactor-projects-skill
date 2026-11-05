"""View de usuários."""
from flask import Blueprint, jsonify, request

from controllers import user_controller
from middlewares.auth import current_identity, require_admin, require_auth
from models.base import now_utc
from routes.serializers import (
    serialize_task,
    serialize_task_summary,
    serialize_user,
    serialize_user_with_task_count,
)

user_bp = Blueprint('users', __name__)


@user_bp.get('/users')
@require_auth
def get_users():
    users = user_controller.list_users()
    return jsonify([serialize_user_with_task_count(user, count) for user, count in users]), 200


@user_bp.get('/users/<int:user_id>')
@require_auth
def get_user(user_id):
    user, tasks = user_controller.get_user(user_id)
    data = serialize_user(user)
    data['tasks'] = [serialize_task(task) for task in tasks]
    return jsonify(data), 200


@user_bp.get('/users/<int:user_id>/tasks')
@require_auth
def get_user_tasks(user_id):
    now = now_utc()
    tasks = user_controller.get_user_tasks(user_id)
    return jsonify([serialize_task_summary(task, now) for task in tasks]), 200


@user_bp.post('/users')
def create_user():
    """Cadastro público: um papel privilegiado só é aceito de um admin."""
    user = user_controller.create_user(request.get_json(silent=True), identity=current_identity())
    return jsonify(serialize_user(user)), 201


@user_bp.put('/users/<int:user_id>')
@require_auth
def update_user(user_id):
    user = user_controller.update_user(
        user_id, request.get_json(silent=True), identity=current_identity()
    )
    return jsonify(serialize_user(user)), 200


@user_bp.delete('/users/<int:user_id>')
@require_admin
def delete_user(user_id):
    user_controller.delete_user(user_id)
    return jsonify({'message': 'Usuário deletado com sucesso'}), 200
