"""Autenticação e autorização das rotas.

Duas credenciais são aceitas:

* `Authorization: Bearer <token>` — token assinado emitido por `POST /login`,
  resolvido para o usuário correspondente;
* `X-Admin-Token: <token>` — token administrativo vindo da configuração, para
  operação/automação (não está ligado a um usuário).

As rotas públicas (health, listagem de tasks/categorias, login e cadastro) não
usam estes decorators.
"""
import hmac
from functools import wraps

from flask import current_app, g, request

from config.constants import ROLE_ADMIN
from errors import ForbiddenError, UnauthorizedError
from models.user import User
from services.token_service import read_token


class Identity:
    """Quem está fazendo a requisição."""

    def __init__(self, user_id=None, role=None, user=None):
        self.user_id = user_id
        self.role = role
        self.user = user

    @property
    def is_admin(self):
        return self.role == ROLE_ADMIN


def _settings():
    return current_app.config['SETTINGS']


def _identity_from_admin_token(settings):
    header = request.headers.get('X-Admin-Token')
    if not header or not settings.ADMIN_TOKEN:
        return None
    if not hmac.compare_digest(header, settings.ADMIN_TOKEN):
        return None
    return Identity(role=ROLE_ADMIN)


def _identity_from_bearer(settings):
    header = request.headers.get('Authorization', '')
    scheme, _, token = header.partition(' ')
    if scheme.lower() != 'bearer' or not token:
        return None
    user_id = read_token(settings.SECRET_KEY, token.strip(), settings.TOKEN_MAX_AGE_SECONDS)
    if user_id is None:
        return None
    user = User.get_by_id(user_id)
    if not user or not user.active:
        return None
    return Identity(user_id=user.id, role=user.role, user=user)


def resolve_identity():
    """Resolve a identidade da requisição atual (uma vez por request)."""
    if 'identity' not in g:
        settings = _settings()
        g.identity = _identity_from_admin_token(settings) or _identity_from_bearer(settings)
    return g.identity


def current_identity():
    return resolve_identity()


def require_auth(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        if resolve_identity() is None:
            raise UnauthorizedError('Autenticação necessária')
        return view(*args, **kwargs)

    return wrapper


def require_admin(view):
    @wraps(view)
    def wrapper(*args, **kwargs):
        identity = resolve_identity()
        if identity is None:
            raise UnauthorizedError('Autenticação necessária')
        if not identity.is_admin:
            raise ForbiddenError('Acesso restrito a administradores')
        return view(*args, **kwargs)

    return wrapper
