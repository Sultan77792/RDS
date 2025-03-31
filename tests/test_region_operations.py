import unittest
from unittest.mock import Mock
from use_cases.region_operations import RegionOperations

class TestRegionOperations(unittest.TestCase):
    def setUp(self):
        self.region_repository = Mock()
        self.region_ops = RegionOperations(self.region_repository)

    def test_get_all_regions(self):
        """Тест получения всех регионов."""
        self.region_repository.get_all_regions.return_value = ['Регион1', 'Регион2']
        result = self.region_ops.get_all_regions()
        self.assertEqual(result, ['Регион1', 'Регион2'])

    def test_get_locations_by_region(self):
        """Тест получения территорий по региону."""
        self.region_repository.get_locations.return_value = ['Территория1', 'Территория2']
        result = self.region_ops.get_locations_by_region('Регион1')
        self.assertEqual(result, ['Территория1', 'Территория2'])

    def test_validate_region_valid(self):
        """Тест валидации существующего региона."""
        self.region_repository.get_all_regions.return_value = ['Регион1', 'Регион2']
        result = self.region_ops.validate_region('Регион1')
        self.assertTrue(result)

    def test_validate_region_invalid(self):
        """Тест валидации несуществующего региона."""
        self.region_repository.get_all_regions.return_value = ['Регион1', 'Регион2']
        result = self.region_ops.validate_region('Регион3')
        self.assertFalse(result)

if __name__ == '__main__':
    unittest.main()