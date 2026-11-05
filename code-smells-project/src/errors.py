"""Hierarquia de erros de domínio.

Controllers e models levantam estes erros; o middleware de erro é o único
lugar que os traduz para status HTTP. Nenhum import de framework aqui.
"""


class AppError(Exception):
    """Erro de domínio previsto, seguro para ser exibido ao cliente."""

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
