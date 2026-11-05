"""Emissão e verificação de tokens de autenticação assinados.

Usa `itsdangerous` (dependência do próprio Flask — nenhum pacote novo). O token
é assinado com a SECRET_KEY e tem validade limitada, substituindo a string
previsível derivada do id do usuário que a versão anterior devolvia.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

_SALT = 'task-manager-auth'


def _serializer(secret_key):
    return URLSafeTimedSerializer(secret_key, salt=_SALT)


def issue_token(secret_key, user_id):
    return _serializer(secret_key).dumps({'user_id': user_id})


def read_token(secret_key, token, max_age_seconds):
    """Devolve o `user_id` do token, ou None se inválido/expirado."""
    try:
        payload = _serializer(secret_key).loads(token, max_age=max_age_seconds)
    except (BadSignature, SignatureExpired):
        return None
    if not isinstance(payload, dict):
        return None
    return payload.get('user_id')
