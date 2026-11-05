"""View de categorias (extraída de report_routes.py, onde não pertencia)."""
from flask import Blueprint, jsonify, request

from controllers import category_controller
from middlewares.auth import require_auth
from routes.serializers import serialize_category, serialize_category_with_task_count

category_bp = Blueprint('categories', __name__)


@category_bp.get('/categories')
def get_categories():
    categories = category_controller.list_categories()
    return jsonify([serialize_category_with_task_count(c, count) for c, count in categories]), 200


@category_bp.post('/categories')
@require_auth
def create_category():
    category = category_controller.create_category(request.get_json(silent=True))
    return jsonify(serialize_category(category)), 201


@category_bp.put('/categories/<int:cat_id>')
@require_auth
def update_category(cat_id):
    category = category_controller.update_category(cat_id, request.get_json(silent=True))
    return jsonify(serialize_category(category)), 200


@category_bp.delete('/categories/<int:cat_id>')
@require_auth
def delete_category(cat_id):
    category_controller.delete_category(cat_id)
    return jsonify({'message': 'Categoria deletada'}), 200
