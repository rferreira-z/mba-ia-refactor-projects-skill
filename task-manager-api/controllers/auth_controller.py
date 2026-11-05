"""Caso de uso de autenticação."""
from controllers import validators
from errors import ForbiddenError, UnauthorizedError, ValidationError
from models.user import User
from services.token_service import issue_token


def login(data, secret_key):
    """Autentica e devolve (usuário, token assinado)."""
    validators.ensure_payload(data)

    email = data.get('email')
    password = data.get('password')
    if not email or not password:
        raise ValidationError('Email e senha são obrigatórios')

    user = User.get_by_email(email)
    # A mesma mensagem para e-mail inexistente e senha errada evita enumerar usuários
    if not user or not user.check_password(password):
        raise UnauthorizedError('Credenciais inválidas')
    if not user.active:
        raise ForbiddenError('Usuário inativo')

    return user, issue_token(secret_key, user.id)
