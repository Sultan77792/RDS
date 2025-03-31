import unittest
from datetime import datetime
from unittest.mock import Mock
from core.entities import FireEntity
from use_cases.fire_analysis import FireAnalysis

class TestFireAnalysis(unittest.TestCase):
    def setUp(self):
        # Создаем мок-репозиторий
        self.fire_repository = Mock()
        self.fire_analysis = FireAnalysis(self.fire_repository)

    def test_get_fire_summary_empty(self):
        """Тест сводки при отсутствии данных."""
        self.fire_repository.get_all.return_value = []
        summary = self.fire_analysis.get_fire_summary()
        expected = {
            "total_fires": 0,
            "total_area": 0,
            "total_damage": 0,
            "total_people": 0,
            "total_technics": 0,
            "total_aircraft": 0
        }
        self.assertEqual(summary, expected)

    def test_get_fire_summary_with_data(self):
        """Тест сводки с данными о пожарах."""
        fires = [
            FireEntity(
                id=1,
                date=datetime(2023, 1, 1),
                region="Акмолинская область",
                location="Акколь",
                damage_area=10.5,
                damage_tenge=1000,
                LO_people_count=5,
                APS_tecnic_count=2,
                KPS_aircraft_count=1
            ),
            FireEntity(
                id=2,
                date=datetime(2023, 2, 1),
                region="Алматинская область",
                location="Каскеленское",
                damage_area=20.0,
                damage_tenge=2000,
                MIO_people_count=3,
                other_org_tecnic_count=1
            )
        ]
        self.fire_repository.get_all.return_value = fires
        summary = self.fire_analysis.get_fire_summary()
        expected = {
            "total_fires": 2,
            "total_area": 30.5,
            "total_damage": 3000,
            "total_people": 8,  # 5 (LO) + 3 (MIO)
            "total_technics": 3,  # 2 (APS) + 1 (other_org)
            "total_aircraft": 1  # 1 (KPS)
        }
        self.assertEqual(summary, expected)

    def test_get_fires_by_region(self):
        """Тест получения пожаров по региону."""
        fires = [
            FireEntity(id=1, date=datetime(2023, 1, 1), region="Акмолинская область", location="Акколь"),
            FireEntity(id=2, date=datetime(2023, 2, 1), region="Алматинская область", location="Каскеленское")
        ]
        self.fire_repository.get_by_region.return_value = [fires[0]]
        result = self.fire_analysis.get_fires_by_region("Акмолинская область")
        self.assertEqual(len(result), 1)
        self.assertEqual(result[0].region, "Акмолинская область")

    def test_add_fire(self):
        """Тест добавления пожара."""
        fire = FireEntity(
            id=0,
            date=datetime(2023, 1, 1),
            region="Акмолинская область",
            location="Акколь",
            damage_area=10.0
        )
        saved_fire = FireEntity(
            id=1,
            date=datetime(2023, 1, 1),
            region="Акмолинская область",
            location="Акколь",
            damage_area=10.0
        )
        self.fire_repository.add.return_value = saved_fire
        result = self.fire_analysis.add_fire(fire)
        self.fire_repository.add.assert_called_once_with(fire)
        self.assertEqual(result.id, 1)

if __name__ == '__main__':
    unittest.main()