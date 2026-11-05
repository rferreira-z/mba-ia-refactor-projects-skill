"""View dos endpoints de sistema: índice da API e health check."""
from flask import Blueprint, jsonify


def create_sistema_blueprint(controller):
    bp = Blueprint("sistema", __name__)

    @bp.get("/")
    def index():
        return jsonify(controller.indice()), 200

    @bp.get("/health")
    def health_check():
        return jsonify(controller.health()), 200

    return bp
