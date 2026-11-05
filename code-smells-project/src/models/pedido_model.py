"""Persistência de pedidos e seus itens.

A criação do pedido roda em uma transação única com baixa atômica de estoque;
a listagem carrega todos os itens em duas consultas, não em N+1.
"""
from collections import defaultdict

from src.config.constants import PRODUTO_REMOVIDO, STATUS_PENDENTE
from src.errors import ValidationError


class PedidoModel:
    CAMPOS_PUBLICOS = ("id", "usuario_id", "status", "total", "criado_em")

    def __init__(self, database):
        self.db = database

    @classmethod
    def _to_dict(cls, row):
        return {campo: row[campo] for campo in cls.CAMPOS_PUBLICOS} if row else None

    def criar_com_itens(self, usuario_id, itens, total):
        """Insere pedido + itens e debita o estoque, tudo em uma transação.

        `itens` traz `produto_id`, `quantidade`, `preco_unitario` e `nome`.
        A baixa usa `WHERE estoque >= ?` para que duas requisições simultâneas
        não possam vender a mesma unidade.
        """
        with self.db.transacao() as conexao:
            cursor = conexao.execute(
                "INSERT INTO pedidos (usuario_id, status, total) VALUES (?, ?, ?)",
                (usuario_id, STATUS_PENDENTE, total),
            )
            pedido_id = cursor.lastrowid

            # Uma baixa por item: cada uma precisa do próprio rowcount para
            # identificar qual produto ficou sem estoque. São N itens de um
            # pedido, não uma varredura sobre um resultado ilimitado.
            for item in itens:
                baixa = conexao.execute(
                    "UPDATE produtos SET estoque = estoque - ? WHERE id = ? AND estoque >= ?",
                    (item["quantidade"], item["produto_id"], item["quantidade"]),
                )
                if baixa.rowcount != 1:
                    raise ValidationError("Estoque insuficiente para " + item["nome"])

            conexao.executemany(
                "INSERT INTO itens_pedido (pedido_id, produto_id, quantidade, preco_unitario)"
                " VALUES (?, ?, ?, ?)",
                [
                    (pedido_id, item["produto_id"], item["quantidade"], item["preco_unitario"])
                    for item in itens
                ],
            )
        return {"pedido_id": pedido_id, "total": total}

    def listar(self, usuario_id=None):
        """Lista pedidos com seus itens. Uma consulta de pedidos + uma de itens."""
        if usuario_id is None:
            rows = self.db.query_all("SELECT * FROM pedidos ORDER BY id")
        else:
            rows = self.db.query_all(
                "SELECT * FROM pedidos WHERE usuario_id = ? ORDER BY id", (usuario_id,)
            )

        pedidos = [self._to_dict(row) for row in rows]
        if not pedidos:
            return pedidos

        itens_por_pedido = self._carregar_itens([pedido["id"] for pedido in pedidos])
        for pedido in pedidos:
            pedido["itens"] = itens_por_pedido[pedido["id"]]
        return pedidos

    def _carregar_itens(self, pedido_ids):
        marcadores = ",".join("?" * len(pedido_ids))
        rows = self.db.query_all(
            "SELECT i.pedido_id, i.produto_id, i.quantidade, i.preco_unitario, p.nome AS produto_nome"
            " FROM itens_pedido i"
            " LEFT JOIN produtos p ON p.id = i.produto_id"
            " WHERE i.pedido_id IN (" + marcadores + ")"
            " ORDER BY i.id",
            list(pedido_ids),
        )
        agrupados = defaultdict(list)
        for row in rows:
            agrupados[row["pedido_id"]].append(
                {
                    "produto_id": row["produto_id"],
                    "produto_nome": row["produto_nome"] or PRODUTO_REMOVIDO,
                    "quantidade": row["quantidade"],
                    "preco_unitario": row["preco_unitario"],
                }
            )
        return agrupados

    def existe(self, pedido_id):
        return self.db.query_one("SELECT 1 FROM pedidos WHERE id = ?", (pedido_id,)) is not None

    def atualizar_status(self, pedido_id, novo_status):
        cursor = self.db.execute(
            "UPDATE pedidos SET status = ? WHERE id = ?", (novo_status, pedido_id)
        )
        return cursor.rowcount == 1

    def contar(self):
        return self.db.query_one("SELECT COUNT(*) AS total FROM pedidos")["total"]

    def resumo_vendas(self):
        """Agregados de vendas em duas consultas (antes eram cinco COUNT separados)."""
        totais = self.db.query_one(
            "SELECT COUNT(*) AS total_pedidos, COALESCE(SUM(total), 0) AS faturamento FROM pedidos"
        )
        por_status = {
            row["status"]: row["quantidade"]
            for row in self.db.query_all(
                "SELECT status, COUNT(*) AS quantidade FROM pedidos GROUP BY status"
            )
        }
        return {
            "total_pedidos": totais["total_pedidos"],
            "faturamento": totais["faturamento"],
            "por_status": por_status,
        }
