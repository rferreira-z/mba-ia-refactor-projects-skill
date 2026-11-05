"""Guard de autorização administrativa.

Aceita duas credenciais equivalentes:
  * `X-Admin-Token: <ADMIN_TOKEN>` — token de operação, vindo do ambiente;
  * `Authorization: Bearer <token>` — token assinado emitido no login, desde
    que pertença a um usuário do tipo admin.

Sem `ADMIN_TOKEN` configurado e sem Bearer válido o acesso é negado
(fail-closed).
"""
import hmac
from functools import wraps

from flask import request

from src.config.constants import TIPO_USUARIO_ADMIN
from src.errors import ForbiddenError

CABECALHO_ADMIN = "X-Admin-Token"
CABECALHO_AUTORIZACAO = "Authorization"
PREFIXO_BEARER = "bearer "


def require_admin(settings, tokens):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            if not (_token_de_operacao_valido(settings) or _bearer_de_admin(tokens)):
                raise ForbiddenError("Acesso administrativo negado")
            return view(*args, **kwargs)

        return wrapper

    return decorator


def _token_de_operacao_valido(settings):
    esperado = settings.ADMIN_TOKEN
    if not esperado:
        return False
    return hmac.compare_digest(request.headers.get(CABECALHO_ADMIN, ""), esperado)


def _bearer_de_admin(tokens):
    cabecalho = request.headers.get(CABECALHO_AUTORIZACAO, "")
    if not cabecalho.lower().startswith(PREFIXO_BEARER):
        return False
    payload = tokens.validar(cabecalho[len(PREFIXO_BEARER):].strip())
    return bool(payload) and payload.get("tipo") == TIPO_USUARIO_ADMIN
