from adapters.repositories.user_repository import UserRepository
from core.models import User
from typing import Optional

class UserService:
    @staticmethod
    def create_user(username, password, roles, region):
        """Создать пользователя"""
        return UserRepository.create(username, password, roles, region)

    @staticmethod
    def list_users():
        """Получить список всех пользователей"""
        return UserRepository.get_all()

    @staticmethod
    def delete_user(user_id):
        """Удалить пользователя"""
        return UserRepository.delete(user_id)

    @staticmethod
    def authenticate(username: str, password: str) -> Optional[User]:
        """Аутентифицировать пользователя"""
        user = UserRepository.get_user_by_username(username)
        if user and user.check_password(password):
            return user
        return None
