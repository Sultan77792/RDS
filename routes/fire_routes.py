from flask import Blueprint
from controllers.fire_controller import FireController
from services.fire_service import UserService
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from adapters.repositories.region_repository import SQLAlchemyRegionRepository
from infrastructure.database import db
from flask_login import LoginManager

fire_bp = Blueprint('fire', __name__)

# Инициализация зависимостей
fire_repository = SQLAlchemyFireRepository()
region_repository = SQLAlchemyRegionRepository()
fire_service = UserService(fire_repository, region_repository, db)
fire_controller = FireController(fire_service)

# Регистрация маршрутов
fire_bp.add_url_rule('/', 'home', fire_controller.home, methods=['GET'])
fire_bp.add_url_rule('/login', 'login', fire_controller.login, methods=['GET', 'POST'])
fire_bp.add_url_rule('/logout', 'logout', fire_controller.logout, methods=['GET'])
fire_bp.add_url_rule('/form', 'add_fire', fire_controller.add_fire, methods=['GET', 'POST'])
fire_bp.add_url_rule('/edit/<int:fire_id>', 'edit_fire', fire_controller.edit_fire, methods=['GET', 'POST'])
fire_bp.add_url_rule('/delete/<int:fire_id>', 'delete_fire', fire_controller.delete_fire, methods=['POST'])
fire_bp.add_url_rule('/admin-dashboard', 'admin_dashboard', fire_controller.admin_dashboard, methods=['GET'])
fire_bp.add_url_rule('/export-audit', 'export_audit', fire_controller.export_audit, methods=['GET'])
fire_bp.add_url_rule('/get-locations', 'get_locations', fire_controller.get_locations, methods=['GET'])
fire_bp.add_url_rule('/download/<filename>', 'download_file', fire_controller.download_file, methods=['GET'])

# Добавленный маршрут для API
fire_bp.add_url_rule('/api/fires', 'get_fires', fire_controller.get_fires, methods=['GET'])
