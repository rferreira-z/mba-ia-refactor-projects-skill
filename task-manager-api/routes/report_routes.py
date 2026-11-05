"""View de relatórios."""
from flask import Blueprint, jsonify

from controllers import report_controller
from middlewares.auth import require_admin, require_auth

report_bp = Blueprint('reports', __name__)


@report_bp.get('/reports/summary')
@require_admin
def summary_report():
    """Agrega produtividade de todos os usuários: restrito a administradores."""
    return jsonify(report_controller.summary()), 200


@report_bp.get('/reports/user/<int:user_id>')
@require_auth
def user_report(user_id):
    return jsonify(report_controller.user_report(user_id)), 200
