"""Hashing de senha com KDF lento e salgado.

Usa `werkzeug.security` (já instalado como dependência do Flask — nenhum pacote
novo). O default do Werkzeug é scrypt com salt aleatório por senha, substituindo
o MD5 sem salt da versão anterior.
"""
from werkzeug.security import check_password_hash, generate_password_hash


def hash_password(raw_password):
    return generate_password_hash(raw_password)


def verify_password(stored_hash, raw_password):
    """Compara em tempo constante. Hashes em formato legado (MD5) não validam."""
    if not stored_hash or not raw_password:
        return False
    try:
        return check_password_hash(stored_hash, raw_password)
    except ValueError:
        # Hash antigo, em formato não reconhecido: trata como credencial inválida
        return False
