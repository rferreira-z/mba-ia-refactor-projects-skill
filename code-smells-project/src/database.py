"""Acesso ao SQLite: conexão por requisição, schema e seed.

Substitui o antigo singleton global (`global db_connection` +
`check_same_thread=False`). Cada requisição recebe a sua conexão, guardada
no contexto de aplicação do Flask e fechada no teardown.
"""
import logging
import sqlite3
from contextlib import contextmanager

from flask import g

from src.config.constants import CATEGORIA_PADRAO, STATUS_PENDENTE, TIPO_USUARIO_ADMIN, TIPO_USUARIO_PADRAO

logger = logging.getLogger(__name__)

_CHAVE_CONEXAO = "_loja_db_connection"

SCHEMA = """
CREATE TABLE IF NOT EXISTS produtos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    descricao TEXT,
    preco REAL NOT NULL,
    estoque INTEGER NOT NULL,
    categoria TEXT,
    ativo INTEGER DEFAULT 1,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS usuarios (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT NOT NULL UNIQUE,
    senha TEXT NOT NULL,
    tipo TEXT NOT NULL DEFAULT 'cliente',
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS pedidos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    usuario_id INTEGER NOT NULL REFERENCES usuarios(id),
    status TEXT NOT NULL DEFAULT 'pendente',
    total REAL NOT NULL,
    criado_em TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS itens_pedido (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    pedido_id INTEGER NOT NULL REFERENCES pedidos(id) ON DELETE CASCADE,
    produto_id INTEGER NOT NULL REFERENCES produtos(id),
    quantidade INTEGER NOT NULL,
    preco_unitario REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_pedidos_usuario ON pedidos(usuario_id);
CREATE INDEX IF NOT EXISTS idx_itens_pedido_pedido ON itens_pedido(pedido_id);
CREATE INDEX IF NOT EXISTS idx_produtos_categoria ON produtos(categoria);
"""

PRODUTOS_SEED = [
    ("Notebook Gamer", "Notebook potente para jogos", 5999.99, 10, "informatica"),
    ("Mouse Wireless", "Mouse sem fio ergonômico", 89.90, 50, "informatica"),
    ("Teclado Mecânico", "Teclado mecânico RGB", 299.90, 30, "informatica"),
    ("Monitor 27''", "Monitor 27 polegadas 144hz", 1899.90, 15, "informatica"),
    ("Headset Gamer", "Headset com microfone", 199.90, 25, "informatica"),
    ("Cadeira Gamer", "Cadeira ergonômica", 1299.90, 8, "moveis"),
    ("Webcam HD", "Webcam 1080p", 249.90, 20, "informatica"),
    ("Hub USB", "Hub USB 3.0 7 portas", 79.90, 40, "informatica"),
    ("SSD 1TB", "SSD NVMe 1TB", 449.90, 35, "informatica"),
    ("Camiseta Dev", "Camiseta estampa código", 59.90, 100, "vestuario"),
]

# Credenciais de demonstração: senhas passam pelo mesmo hasher da aplicação.
USUARIOS_SEED = [
    ("Admin", "admin@loja.com", "admin123", TIPO_USUARIO_ADMIN),
    ("João Silva", "joao@email.com", "123456", TIPO_USUARIO_PADRAO),
    ("Maria Santos", "maria@email.com", "senha123", TIPO_USUARIO_PADRAO),
]


class Database:
    """Fábrica de conexões SQLite com escopo de requisição."""

    def __init__(self, path):
        self.path = path

    def nova_conexao(self):
        """Conexão avulsa, usada no bootstrap (fora de um contexto de app)."""
        conexao = sqlite3.connect(self.path)
        conexao.row_factory = sqlite3.Row
        conexao.execute("PRAGMA foreign_keys = ON")
        return conexao

    @property
    def conexao(self):
        """Conexão da requisição atual, criada sob demanda."""
        conexao = g.get(_CHAVE_CONEXAO)
        if conexao is None:
            conexao = self.nova_conexao()
            setattr(g, _CHAVE_CONEXAO, conexao)
        return conexao

    def fechar(self, _excecao=None):
        conexao = g.pop(_CHAVE_CONEXAO, None)
        if conexao is not None:
            conexao.close()

    # --- Operações ---------------------------------------------------------
    def query_all(self, sql, params=()):
        return self.conexao.execute(sql, params).fetchall()

    def query_one(self, sql, params=()):
        return self.conexao.execute(sql, params).fetchone()

    def execute(self, sql, params=()):
        conexao = self.conexao
        try:
            cursor = conexao.execute(sql, params)
            conexao.commit()
            return cursor
        except Exception:
            conexao.rollback()
            raise

    @contextmanager
    def transacao(self):
        """Agrupa várias escritas: commit no sucesso, rollback em qualquer erro."""
        conexao = self.conexao
        try:
            yield conexao
            conexao.commit()
        except Exception:
            conexao.rollback()
            raise


def init_database(database, password_service, seed=True):
    """Cria o schema e, se a base estiver vazia, popula os dados de exemplo."""
    conexao = database.nova_conexao()
    try:
        conexao.executescript(SCHEMA)
        if seed and conexao.execute("SELECT COUNT(*) FROM produtos").fetchone()[0] == 0:
            _popular(conexao, password_service)
        conexao.commit()
    finally:
        conexao.close()


def _popular(conexao, password_service):
    conexao.executemany(
        "INSERT INTO produtos (nome, descricao, preco, estoque, categoria) VALUES (?, ?, ?, ?, ?)",
        PRODUTOS_SEED,
    )
    conexao.executemany(
        "INSERT INTO usuarios (nome, email, senha, tipo) VALUES (?, ?, ?, ?)",
        [
            (nome, email, password_service.gerar_hash(senha), tipo)
            for nome, email, senha, tipo in USUARIOS_SEED
        ],
    )
    logger.info(
        "Banco populado: %s produtos, %s usuários (categoria padrão=%s, status padrão=%s)",
        len(PRODUTOS_SEED),
        len(USUARIOS_SEED),
        CATEGORIA_PADRAO,
        STATUS_PENDENTE,
    )
