"""Casos de uso de pedido: valida estoque, orquestra a transação e notifica."""
import logging

from src.controllers.validators import validar_novo_pedido, validar_status_pedido
from src.errors import NotFoundError, ValidationError

logger = logging.getLogger(__name__)


class PedidoController:
    def __init__(self, pedidos, produtos, usuarios, notificacoes):
        self.pedidos = pedidos
        self.produtos = produtos
        self.usuarios = usuarios
        self.notificacoes = notificacoes

    def criar(self, dados):
        pedido = validar_novo_pedido(dados)
        usuario_id = pedido["usuario_id"]

        if not self.usuarios.existe(usuario_id):
            raise ValidationError("Usuário " + str(usuario_id) + " não encontrado")

        itens, total = self._montar_itens(pedido["itens"])
        resultado = self.pedidos.criar_com_itens(usuario_id, itens, total)

        self.notificacoes.pedido_criado(resultado["pedido_id"], usuario_id)
        logger.info("pedido.criado id=%s total=%s", resultado["pedido_id"], total)
        return resultado

    def _montar_itens(self, itens):
        """Carrega todos os produtos de uma vez e aplica as regras de estoque."""
        catalogo = self.produtos.buscar_varios_por_ids({item["produto_id"] for item in itens})

        itens_completos = []
        total = 0
        for item in itens:
            produto = catalogo.get(item["produto_id"])
            if produto is None:
                raise ValidationError("Produto " + str(item["produto_id"]) + " não encontrado")
            if produto["estoque"] < item["quantidade"]:
                raise ValidationError("Estoque insuficiente para " + produto["nome"])

            total = total + (produto["preco"] * item["quantidade"])
            itens_completos.append(
                {
                    "produto_id": produto["id"],
                    "nome": produto["nome"],
                    "quantidade": item["quantidade"],
                    "preco_unitario": produto["preco"],
                }
            )
        return itens_completos, total

    def listar(self):
        return self.pedidos.listar()

    def listar_do_usuario(self, usuario_id):
        return self.pedidos.listar(usuario_id)

    def atualizar_status(self, pedido_id, dados):
        novo_status = validar_status_pedido(dados)

        if not self.pedidos.atualizar_status(pedido_id, novo_status):
            raise NotFoundError("Pedido não encontrado")

        self.notificacoes.status_alterado(pedido_id, novo_status)
        logger.info("pedido.status_atualizado id=%s status=%s", pedido_id, novo_status)
