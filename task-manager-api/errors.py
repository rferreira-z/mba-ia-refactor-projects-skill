"""Erros de domínio levantados pelos controllers e traduzidos para HTTP
pelo middleware `middlewares/error_handler.py`."""


class AppError(Exception):
    """Erro de aplicação com status HTTP associado."""

    status = 400

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    status = 400


class UnauthorizedError(AppError):
    status = 401


class ForbiddenError(AppError):
    status = 403


class NotFoundError(AppError):
    status = 404


class ConflictError(AppError):
    status = 409
