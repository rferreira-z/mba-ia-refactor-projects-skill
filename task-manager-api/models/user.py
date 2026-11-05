from sqlalchemy import select

from config.constants import DEFAULT_USER_ROLE, ROLE_ADMIN
from database import db
from models.base import now_utc
from services.password_hasher import hash_password, verify_password


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(50), default=DEFAULT_USER_ROLE)
    active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=now_utc)

    # --- regras da própria entidade -------------------------------------

    def set_password(self, raw_password):
        """Armazena a senha com hash lento e salgado (nunca em texto puro)."""
        self.password = hash_password(raw_password)

    def check_password(self, raw_password):
        return verify_password(self.password, raw_password)

    def is_admin(self):
        return self.role == ROLE_ADMIN

    # --- persistência ----------------------------------------------------

    @staticmethod
    def get_by_id(user_id):
        return db.session.get(User, user_id)

    @staticmethod
    def get_by_email(email):
        return db.session.scalars(select(User).filter_by(email=email)).first()

    @staticmethod
    def list_all():
        return db.session.scalars(select(User).order_by(User.id)).all()

    @staticmethod
    def email_taken(email, ignore_user_id=None):
        stmt = select(User.id).filter_by(email=email)
        if ignore_user_id is not None:
            stmt = stmt.where(User.id != ignore_user_id)
        return db.session.scalars(stmt).first() is not None

    @staticmethod
    def create(name, email, raw_password, role):
        user = User(name=name, email=email, role=role)
        user.set_password(raw_password)
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def save():
        db.session.commit()

    @staticmethod
    def delete_with_tasks(user):
        """Remove o usuário e suas tasks numa única transação."""
        from models.task import Task

        Task.delete_by_user(user.id, commit=False)
        db.session.delete(user)
        db.session.commit()
