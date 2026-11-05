"""Helpers compartilhados pelos models."""
from datetime import datetime, timezone


def now_utc():
    """UTC atual como datetime *naive*.

    As colunas do schema são `DateTime` sem timezone, então mantemos os valores
    naive para evitar comparações entre datetimes aware e naive. Substitui a
    função de UTC depreciada no Python 3.12+, construída sobre `datetime.now`.
    """
    return datetime.now(timezone.utc).replace(tzinfo=None)
