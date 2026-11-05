from sqlalchemy import case, func, or_, select
from sqlalchemy.orm import joinedload

from config.constants import (
    CLOSED_TASK_STATUSES,
    DEFAULT_PRIORITY,
    STATUS_DONE,
    STATUS_PENDING,
    TAG_SEPARATOR,
)
from database import db
from models.base import now_utc


class Task(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), default=STATUS_PENDING)
    priority = db.Column(db.Integer, default=DEFAULT_PRIORITY)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'), nullable=True)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id', ondelete='SET NULL'), nullable=True)
    created_at = db.Column(db.DateTime, default=now_utc)
    updated_at = db.Column(db.DateTime, default=now_utc, onupdate=now_utc)
    due_date = db.Column(db.DateTime, nullable=True)
    tags = db.Column(db.String(500), nullable=True)

    user = db.relationship('User', backref=db.backref('tasks', passive_deletes=True))
    category = db.relationship('Category', backref=db.backref('tasks', passive_deletes=True))

    # --- regras da própria entidade -------------------------------------

    def is_overdue(self, now=None):
        """Única implementação da regra "task atrasada" do sistema."""
        if not self.due_date:
            return False
        return self.due_date < (now or now_utc()) and self.status not in CLOSED_TASK_STATUSES

    def tag_list(self):
        return self.tags.split(TAG_SEPARATOR) if self.tags else []

    def set_tags(self, tags):
        self.tags = TAG_SEPARATOR.join(tags) if isinstance(tags, list) else tags

    # --- cláusula SQL equivalente a is_overdue (usada nas agregações) ----

    @staticmethod
    def _overdue_clause(now):
        return (
            Task.due_date.isnot(None),
            Task.due_date < now,
            Task.status.notin_(tuple(CLOSED_TASK_STATUSES)),
        )

    # --- persistência ----------------------------------------------------

    @staticmethod
    def get_by_id(task_id):
        return db.session.get(Task, task_id)

    @staticmethod
    def list_all(with_relations=False):
        stmt = select(Task).order_by(Task.id)
        if with_relations:
            # Carrega user e category junto: evita 2 queries por task (N+1)
            stmt = stmt.options(joinedload(Task.user), joinedload(Task.category))
        return db.session.scalars(stmt).unique().all()

    @staticmethod
    def list_by_user(user_id):
        return db.session.scalars(select(Task).filter_by(user_id=user_id).order_by(Task.id)).all()

    @staticmethod
    def search(text=None, status=None, priority=None, user_id=None):
        stmt = select(Task)
        if text:
            pattern = f'%{text}%'
            stmt = stmt.where(or_(Task.title.like(pattern), Task.description.like(pattern)))
        if status:
            stmt = stmt.where(Task.status == status)
        if priority is not None:
            stmt = stmt.where(Task.priority == priority)
        if user_id is not None:
            stmt = stmt.where(Task.user_id == user_id)
        return db.session.scalars(stmt.order_by(Task.id)).all()

    @staticmethod
    def count_all():
        return db.session.scalar(select(func.count(Task.id)))

    @staticmethod
    def status_counts():
        """{status: total} numa única query (substitui 4 COUNT(*) separados)."""
        rows = db.session.execute(select(Task.status, func.count(Task.id)).group_by(Task.status)).all()
        return {status: total for status, total in rows}

    @staticmethod
    def priority_counts():
        """{priority: total} numa única query (substitui 5 COUNT(*) separados)."""
        rows = db.session.execute(select(Task.priority, func.count(Task.id)).group_by(Task.priority)).all()
        return {priority: total for priority, total in rows}

    @staticmethod
    def count_overdue(now):
        return db.session.scalar(select(func.count(Task.id)).where(*Task._overdue_clause(now)))

    @staticmethod
    def list_overdue(now):
        return db.session.scalars(select(Task).where(*Task._overdue_clause(now)).order_by(Task.id)).all()

    @staticmethod
    def count_created_since(moment):
        return db.session.scalar(select(func.count(Task.id)).where(Task.created_at >= moment))

    @staticmethod
    def count_completed_since(moment):
        return db.session.scalar(
            select(func.count(Task.id)).where(Task.status == STATUS_DONE, Task.updated_at >= moment)
        )

    @staticmethod
    def totals_by_user():
        """{user_id: (total, concluídas)} numa única query (evita N+1 no relatório)."""
        done_flag = case((Task.status == STATUS_DONE, 1), else_=0)
        rows = db.session.execute(
            select(Task.user_id, func.count(Task.id), func.coalesce(func.sum(done_flag), 0))
            .where(Task.user_id.isnot(None))
            .group_by(Task.user_id)
        ).all()
        return {user_id: (total, done) for user_id, total, done in rows}

    @staticmethod
    def create(**fields):
        task = Task(**fields)
        db.session.add(task)
        db.session.commit()
        return task

    @staticmethod
    def save():
        db.session.commit()

    @staticmethod
    def delete(task):
        db.session.delete(task)
        db.session.commit()

    @staticmethod
    def delete_by_user(user_id, commit=True):
        db.session.execute(db.delete(Task).where(Task.user_id == user_id))
        if commit:
            db.session.commit()

    @staticmethod
    def clear_category(category_id, commit=True):
        db.session.execute(db.update(Task).where(Task.category_id == category_id).values(category_id=None))
        if commit:
            db.session.commit()
