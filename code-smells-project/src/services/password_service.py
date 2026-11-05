"""Hashing de senha com KDF lento e salgado.

Usa o Werkzeug, que já acompanha o Flask — nenhuma dependência nova.
"""
from werkzeug.security import check_password_hash, generate_password_hash


class PasswordService:
    def gerar_hash(self, senha):
        return generate_password_hash(senha)

    def verificar(self, senha, hash_armazenado):
        """Compara em código; a senha nunca entra numa cláusula SQL."""
        if not hash_armazenado:
            return False
        try:
            return check_password_hash(hash_armazenado, senha)
        except (ValueError, TypeError):
            return False
