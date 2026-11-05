"""Persistência de produtos. Sem Flask, sem regra de negócio."""
import sqlite3

from src.errors import ConflictError


class ProdutoModel:
    CAMPOS_PUBLICOS = ("id", "nome", "descricao", "preco", "estoque", "categoria", "ativo", "criado_em")

    def __init__(self, database):
        self.db = database

    @classmethod
    def _to_dict(cls, row):
        """Mapeamento linha -> dict, definido uma única vez."""
        return {campo: row[campo] for campo in cls.CAMPOS_PUBLICOS} if row else None

    def listar(self):
        return [self._to_dict(row) for row in self.db.query_all("SELECT * FROM produtos ORDER BY id")]

    def buscar_por_id(self, produto_id):
        return self._to_dict(self.db.query_one("SELECT * FROM produtos WHERE id = ?", (produto_id,)))

    def buscar_varios_por_ids(self, produto_ids):
        """Carrega vários produtos em uma consulta só (evita N+1)."""
        if not produto_ids:
            return {}
        marcadores = ",".join("?" * len(produto_ids))
        rows = self.db.query_all(
            "SELECT * FROM produtos WHERE id IN (" + marcadores + ")", list(produto_ids)
        )
        return {row["id"]: self._to_dict(row) for row in rows}

    def buscar(self, termo=None, categoria=None, preco_min=None, preco_max=None):
        """Busca com filtros opcionais; só os marcadores `?` entram no SQL."""
        condicoes = ["1=1"]
        params = []
        if termo:
            condicoes.append("(nome LIKE ? OR descricao LIKE ?)")
            params.extend(["%" + termo + "%", "%" + termo + "%"])
        if categoria:
            condicoes.append("categoria = ?")
            params.append(categoria)
        if preco_min is not None:
            condicoes.append("preco >= ?")
            params.append(preco_min)
        if preco_max is not None:
            condicoes.append("preco <= ?")
            params.append(preco_max)

        sql = "SELECT * FROM produtos WHERE " + " AND ".join(condicoes) + " ORDER BY id"
        return [self._to_dict(row) for row in self.db.query_all(sql, params)]

    def criar(self, nome, descricao, preco, estoque, categoria):
        cursor = self.db.execute(
            "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
            (nome, descricao, preco, estoque, categoria),
        )
        return cursor.lastrowid

    def atualizar(self, produto_id, nome, descricao, preco, estoque, categoria):
        self.db.execute(
            "UPDATE produtos SET nome = ?, descricao = ?, preco = ?, estoque = ?, categoria = ? WHERE id = ?",
            (nome, descricao, preco, estoque, categoria, produto_id),
        )
        return True

    def deletar(self, produto_id):
        try:
            self.db.execute("DELETE FROM produtos WHERE id = ?", (produto_id,))
        except sqlite3.IntegrityError as erro:
            raise ConflictError(
                "Produto está vinculado a pedidos e não pode ser removido"
            ) from erro
        return True

    def contar(self):
        return self.db.query_one("SELECT COUNT(*) AS total FROM produtos")["total"]
