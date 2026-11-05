"""Composition root — o único lugar onde dependências concretas são ligadas.

Nenhuma rota e nenhuma regra de negócio moram aqui: apenas a montagem
config -> banco -> services -> models -> controllers -> views.
"""
import logging

from flask import Flask
from flask_cors import CORS

from src.config.settings import Settings
from src.controllers.admin_controller import AdminController
from src.controllers.pedido_controller import PedidoController
from src.controllers.produto_controller import ProdutoController
from src.controllers.relatorio_controller import RelatorioController
from src.controllers.sistema_controller import SistemaController
from src.controllers.usuario_controller import UsuarioController
from src.database import Database, init_database
from src.middlewares.error_handler import register_error_handlers
from src.models.pedido_model import PedidoModel
from src.models.produto_model import ProdutoModel
from src.models.usuario_model import UsuarioModel
from src.services.notificacao_service import NotificacaoService
from src.services.password_service import PasswordService
from src.services.token_service import TokenService
from src.views.admin_routes import create_admin_blueprint
from src.views.pedido_routes import create_pedido_blueprint
from src.views.produto_routes import create_produto_blueprint
from src.views.relatorio_routes import create_relatorio_blueprint
from src.views.sistema_routes import create_sistema_blueprint
from src.views.usuario_routes import create_usuario_blueprint

logger = logging.getLogger(__name__)


def create_app(settings=None, database=None):
    settings = settings or Settings()
    _configurar_logging(settings)

    app = Flask(__name__)
    app.config.from_object(settings)
    app.config["SETTINGS"] = settings
    CORS(app, origins=settings.CORS_ORIGINS)

    # --- Infraestrutura ---------------------------------------------------
    database = database or Database(settings.DATABASE_PATH)
    senhas = PasswordService()
    tokens = TokenService(settings.SECRET_KEY)
    notificacoes = NotificacaoService()

    init_database(database, senhas, seed=settings.SEED_ON_STARTUP)
    app.teardown_appcontext(database.fechar)

    # --- Models -----------------------------------------------------------
    produtos = ProdutoModel(database)
    usuarios = UsuarioModel(database)
    pedidos = PedidoModel(database)

    # --- Controllers ------------------------------------------------------
    produto_controller = ProdutoController(produtos)
    usuario_controller = UsuarioController(usuarios, senhas, tokens)
    pedido_controller = PedidoController(pedidos, produtos, usuarios, notificacoes)
    relatorio_controller = RelatorioController(pedidos)
    sistema_controller = SistemaController(produtos, usuarios, pedidos)
    admin_controller = AdminController(database)

    # --- Views ------------------------------------------------------------
    app.register_blueprint(create_sistema_blueprint(sistema_controller))
    app.register_blueprint(create_produto_blueprint(produto_controller))
    app.register_blueprint(create_usuario_blueprint(usuario_controller))
    app.register_blueprint(create_pedido_blueprint(pedido_controller))
    app.register_blueprint(create_relatorio_blueprint(relatorio_controller))
    app.register_blueprint(create_admin_blueprint(admin_controller, settings, tokens))

    register_error_handlers(app)

    if settings.usando_secret_key_padrao:
        logger.warning(
            "SECRET_KEY de desenvolvimento em uso; defina a variável SECRET_KEY em produção"
        )
    if not settings.ADMIN_TOKEN:
        logger.warning("ADMIN_TOKEN não configurado; rotas /admin negarão todo acesso")

    return app


def _configurar_logging(settings):
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL, logging.INFO),
        format="%(asctime)s %(levelname)-8s %(name)s %(message)s",
    )
