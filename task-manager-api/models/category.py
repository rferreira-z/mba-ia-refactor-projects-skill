from sqlalchemy import func, select

from config.constants import DEFAULT_CATEGORY_COLOR
from database import db
from models.base import now_utc


class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(300), nullable=True)
    color = db.Column(db.String(7), default=DEFAULT_CATEGORY_COLOR)
    created_at = db.Column(db.DateTime, default=now_utc)

    # --- persistência ----------------------------------------------------

    @staticmethod
    def get_by_id(category_id):
        return db.session.get(Category, category_id)

    @staticmethod
    def list_all():
        return db.session.scalars(select(Category).order_by(Category.id)).all()

    @staticmethod
    def task_counts():
        """{category_id: total_de_tasks} numa única query (evita N+1)."""
        from models.task import Task

        rows = db.session.execute(
            select(Task.category_id, func.count(Task.id))
            .where(Task.category_id.isnot(None))
            .group_by(Task.category_id)
        ).all()
        return {category_id: total for category_id, total in rows}

    @staticmethod
    def create(name, description, color):
        category = Category(name=name, description=description, color=color)
        db.session.add(category)
        db.session.commit()
        return category

    @staticmethod
    def save():
        db.session.commit()

    @staticmethod
    def delete_and_detach_tasks(category):
        """Remove a categoria e desassocia as tasks numa única transação.

        O `UPDATE` explícito garante consistência mesmo para tasks que não
        estejam carregadas na sessão (o nullify do ORM só alcança as carregadas).
        """
        from models.task import Task

        Task.clear_category(category.id, commit=False)
        db.session.delete(category)
        db.session.commit()
