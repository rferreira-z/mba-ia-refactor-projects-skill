"""Endpoints de sistema: índice da API e health check.

O health devolve apenas estado operacional — nunca segredo, caminho de
arquivo ou flag de configuração.
"""
from src.config.constants import API_VERSION


class SistemaController:
    def __init__(self, produtos, usuarios, pedidos):
        self.produtos = produtos
        self.usuarios = usuarios
        self.pedidos = pedidos

    def indice(self):
        return {
            "mensagem": "Bem-vindo à API da Loja",
            "versao": API_VERSION,
            "endpoints": {
                "produtos": "/produtos",
                "usuarios": "/usuarios",
                "pedidos": "/pedidos",
                "login": "/login",
                "relatorios": "/relatorios/vendas",
                "health": "/health",
            },
        }

    def health(self):
        return {
            "status": "ok",
            "database": "connected",
            "counts": {
                "produtos": self.produtos.contar(),
                "usuarios": self.usuarios.contar(),
                "pedidos": self.pedidos.contar(),
            },
            "versao": API_VERSION,
        }
