"""Emissão e validação de tokens assinados.

`itsdangerous` já acompanha o Flask — nenhuma dependência nova.
"""
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer

VALIDADE_PADRAO_SEGUNDOS = 24 * 60 * 60


class TokenService:
    def __init__(self, secret_key, validade_segundos=VALIDADE_PADRAO_SEGUNDOS):
        self._serializer = URLSafeTimedSerializer(secret_key, salt="auth")
        self._validade_segundos = validade_segundos

    def emitir(self, usuario_id, tipo):
        return self._serializer.dumps({"usuario_id": usuario_id, "tipo": tipo})

    def validar(self, token):
        """Devolve o payload do token ou None se for inválido/expirado."""
        try:
            return self._serializer.loads(token, max_age=self._validade_segundos)
        except (BadSignature, SignatureExpired):
            return None
