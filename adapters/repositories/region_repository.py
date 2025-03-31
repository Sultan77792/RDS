from abc import ABC, abstractmethod
from typing import List, Dict
from regions import REGIONS_AND_LOCATIONS  # Предполагается, что данные регионов остаются в отдельном файле

class RegionRepository(ABC):
    @abstractmethod
    def get_all_regions(self) -> List[str]:
        pass

    @abstractmethod
    def get_locations(self, region: str) -> List[str]:
        pass

    @abstractmethod
    def get_region_location_mapping(self) -> Dict[str, List[str]]:
        pass

class SQLAlchemyRegionRepository(RegionRepository):
    """Реализация репозитория регионов на основе статических данных (не использует SQLAlchemy напрямую)."""
    def __init__(self):
        self.regions_and_locations = REGIONS_AND_LOCATIONS

    def get_all_regions(self) -> List[str]:
        """Получить список всех регионов."""
        return list(self.regions_and_locations.keys())

    def get_locations(self, region: str) -> List[str]:
        """Получить список территорий для региона."""
        return self.regions_and_locations.get(region, [])

    def get_region_location_mapping(self) -> Dict[str, List[str]]:
        """Получить полное соответствие регионов и территорий."""
        return self.regions_and_locations.copy()