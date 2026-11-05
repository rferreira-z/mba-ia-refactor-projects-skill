"""Configuração da aplicação lida de variáveis de ambiente.

Nenhum segredo literal: todos os valores sensíveis vêm do ambiente e os defaults
são obviamente de desenvolvimento. Veja `.env.example`.
"""
import os


def _as_bool(value, default=False):
    if value is None:
        return default
    return value.strip().lower() in ('1', 'true', 'yes', 'on')


def _as_int(value, default):
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


class Settings:
    """Configuração imutável da aplicação (instanciada no composition root)."""

    def __init__(self, env=None):
        env = os.environ if env is None else env

        # Segurança
        self.SECRET_KEY = env.get('SECRET_KEY', 'dev-only-change-me')
        self.ADMIN_TOKEN = env.get('ADMIN_TOKEN', 'dev-admin-token-change-me')
        self.TOKEN_MAX_AGE_SECONDS = _as_int(env.get('TOKEN_MAX_AGE_SECONDS'), 8 * 60 * 60)

        # Banco de dados
        self.SQLALCHEMY_DATABASE_URI = env.get('DATABASE_URL', 'sqlite:///tasks.db')
        self.SQLALCHEMY_TRACK_MODIFICATIONS = False

        # Runtime (debug desligado por padrão; bind apenas em loopback)
        self.DEBUG = _as_bool(env.get('FLASK_DEBUG'), False)
        self.HOST = env.get('HOST', '127.0.0.1')
        self.PORT = _as_int(env.get('PORT'), 5000)

        # CORS: lista de origens separadas por vírgula ('*' libera todas)
        self.CORS_ORIGINS = [o.strip() for o in env.get('CORS_ORIGINS', 'http://localhost:3000').split(',') if o.strip()]

        # Notificações por e-mail (desligadas enquanto SMTP_HOST estiver vazio)
        self.SMTP_HOST = env.get('SMTP_HOST', '')
        self.SMTP_PORT = _as_int(env.get('SMTP_PORT'), 587)
        self.SMTP_USER = env.get('SMTP_USER', '')
        self.SMTP_PASSWORD = env.get('SMTP_PASSWORD', '')

        self.LOG_LEVEL = env.get('LOG_LEVEL', 'INFO')
