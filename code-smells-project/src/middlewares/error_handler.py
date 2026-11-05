"""Tratamento central de erros — o único lugar que mapeia erro para HTTP.

Substitui os 17 blocos `try/except Exception` que repetiam a mesma resposta de
erro em cada handler. Erros previstos usam a sua própria mensagem;
erros inesperados são registrados no log do servidor e devolvem uma
mensagem genérica, sem vazar o schema do banco.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from src.errors import AppError


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def _erro_de_dominio(erro):
        return jsonify({"erro": erro.message, "sucesso": False}), erro.status

    @app.errorhandler(HTTPException)
    def _erro_http(erro):
        return jsonify({"erro": erro.description, "sucesso": False}), erro.code

    @app.errorhandler(Exception)
    def _erro_inesperado(erro):
        app.logger.exception("Erro não tratado: %s", type(erro).__name__)
        return jsonify({"erro": "Erro interno do servidor", "sucesso": False}), 500
