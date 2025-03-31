import unittest
from unittest.mock import Mock, patch
from flask import Flask
from adapters.controllers.fire_controller import FireController, fire_bp
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from adapters.repositories.region_repository import SQLAlchemyRegionRepository
from core.entities import FireEntity
from datetime import datetime
from forms import FireForm

class TestFireController(unittest.TestCase):
    def setUp(self):
        # Создаем Flask-приложение для тестирования
        self.app = Flask(__name__)
        self.app.config['TESTING'] = True
        self.app.config['SECRET_KEY'] = 'test-secret-key'
        self.app.config['WTF_CSRF_ENABLED'] = False  # Отключаем CSRF для тестов
        self.client = self.app.test_client()

        # Создаем моки репозиториев
        self.fire_repository = Mock(spec=SQLAlchemyFireRepository)
        self.region_repository = Mock(spec=SQLAlchemyRegionRepository)
        self.fire_controller = FireController(self.fire_repository, self.region_repository)

        # Регистрируем Blueprint
        self.app.register_blueprint(fire_bp)

        # Мокаем Flask-Login
        with self.app.app_context():
            self.app.login_manager = Mock()
            self.app.login_manager.login_view = 'fire.login'

    def test_login_success(self):
        """Тест успешного логина."""
        with self.app.test_request_context():
            with patch('core.models.User') as mock_user:
                mock_user_instance = Mock()
                mock_user_instance.check_password.return_value = True
                mock_user_instance.roles = 'admin'
                mock_user.query.filter_by.return_value.first.return_value = mock_user_instance
                with patch('flask_login.login_user') as mock_login:
                    response = self.client.post('/login', data={'username': 'admin', 'password': 'pass'})
                    self.assertEqual(response.status_code, 302)
                    self.assertIn('/admin-dashboard', response.location)
                    mock_login.assert_called_once()

    def test_login_failure(self):
        """Тест неудачного логина."""
        with self.app.test_request_context():
            with patch('core.models.User') as mock_user:
                mock_user.query.filter_by.return_value.first.return_value = None
                response = self.client.post('/login', data={'username': 'admin', 'password': 'wrong'})
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Неверное имя пользователя или пароль', response.data)

    def test_add_fire_success(self):
        """Тест успешного добавления пожара."""
        with self.app.test_request_context():
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=True, roles='operator', username='operator1', region='Акмолинская область')
                self.region_repository.get_all_regions.return_value = ['Акмолинская область']
                self.region_repository.get_locations_by_region.return_value = ['Акколь']
                fire_data = {
                    'date': '2023-01-01',
                    'region': 'Акмолинская область',
                    'location': 'Акколь',
                    'damage_area': '10.5',
                    'submit': 'Сохранить'
                }
                saved_fire = FireEntity(id=1, date=datetime(2023, 1, 1), region='Акмолинская область', location='Акколь', damage_area=10.5)
                self.fire_repository.add.return_value = saved_fire
                response = self.client.post('/form', data=fire_data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Данные успешно добавлены!', response.data)

    def test_edit_fire_success(self):
        """Тест успешного редактирования пожара."""
        with self.app.test_request_context():
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=True, roles='admin', username='admin1')
                fire = FireEntity(id=1, date=datetime(2023, 1, 1), region='Акмолинская область', location='Акколь', damage_area=10.5)
                self.fire_repository.get_by_id.return_value = fire
                self.region_repository.get_all_regions.return_value = ['Акмолинская область']
                self.region_repository.get_locations_by_region.return_value = ['Акколь']
                updated_fire = FireEntity(id=1, date=datetime(2023, 1, 1), region='Акмолинская область', location='Акколь', damage_area=15.0)
                self.fire_repository.update.return_value = updated_fire
                fire_data = {
                    'date': '2023-01-01',
                    'region': 'Акмолинская область',
                    'location': 'Акколь',
                    'damage_area': '15.0',
                    'submit': 'Сохранить'
                }
                response = self.client.post('/edit/1', data=fire_data, follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Данные успешно обновлены!', response.data)

    def test_delete_fire_success(self):
        """Тест успешного удаления пожара."""
        with self.app.test_request_context():
            with patch('flask_login.utils._get_user') as mock_user:
                mock_user.return_value = Mock(is_authenticated=True, roles='admin', username='admin1')
                fire = FireEntity(id=1, date=datetime(2023, 1, 1), region='Акмолинская область', location='Акколь')
                self.fire_repository.get_by_id.return_value = fire
                response = self.client.post('/delete/1', follow_redirects=True)
                self.assertEqual(response.status_code, 200)
                self.assertIn(b'Запись о пожаре с ID 1 успешно удалена', response.data)

if __name__ == '__main__':
    unittest.main()