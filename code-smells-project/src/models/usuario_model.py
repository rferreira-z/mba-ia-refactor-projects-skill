"""Persistência de usuários.

`CAMPOS_PUBLICOS` é uma allow-list: o hash da senha nunca sai daqui, exceto
pelo método explícito `buscar_credenciais_por_email`, usado só na autenticação.
"""
import sqlite3

from src.errors import ConflictError


class UsuarioModel:
    CAMPOS_PUBLICOS = ("id", "nome", "email", "tipo", "criado_em")
    CAMPOS_SESSAO = ("id", "nome", "email", "tipo")

    def __init__(self, database):
        self.db = database

    @classmethod
    def _to_dict(cls, row, campos=None):
        campos = campos or cls.CAMPOS_PUBLICOS
        return {campo: row[campo] for campo in campos} if row else None

    def listar(self):
        return [self._to_dict(row) for row in self.db.query_all("SELECT * FROM usuarios ORDER BY id")]

    def buscar_por_id(self, usuario_id):
        return self._to_dict(self.db.query_one("SELECT * FROM usuarios WHERE id = ?", (usuario_id,)))

    def existe(self, usuario_id):
        return self.db.query_one("SELECT 1 FROM usuarios WHERE id = ?", (usuario_id,)) is not None

    def buscar_credenciais_por_email(self, email):
        """Retorna os dados de sessão + o hash armazenado, para verificação em código."""
        row = self.db.query_one("SELECT * FROM usuarios WHERE email = ?", (email,))
        if row is None:
            return None
        return {"usuario": self._to_dict(row, self.CAMPOS_SESSAO), "senha_hash": row["senha"]}

    def criar(self, nome, email, senha_hash, tipo):
        try:
            cursor = self.db.execute(
                "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
                (nome, email, senha_hash, tipo),
            )
        except sqlite3.IntegrityError as erro:
            raise ConflictError("Email já cadastrado") from erro
        return cursor.lastrowid

    def contar(self):
        return self.db.query_one("SELECT COUNT(*) AS total FROM usuarios")["total"]
