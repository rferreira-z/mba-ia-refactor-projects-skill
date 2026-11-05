"""Casos de uso de produto. Não conhece HTTP nem SQL."""
import logging

from src.controllers.validators import validar_filtros_produto, validar_produto
from src.errors import NotFoundError

logger = logging.getLogger(__name__)


class ProdutoController:
    def __init__(self, produtos):
        self.produtos = produtos

    def listar(self):
        produtos = self.produtos.listar()
        logger.info("produto.listar total=%s", len(produtos))
        return produtos

    def obter(self, produto_id):
        produto = self.produtos.buscar_por_id(produto_id)
        if produto is None:
            raise NotFoundError("Produto não encontrado")
        return produto

    def buscar(self, termo, categoria, preco_min, preco_max):
        filtros = validar_filtros_produto(termo, categoria, preco_min, preco_max)
        return self.produtos.buscar(**filtros)

    def criar(self, dados):
        produto = validar_produto(dados)
        produto_id = self.produtos.criar(**produto)
        logger.info("produto.criado id=%s", produto_id)
        return produto_id

    def atualizar(self, produto_id, dados):
        # A existência é verificada antes da validação, como no contrato original.
        if self.produtos.buscar_por_id(produto_id) is None:
            raise NotFoundError("Produto não encontrado")
        produto = validar_produto(dados)
        self.produtos.atualizar(produto_id, **produto)
        logger.info("produto.atualizado id=%s", produto_id)

    def deletar(self, produto_id):
        if self.produtos.buscar_por_id(produto_id) is None:
            raise NotFoundError("Produto não encontrado")
        self.produtos.deletar(produto_id)
        logger.info("produto.deletado id=%s", produto_id)
