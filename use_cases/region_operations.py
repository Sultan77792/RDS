from typing import List, Dict

class RegionOperations:
    def __init__(self, region_repository):
        self.region_repository = region_repository

    def get_all_regions(self) -> List[str]:
        """Получить список всех регионов."""
        return self.region_repository.get_all_regions()

    def get_locations_by_region(self, region: str) -> List[str]:
        """Получить список территорий для указанного региона."""
        return self.region_repository.get_locations(region)

    def get_region_location_mapping(self) -> Dict[str, List[str]]:
        """Получить полное соответствие регионов и их территорий."""
        return self.region_repository.get_region_location_mapping()

    def validate_region(self, region: str) -> bool:
        """Проверить, существует ли регион."""
        regions = self.region_repository.get_all_regions()
        return region in regions

    def validate_location(self, region: str, location: str) -> bool:
        """Проверить, существует ли территория в указанном регионе."""
        locations = self.region_repository.get_locations(region)
        return location in locations