"""Casos de uso de categorias."""
from config.constants import DEFAULT_CATEGORY_COLOR
from controllers import validators
from errors import NotFoundError
from models.category import Category


def _get_category_or_404(category_id):
    category = Category.get_by_id(category_id)
    if not category:
        raise NotFoundError('Categoria não encontrada')
    return category


def list_categories():
    """Devolve [(categoria, total_de_tasks)] com uma única query agregada."""
    counts = Category.task_counts()
    return [(category, counts.get(category.id, 0)) for category in Category.list_all()]


def create_category(data):
    validators.ensure_payload(data)
    name = validators.validate_name(data.get('name'))
    return Category.create(
        name=name,
        description=data.get('description', ''),
        color=data.get('color', DEFAULT_CATEGORY_COLOR),
    )


def update_category(category_id, data):
    category = _get_category_or_404(category_id)
    validators.ensure_payload(data)

    if 'name' in data:
        category.name = validators.validate_name(data['name'])
    if 'description' in data:
        category.description = data['description']
    if 'color' in data:
        category.color = data['color']

    Category.save()
    return category


def delete_category(category_id):
    """Remove a categoria e desassocia suas tasks na mesma transação."""
    Category.delete_and_detach_tasks(_get_category_or_404(category_id))
