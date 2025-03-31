import unittest
from unittest.mock import Mock, patch
from core.entities import FireEntity
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from adapters.repositories.region_repository import SQLAlchemyRegionRepository
from datetime import datetime

class TestRepositories(unittest.TestCase):
    def setUp(self):
        self.fire_repo = SQLAlchemyFireRepository()
        self.region_repo = SQLAlchemyRegionRepository()

    @patch('infrastructure.database.db.session')
    def test_fire_repository_get_all(self, mock_session):
        """Тест получения всех пожаров."""
        mock_fire = Mock(id=1, date=datetime(2023, 1, 1), region='Регион1', location='Локация1')
        mock_session.query.return_value.order_by.return_value.all.return_value = [mock_fire]
        result = self.fire_repo.get_all()
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].id, 1)

    def test_region_repository_get_all_regions(self):
        """Тест получения всех регионов."""
        result = self.region_repo.get_all_regions()
        self.assertTrue(len(result) > 0)
        self.assertIn('Акмолинская область', result)

    def test_region_repository_get_locations(self):
        """Тест получения территорий по региону."""
        result = self.region_repo.get_locations('Акмолинская область')
        self.assertTrue(len(result) > 0)
        self.assertIn('Акколь', result)

if __name__ == '__main__':
    unittest.main()