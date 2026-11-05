"""Notificações ao cliente (e-mail / SMS / push).

Implementação de desenvolvimento: registra no logger em vez de enviar.
Fica isolada atrás desta interface para que uma implementação real possa
substituí-la por injeção de dependência, sem tocar nos controllers.
"""
import logging

from src.config.constants import STATUS_APROVADO, STATUS_CANCELADO

logger = logging.getLogger(__name__)


class NotificacaoService:
    def pedido_criado(self, pedido_id, usuario_id):
        logger.info("notificacao.email pedido_id=%s usuario_id=%s", pedido_id, usuario_id)
        logger.info("notificacao.sms pedido_id=%s evento=pedido_recebido", pedido_id)
        logger.info("notificacao.push pedido_id=%s evento=novo_pedido", pedido_id)

    def status_alterado(self, pedido_id, novo_status):
        if novo_status == STATUS_APROVADO:
            logger.info("notificacao.pedido_aprovado pedido_id=%s acao=preparar_envio", pedido_id)
        elif novo_status == STATUS_CANCELADO:
            logger.info("notificacao.pedido_cancelado pedido_id=%s acao=devolver_estoque", pedido_id)
