"""Casos de uso de usuários."""
from config.constants import DEFAULT_USER_ROLE
from controllers import validators
from errors import ConflictError, ForbiddenError, NotFoundError, ValidationError
from models.task import Task
from models.user import User

REQUIRED_CREATE_FIELDS = (
    ('name', 'Nome é obrigatório'),
    ('email', 'Email é obrigatório'),
    ('password', 'Senha é obrigatória'),
)


def _get_user_or_404(user_id):
    user = User.get_by_id(user_id)
    if not user:
        raise NotFoundError('Usuário não encontrado')
    return user


def _ensure_can_manage(identity, user_id):
    """Só o próprio usuário ou um admin altera um cadastro."""
    if identity is None or not (identity.is_admin or identity.user_id == user_id):
        raise ForbiddenError('Acesso negado')


def _ensure_admin(identity, message):
    if identity is None or not identity.is_admin:
        raise ForbiddenError(message)


def list_users():
    users = User.list_all()
    # Uma query agregada em vez de carregar as tasks de cada usuário (N+1)
    totals = Task.totals_by_user()
    return [(user, totals.get(user.id, (0, 0))[0]) for user in users]


def get_user(user_id):
    user = _get_user_or_404(user_id)
    return user, Task.list_by_user(user_id)


def get_user_tasks(user_id):
    _get_user_or_404(user_id)
    return Task.list_by_user(user_id)


def create_user(data, identity=None):
    validators.ensure_payload(data)

    for field, message in REQUIRED_CREATE_FIELDS:
        if not data.get(field):
            raise ValidationError(message)

    name = validators.validate_name(data['name'])
    email = validators.validate_email(data['email'])
    password = validators.validate_password(data['password'], 'Senha deve ter no mínimo 4 caracteres')
    role = validators.validate_role(data.get('role', DEFAULT_USER_ROLE))

    # Cadastro anônimo (ou de não-admin) nunca concede papel privilegiado
    if role != DEFAULT_USER_ROLE and (identity is None or not identity.is_admin):
        role = DEFAULT_USER_ROLE

    if User.email_taken(email):
        raise ConflictError('Email já cadastrado')

    return User.create(name=name, email=email, raw_password=password, role=role)


def update_user(user_id, data, identity=None):
    user = _get_user_or_404(user_id)
    _ensure_can_manage(identity, user_id)
    validators.ensure_payload(data)

    if 'name' in data:
        user.name = validators.validate_name(data['name'])

    if 'email' in data:
        email = validators.validate_email(data['email'])
        if User.email_taken(email, ignore_user_id=user_id):
            raise ConflictError('Email já cadastrado')
        user.email = email

    if 'password' in data:
        user.set_password(validators.validate_password(data['password'], 'Senha muito curta'))

    if 'role' in data:
        role = validators.validate_role(data['role'])
        _ensure_admin(identity, 'Apenas administradores alteram o papel de um usuário')
        user.role = role

    if 'active' in data:
        _ensure_admin(identity, 'Apenas administradores ativam ou desativam usuários')
        user.active = validators.validate_active(data['active'])

    User.save()
    return user


def delete_user(user_id):
    """Remove o usuário e suas tasks numa única transação."""
    User.delete_with_tasks(_get_user_or_404(user_id))
