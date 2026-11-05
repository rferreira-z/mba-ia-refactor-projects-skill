"""View de autenticação."""
from flask import Blueprint, current_app, jsonify, request

from controllers import auth_controller
from routes.serializers import serialize_user

auth_bp = Blueprint('auth', __name__)


@auth_bp.post('/login')
def login():
    user, token = auth_controller.login(
        request.get_json(silent=True), current_app.config['SETTINGS'].SECRET_KEY
    )
    return jsonify({
        'message': 'Login realizado com sucesso',
        'user': serialize_user(user),
        'token': token,
    }), 200
