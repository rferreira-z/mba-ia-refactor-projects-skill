"""Constantes de domínio — única fonte de verdade para regras e limites."""

# Status de task
STATUS_PENDING = 'pending'
STATUS_IN_PROGRESS = 'in_progress'
STATUS_DONE = 'done'
STATUS_CANCELLED = 'cancelled'

TASK_STATUSES = (STATUS_PENDING, STATUS_IN_PROGRESS, STATUS_DONE, STATUS_CANCELLED)
# Status em que uma task não pode mais ser considerada atrasada
CLOSED_TASK_STATUSES = frozenset({STATUS_DONE, STATUS_CANCELLED})

# Papéis de usuário
ROLE_USER = 'user'
ROLE_ADMIN = 'admin'
ROLE_MANAGER = 'manager'

USER_ROLES = (ROLE_USER, ROLE_ADMIN, ROLE_MANAGER)
DEFAULT_USER_ROLE = ROLE_USER

# Limites de validação
MIN_TITLE_LENGTH = 3
MAX_TITLE_LENGTH = 200
MIN_PASSWORD_LENGTH = 4

MIN_PRIORITY = 1
MAX_PRIORITY = 5
DEFAULT_PRIORITY = 3
# Prioridade <= este valor conta como "alta prioridade" nos relatórios
HIGH_PRIORITY_THRESHOLD = 2

PRIORITY_LABELS = {1: 'critical', 2: 'high', 3: 'medium', 4: 'low', 5: 'minimal'}

# Categorias
DEFAULT_CATEGORY_COLOR = '#000000'

# Formatos e separadores
DATE_FORMAT = '%Y-%m-%d'
TAG_SEPARATOR = ','
EMAIL_PATTERN = r'^[a-zA-Z0-9+_.-]+@[a-zA-Z0-9.-]+$'

# Janela usada em "recent activity" no relatório geral
RECENT_ACTIVITY_DAYS = 7
