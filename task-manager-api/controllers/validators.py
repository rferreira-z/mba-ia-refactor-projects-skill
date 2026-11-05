"""Validação de entrada — uma única definição por regra, usada por create e update.

Todas as checagens são tolerantes a tipo: um campo com o tipo errado vira
`ValidationError` (400) em vez de estourar uma exceção não tratada (500).
"""
import re
from datetime import datetime

from config.constants import (
    DATE_FORMAT,
    EMAIL_PATTERN,
    MAX_PRIORITY,
    MAX_TITLE_LENGTH,
    MIN_PASSWORD_LENGTH,
    MIN_PRIORITY,
    MIN_TITLE_LENGTH,
    TASK_STATUSES,
    USER_ROLES,
)
from errors import ValidationError

_EMAIL_RE = re.compile(EMAIL_PATTERN)


def ensure_payload(data):
    if not isinstance(data, dict) or not data:
        raise ValidationError('Dados inválidos')
    return data


# --- campos de task -----------------------------------------------------

def validate_title(value, required_message='Título é obrigatório'):
    if not isinstance(value, str) or not value:
        raise ValidationError(required_message)
    if len(value) < MIN_TITLE_LENGTH:
        raise ValidationError('Título muito curto')
    if len(value) > MAX_TITLE_LENGTH:
        raise ValidationError('Título muito longo')
    return value


def validate_status(value):
    if value not in TASK_STATUSES:
        raise ValidationError('Status inválido')
    return value


def validate_priority(value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValidationError('Prioridade deve ser entre 1 e 5')
    if value < MIN_PRIORITY or value > MAX_PRIORITY:
        raise ValidationError('Prioridade deve ser entre 1 e 5')
    return value


def validate_due_date(value, message='Formato de data inválido'):
    if not isinstance(value, str):
        raise ValidationError(message)
    try:
        return datetime.strptime(value, DATE_FORMAT)
    except ValueError:
        raise ValidationError(message)


def validate_tags(value):
    if value is None:
        return None
    if isinstance(value, list):
        if not all(isinstance(tag, str) for tag in value):
            raise ValidationError('Tags inválidas')
        return value
    if isinstance(value, str):
        return value
    raise ValidationError('Tags inválidas')


def validate_optional_int(value, message):
    """Converte um parâmetro de query/corpo em int, ou falha com 400."""
    if value is None or value == '':
        return None
    if isinstance(value, bool):
        raise ValidationError(message)
    if isinstance(value, int):
        return value
    try:
        return int(str(value))
    except (TypeError, ValueError):
        raise ValidationError(message)


# --- campos de usuário --------------------------------------------------

def validate_name(value, message='Nome é obrigatório'):
    if not isinstance(value, str) or not value.strip():
        raise ValidationError(message)
    return value


def validate_email(value):
    if not isinstance(value, str) or not _EMAIL_RE.match(value):
        raise ValidationError('Email inválido')
    return value


def validate_password(value, message):
    if not isinstance(value, str) or len(value) < MIN_PASSWORD_LENGTH:
        raise ValidationError(message)
    return value


def validate_role(value):
    if value not in USER_ROLES:
        raise ValidationError('Role inválido')
    return value


def validate_active(value):
    if not isinstance(value, bool):
        raise ValidationError('Campo active deve ser booleano')
    return value
