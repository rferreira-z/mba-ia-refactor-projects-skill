"""Caminho único de tratamento de erro.

Controllers e views levantam erros de domínio (`errors.AppError`); aqui eles
viram resposta HTTP com corpo consistente. Erros inesperados são logados com
stack no servidor e devolvem uma mensagem genérica ao cliente.
"""
from flask import jsonify
from werkzeug.exceptions import HTTPException

from errors import AppError

GENERIC_ERROR_MESSAGE = 'Erro interno'


def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(err):
        return jsonify({'error': err.message}), err.status

    @app.errorhandler(HTTPException)
    def handle_http_exception(err):
        # 404/405 do roteador do Flask continuam com o comportamento original
        return err

    @app.errorhandler(Exception)
    def handle_unexpected(err):
        app.logger.exception('Erro não tratado')
        return jsonify({'error': GENERIC_ERROR_MESSAGE}), 500
