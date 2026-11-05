"""Configuração da aplicação (camada CONFIG).

Todo valor vem de variável de ambiente, com defaults de desenvolvimento
explicitamente não-produtivos. Nenhum segredo literal mora aqui.
"""
import os

_VALORES_VERDADEIROS = frozenset({"1", "true", "yes", "on", "sim"})

SECRET_KEY_PADRAO_DEV = "dev-only-change-me"


def _flag(ambiente, nome, padrao="0"):
    return ambiente.get(nome, padrao).strip().lower() in _VALORES_VERDADEIROS


def _inteiro(ambiente, nome, padrao):
    try:
        return int(ambiente.get(nome, padrao))
    except ValueError:
        return int(padrao)


class Settings:
    """Configurações lidas do ambiente; instanciada uma vez pelo create_app()."""

    def __init__(self, ambiente=None):
        ambiente = os.environ if ambiente is None else ambiente

        self.SECRET_KEY = ambiente.get("SECRET_KEY", SECRET_KEY_PADRAO_DEV)
        self.DEBUG = _flag(ambiente, "FLASK_DEBUG")
        self.HOST = ambiente.get("HOST", "127.0.0.1")
        self.PORT = _inteiro(ambiente, "PORT", "5000")
        self.DATABASE_PATH = ambiente.get("DATABASE_PATH", "loja.db")
        self.SEED_ON_STARTUP = _flag(ambiente, "SEED_ON_STARTUP", "1")
        self.LOG_LEVEL = ambiente.get("LOG_LEVEL", "INFO").upper()
        # Sem token configurado o guard administrativo nega todo acesso.
        self.ADMIN_TOKEN = ambiente.get("ADMIN_TOKEN", "")
        self.CORS_ORIGINS = [
            origem.strip()
            for origem in ambiente.get(
                "CORS_ORIGINS", "http://localhost:3000,http://localhost:5173"
            ).split(",")
            if origem.strip()
        ]

    @property
    def usando_secret_key_padrao(self):
        return self.SECRET_KEY == SECRET_KEY_PADRAO_DEV
