"""View administrativa — todas as rotas atrás do guard de admin."""
from flask import Blueprint, jsonify, request

from src.middlewares.auth import require_admin


def create_admin_blueprint(controller, settings, tokens):
    bp = Blueprint("admin", __name__, url_prefix="/admin")
    somente_admin = require_admin(settings, tokens)

    @bp.post("/reset-db")
    @somente_admin
    def resetar_database():
        controller.resetar_banco()
        return jsonify({"mensagem": "Banco de dados resetado", "sucesso": True}), 200

    @bp.post("/query")
    @somente_admin
    def executar_query():
        dados = request.get_json(silent=True) or {}
        resultado = controller.consultar(dados.get("sql", ""))
        return jsonify({"dados": resultado, "sucesso": True}), 200

    return bp
