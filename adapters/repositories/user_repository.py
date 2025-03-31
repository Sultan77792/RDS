from infrastructure.database import db
from core.models import User

class UserRepository:
    @staticmethod
    def get_all():
        """Получить всех пользователей"""
        return User.query.all()

    @staticmethod
    def get_by_id(user_id):
        """Получить пользователя по ID"""
        return User.query.get(user_id)

    @staticmethod
    def get_user_by_username(username):
        """Получить пользователя по имени"""
        return User.query.filter_by(username=username).first()

    @staticmethod
    def create(username, password, roles, region):
        """Создать нового пользователя"""
        user = User(username=username, roles=roles, region=region)
        user.set_password(password)  # Используем существующий метод set_password
        db.session.add(user)
        db.session.commit()
        return user

    @staticmethod
    def delete(user_id):
        """Удалить пользователя"""
        user = User.query.get(user_id)
        if user:
            db.session.delete(user)
            db.session.commit()
            return True
        return False
