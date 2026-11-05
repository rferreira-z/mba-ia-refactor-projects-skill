"""Validação de entrada, definida uma vez por agregado.

As mensagens de erro são as mesmas do código original, para que os clientes
vejam o contrato inalterado. O que muda é que um tipo errado agora vira
ValidationError (400) em vez de estourar um TypeError (500).
"""
from src.config.constants import (
    CATEGORIA_PADRAO,
    CATEGORIAS_VALIDAS,
    NOME_PRODUTO_MAX,
    NOME_PRODUTO_MIN,
    STATUS_PEDIDO_VALIDOS,
)
from src.errors import ValidationError


def _exigir_dicionario(dados):
    if not isinstance(dados, dict) or not dados:
        raise ValidationError("Dados inválidos")
    return dados


def _numero(valor, mensagem):
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        raise ValidationError(mensagem)
    return valor


def _inteiro(valor, mensagem):
    if isinstance(valor, bool) or not isinstance(valor, int):
        raise ValidationError(mensagem)
    return valor


def validar_produto(dados):
    """Mesmas regras para criação e atualização (antes divergiam)."""
    _exigir_dicionario(dados)

    for campo, mensagem in (
        ("nome", "Nome é obrigatório"),
        ("preco", "Preço é obrigatório"),
        ("estoque", "Estoque é obrigatório"),
    ):
        if campo not in dados:
            raise ValidationError(mensagem)

    nome = dados["nome"]
    if not isinstance(nome, str):
        raise ValidationError("Nome é obrigatório")

    preco = _numero(dados["preco"], "Preço deve ser um número")
    estoque = _inteiro(dados["estoque"], "Estoque deve ser um número inteiro")

    if preco < 0:
        raise ValidationError("Preço não pode ser negativo")
    if estoque < 0:
        raise ValidationError("Estoque não pode ser negativo")
    if len(nome) < NOME_PRODUTO_MIN:
        raise ValidationError("Nome muito curto")
    if len(nome) > NOME_PRODUTO_MAX:
        raise ValidationError("Nome muito longo")

    categoria = dados.get("categoria", CATEGORIA_PADRAO)
    if categoria not in CATEGORIAS_VALIDAS:
        raise ValidationError("Categoria inválida. Válidas: " + str(CATEGORIAS_VALIDAS))

    descricao = dados.get("descricao", "")
    if not isinstance(descricao, str):
        raise ValidationError("Descrição deve ser um texto")

    return {
        "nome": nome,
        "descricao": descricao,
        "preco": preco,
        "estoque": estoque,
        "categoria": categoria,
    }


def validar_filtros_produto(termo, categoria, preco_min, preco_max):
    """Converte os filtros da query string; `0` é um valor válido, não ausência."""
    return {
        "termo": termo or None,
        "categoria": categoria or None,
        "preco_min": _preco_filtro(preco_min, "preco_min"),
        "preco_max": _preco_filtro(preco_max, "preco_max"),
    }


def _preco_filtro(valor, nome_campo):
    if valor is None or valor == "":
        return None
    try:
        return float(valor)
    except (TypeError, ValueError):
        raise ValidationError("Filtro " + nome_campo + " deve ser um número") from None


def validar_novo_usuario(dados):
    _exigir_dicionario(dados)

    nome = dados.get("nome", "")
    email = dados.get("email", "")
    senha = dados.get("senha", "")

    if not nome or not email or not senha:
        raise ValidationError("Nome, email e senha são obrigatórios")
    if not isinstance(email, str) or "@" not in email or "." not in email.split("@")[-1]:
        raise ValidationError("Email inválido")
    if not isinstance(nome, str) or not isinstance(senha, str):
        raise ValidationError("Nome, email e senha são obrigatórios")

    return {"nome": nome, "email": email, "senha": senha}


def validar_credenciais(dados):
    if not isinstance(dados, dict):
        raise ValidationError("Email e senha são obrigatórios")

    email = dados.get("email", "")
    senha = dados.get("senha", "")
    if not email or not senha:
        raise ValidationError("Email e senha são obrigatórios")
    return {"email": email, "senha": senha}


def validar_novo_pedido(dados):
    _exigir_dicionario(dados)

    usuario_id = dados.get("usuario_id")
    itens = dados.get("itens", [])

    if not usuario_id:
        raise ValidationError("Usuario ID é obrigatório")
    if not isinstance(itens, list) or len(itens) == 0:
        raise ValidationError("Pedido deve ter pelo menos 1 item")

    itens_validados = []
    for item in itens:
        if not isinstance(item, dict):
            raise ValidationError("Item do pedido inválido")
        produto_id = item.get("produto_id")
        quantidade = item.get("quantidade")
        if not produto_id:
            raise ValidationError("Item do pedido inválido")
        if not isinstance(quantidade, int) or isinstance(quantidade, bool) or quantidade < 1:
            raise ValidationError("Quantidade do item deve ser um inteiro maior que zero")
        itens_validados.append({"produto_id": produto_id, "quantidade": quantidade})

    return {"usuario_id": usuario_id, "itens": itens_validados}


def validar_status_pedido(dados):
    if not isinstance(dados, dict):
        raise ValidationError("Status inválido")

    novo_status = dados.get("status", "")
    if novo_status not in STATUS_PEDIDO_VALIDOS:
        raise ValidationError("Status inválido")
    return novo_status
