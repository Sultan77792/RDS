import unittest
from unittest.mock import Mock, patch
from flask import Flask
from adapters.controllers.dashboard_controller import DashboardController, dashboard_bp
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from core.entities import FireEntity
from datetime import datetime

class TestDashboardController(unittest.TestCase):
    def setUp(self):
        # Создаем Flask-приложение для тестирования
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.client = self.app.test_client()

        # Создаем мок-репозиторий
        self.fire_repository = Mock(spec=SQLAlchemyFireRepository)
        self.dashboard_controller = DashboardController(self.fire_repository)

        # Регистрируем Blueprint
        self.app.register_blueprint(dashboard_bp)

        # Мокаем Flask-Login
        with self.app.app_context():
            self.app.login_manager = Mock()
            self.app.login_manager.login_view = 'login'

    def test_dashboard_route(self):
        """Тест отображения дашборда."""
        with self.app.test_request_context():
            # Мокаем current_user для прохождения @login_required
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=True, roles='analyst')
                self.fire_repository.get_all.return_value = [
                    FireEntity(id=1, date=datetime(2023, 1, 1), region="Акмолинская область", location="Акколь", damage_area=10.0)
                ]
                response = self.client.get('/dashboard')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'dashboard.html', response.data)  # Проверяем, что рендерится шаблон

    def test_summary_route_no_filters(self):
        """Тест сводки без фильтров."""
        with self.app.test_request_context():
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=True, roles='analyst')
                self.fire_repository.get_all_regions.return_value = ["Акмолинская область"]
                self.fire_repository.get_by_region.return_value = [
                    FireEntity(id=1, date=datetime(2023, 1, 1), region="Акмолинская область", location="Акколь", damage_area=10.0)
                ]
                response = self.client.get('/summary')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'summary.html', response.data)

    def test_summary_route_with_filters(self):
        """Тест сводки с фильтрами по дате."""
        with self.app.test_request_context():
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=True, roles='analyst')
                self.fire_repository.get_all_regions.return_value = ["Акмолинская область"]
                self.fire_repository.get_by_region.return_value = [
                    FireEntity(id=1, date=datetime(2023, 1, 1), region="Акмолинская область", location="Акколь", damage_area=10.0)
                ]
                response = self.client.get('/summary?start_date=2023-01-01&end_date=2023-12-31')
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'summary.html', response.data)

    def test_unauthorized_access(self):
        """Тест доступа без авторизации."""
        with self.app.test_request_context():
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=False)
                response = self.client.get('/dashboard')
                self.assertEqual(response.status_code, 302)  # Перенаправление на login

if __name__ == '__main__':
    unittest.main()