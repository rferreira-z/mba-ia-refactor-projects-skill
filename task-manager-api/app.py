"""Composition root e entry point da aplicação.

É o único lugar onde as dependências concretas são montadas: configuração,
banco, serviços, blueprints e middlewares. Não contém rota nem regra de negócio.
"""
import logging

from dotenv import load_dotenv
from flask import Flask
from flask_cors import CORS
from sqlalchemy import event
from sqlalchemy.engine import Engine

from config.settings import Settings
from database import db
from middlewares.error_handler import register_error_handlers
from routes.auth_routes import auth_bp
from routes.category_routes import category_bp
from routes.health_routes import health_bp
from routes.report_routes import report_bp
from routes.task_routes import task_bp
from routes.user_routes import user_bp
from services.notification_service import NotificationService


@event.listens_for(Engine, 'connect')
def _enable_sqlite_foreign_keys(dbapi_connection, _connection_record):
    """O SQLite ignora chaves estrangeiras por padrão; aqui elas passam a valer."""
    if dbapi_connection.__class__.__module__.startswith('sqlite3'):
        cursor = dbapi_connection.cursor()
        cursor.execute('PRAGMA foreign_keys=ON')
        cursor.close()


def create_app(settings=None):
    load_dotenv()  # lê um .env local, se existir (nunca sobrescreve o ambiente)
    settings = settings or Settings()

    app = Flask(__name__)
    app.config.from_object(settings)
    app.config['SETTINGS'] = settings
    logging.basicConfig(level=settings.LOG_LEVEL)

    CORS(app, origins=settings.CORS_ORIGINS)
    db.init_app(app)

    app.extensions['notifier'] = NotificationService(settings)

    for blueprint in (health_bp, auth_bp, task_bp, user_bp, category_bp, report_bp):
        app.register_blueprint(blueprint)

    register_error_handlers(app)

    with app.app_context():
        import models  # noqa: F401  (registra os models antes do create_all)

        db.create_all()

    return app


app = create_app()


if __name__ == '__main__':
    settings = app.config['SETTINGS']
    app.run(host=settings.HOST, port=settings.PORT, debug=settings.DEBUG)
