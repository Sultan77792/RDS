from flask import Blueprint, request, jsonify, render_template
from flask_login import login_required, current_user
from adapters.services.user_service import UserService
import logging
from regions import REGIONS_AND_LOCATIONS  # Импортируем словарь регионов

# Настройка логирования
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

user_bp = Blueprint('user_bp', __name__)

# Список доступных ролей с человеко-читаемыми названиями
AVAILABLE_ROLES = {
    'admin': 'Администратор',
    'engineer': 'Инженер',
    'analyst': 'Аналитик',
    'user': 'Пользователь'
}

class UserController:
    def __init__(self):
        """Инициализация контроллера с сервисом пользователей."""
        self.user_service = UserService()
        logger.info("UserController initialized")

    @staticmethod
    @user_bp.route('/', methods=['GET'])
    @login_required
    def list_users():
        """Получить список пользователей."""
        try:
            logger.debug("Fetching list of users")
            users = UserService.list_users()
            users_data = [{
                'id': user.id,
                'username': user.username,
                'roles': user.roles,
                'region': user.region
            } for user in users]
            logger.info(f"Retrieved {len(users)} users")
            return jsonify(users_data)
        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(e)}), 500

    @staticmethod
    @user_bp.route('/', methods=['POST'])
    @login_required
    def create_user():
        """Создать нового пользователя."""
        try:
            if 'admin' not in current_user.roles.split(','):
                logger.warning(f"Access denied for user {current_user.username} to create user")
                return jsonify({'error': 'Доступ запрещён'}), 403

            logger.debug("Processing create_user request")
            data = request.json
            
            # Валидация данных
            if not data or not all(key in data for key in ['username', 'password', 'roles', 'region']):
                logger.warning("Missing required fields in request data")
                return jsonify({'error': 'Отсутствуют обязательные поля'}), 400

            # Проверка допустимости роли
            if data['roles'] not in AVAILABLE_ROLES:
                logger.warning(f"Invalid role provided: {data['roles']}")
                return jsonify({'error': 'Указана недопустимая роль'}), 400

            # Проверка допустимости региона
            if data['region'] not in REGIONS_AND_LOCATIONS:
                logger.warning(f"Invalid region provided: {data['region']}")
                return jsonify({'error': 'Указан недопустимый регион'}), 400

            user = UserService.create_user(
                data['username'],
                data['password'],
                data['roles'],
                data['region']
            )
            logger.info(f"User created: {user.username} with ID {user.id}")
            return jsonify({
                'id': user.id,
                'username': user.username,
                'roles': user.roles,
                'region': user.region
            }), 201
        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(e)}), 500

    @staticmethod
    @user_bp.route('/<int:user_id>', methods=['DELETE'])
    @login_required
    def delete_user(user_id):
        """Удалить пользователя."""
        try:
            if 'admin' not in current_user.roles.split(','):
                logger.warning(f"Access denied for user {current_user.username} to delete user {user_id}")
                return jsonify({'error': 'Доступ запрещён'}), 403

            logger.debug(f"Processing delete_user request for user_id: {user_id}")
            if UserService.delete_user(user_id):
                logger.info(f"User {user_id} deleted")
                return jsonify({'message': 'Пользователь удалён'}), 200
            else:
                logger.warning(f"User {user_id} not found")
                return jsonify({'error': 'Пользователь не найден'}), 404
        except Exception as e:
            logger.error(f"Error deleting user {user_id}: {str(e)}")
            return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(e)}), 500

    @staticmethod
    @user_bp.route('/manage', methods=['GET'])
    @login_required
    def manage_users():
        """Страница управления пользователями."""
        try:
            if 'admin' not in current_user.roles.split(','):
                logger.warning(f"Access denied for user {current_user.username} to manage users")
                return jsonify({'error': 'Доступ запрещён'}), 403

            logger.debug("Rendering manage_users page")
            users = UserService.list_users()
            
            # Получаем список регионов из импортированного словаря
            regions = list(REGIONS_AND_LOCATIONS.keys())
            
            # Подготавливаем список ролей для шаблона
            roles = [{'value': k, 'label': v} for k, v in AVAILABLE_ROLES.items()]
            
            logger.info(f"Rendering manage_users with {len(users)} users")
            return render_template(
                'manage_users.html',
                users=users,
                regions=regions,
                roles=roles
            )
        except Exception as e:
            logger.error(f"Error rendering manage_users: {str(e)}")
            return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(e)}), 500