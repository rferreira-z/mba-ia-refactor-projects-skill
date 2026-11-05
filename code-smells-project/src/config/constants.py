"""Constantes de domínio da loja (camada CONFIG).

Toda regra expressa como número ou string literal mora aqui, em um lugar só.
"""

API_VERSION = "1.0.0"

# --- Produtos -------------------------------------------------------------
CATEGORIA_PADRAO = "geral"
CATEGORIAS_VALIDAS = ["informatica", "moveis", "vestuario", "geral", "eletronicos", "livros"]
NOME_PRODUTO_MIN = 2
NOME_PRODUTO_MAX = 200
PRODUTO_REMOVIDO = "Desconhecido"

# --- Usuários -------------------------------------------------------------
TIPO_USUARIO_PADRAO = "cliente"
TIPO_USUARIO_ADMIN = "admin"

# --- Pedidos --------------------------------------------------------------
STATUS_PENDENTE = "pendente"
STATUS_APROVADO = "aprovado"
STATUS_ENVIADO = "enviado"
STATUS_ENTREGUE = "entregue"
STATUS_CANCELADO = "cancelado"
STATUS_PEDIDO_VALIDOS = [
    STATUS_PENDENTE,
    STATUS_APROVADO,
    STATUS_ENVIADO,
    STATUS_ENTREGUE,
    STATUS_CANCELADO,
]

# --- Relatório de vendas --------------------------------------------------
# (faturamento mínimo, percentual de desconto), em ordem decrescente.
FAIXAS_DESCONTO = ((10000, 0.10), (5000, 0.05), (1000, 0.02))
CASAS_DECIMAIS_MONETARIAS = 2
