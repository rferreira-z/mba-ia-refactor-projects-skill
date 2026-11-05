"""Operações administrativas.

O endpoint de consulta deixou de aceitar SQL arbitrário: só um único SELECT
somente-leitura passa. Ambas as operações exigem o guard de admin na View.
"""
import logging
import re

from src.errors import ValidationError

logger = logging.getLogger(__name__)

_SELECT = re.compile(r"^select\b", re.IGNORECASE)

# Ordem importa: filhos antes dos pais, por causa das foreign keys.
TABELAS_RESET = ("itens_pedido", "pedidos", "produtos", "usuarios")


class AdminController:
    def __init__(self, database):
        self.db = database

    def resetar_banco(self):
        with self.db.transacao() as conexao:
            conexao.execute("DELETE FROM itens_pedido")
            conexao.execute("DELETE FROM pedidos")
            conexao.execute("DELETE FROM produtos")
            conexao.execute("DELETE FROM usuarios")
        logger.warning("admin.reset_db tabelas=%s", ",".join(TABELAS_RESET))

    def consultar(self, sql):
        consulta = self._validar_consulta(sql)
        return [dict(row) for row in self.db.query_all(consulta)]

    @staticmethod
    def _validar_consulta(sql):
        if not sql or not str(sql).strip():
            raise ValidationError("Query não informada")

        consulta = str(sql).strip().rstrip(";").strip()
        if ";" in consulta:
            raise ValidationError("Apenas uma instrução é permitida")
        if not _SELECT.match(consulta):
            raise ValidationError("Apenas consultas SELECT são permitidas")
        return consulta
