"""Relatório de vendas: a política comercial mora aqui, não na persistência."""
from src.config.constants import (
    CASAS_DECIMAIS_MONETARIAS,
    FAIXAS_DESCONTO,
    STATUS_APROVADO,
    STATUS_CANCELADO,
    STATUS_PENDENTE,
)


def desconto_para(faturamento):
    """Primeiro percentual cuja faixa o faturamento alcança; 0 se nenhuma."""
    return next(
        (faturamento * percentual for minimo, percentual in FAIXAS_DESCONTO if faturamento > minimo),
        0,
    )


class RelatorioController:
    def __init__(self, pedidos):
        self.pedidos = pedidos

    def vendas(self):
        resumo = self.pedidos.resumo_vendas()
        total_pedidos = resumo["total_pedidos"]
        faturamento = resumo["faturamento"] or 0
        por_status = resumo["por_status"]
        desconto = desconto_para(faturamento)

        return {
            "total_pedidos": total_pedidos,
            "faturamento_bruto": round(faturamento, CASAS_DECIMAIS_MONETARIAS),
            "desconto_aplicavel": round(desconto, CASAS_DECIMAIS_MONETARIAS),
            "faturamento_liquido": round(faturamento - desconto, CASAS_DECIMAIS_MONETARIAS),
            "pedidos_pendentes": por_status.get(STATUS_PENDENTE, 0),
            "pedidos_aprovados": por_status.get(STATUS_APROVADO, 0),
            "pedidos_cancelados": por_status.get(STATUS_CANCELADO, 0),
            "ticket_medio": (
                round(faturamento / total_pedidos, CASAS_DECIMAIS_MONETARIAS)
                if total_pedidos > 0
                else 0
            ),
        }
