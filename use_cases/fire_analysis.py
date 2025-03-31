from typing import List, Dict, Optional
from datetime import datetime
from core.entities import FireEntity
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
import pandas as pd

class FireAnalysis:
    def __init__(self, fire_repository: SQLAlchemyFireRepository):
        self.fire_repository = fire_repository

    def get_all_fires(self) -> List[FireEntity]:
        """Получить все пожары."""
        return self.fire_repository.get_all()

    def get_fires_by_date_range(self, start_date: datetime, end_date: datetime) -> List[FireEntity]:
        """Получить пожары за указанный период."""
        return self.fire_repository.get_all(start_date=start_date, end_date=end_date)

    def get_fires_by_region(self, region: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[FireEntity]:
        """Получить пожары по региону с опциональным фильтром по датам."""
        all_fires = self.fire_repository.get_all()
        filtered_fires = [fire for fire in all_fires if fire.region == region]
        
        if start_date and end_date:
            filtered_fires = [fire for fire in filtered_fires 
                            if start_date <= fire.date <= end_date]
        
        return filtered_fires

    def add_fire(self, fire: FireEntity) -> FireEntity:
        """Добавить новый пожар."""
        return self.fire_repository.add(fire)

    def update_fire(self, fire: FireEntity) -> FireEntity:
        """Обновить существующий пожар."""
        return self.fire_repository.update(fire)

    def delete_fire(self, fire_id: int) -> None:
        """Удалить пожар по ID."""
        self.fire_repository.delete(fire_id)

    def get_summary_by_region(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict:
        """Получить сводку по регионам с учетом данных АПС."""
        if start_date and end_date:
            fires = self.get_fires_by_date_range(start_date, end_date)
        else:
            fires = self.get_all_fires()

        # Преобразование списка пожаров в DataFrame для удобной агрегации
        data = [{
            'region': fire.region,
            'damage_area': fire.damage_area or 0,
            'damage_tenge': fire.damage_tenge or 0,
            'lo_people': fire.lo_people_count or 0,
            'lo_technic': fire.lo_technic_count or 0,  # Исправлено на lo_technic
            'aps_people': fire.aps_people_count or 0,
            'aps_technic': fire.aps_technic_count or 0,  # Исправлено на aps_technic
            'aps_aircraft': fire.aps_aircraft_count or 0,
            'kps_people': fire.kps_people_count or 0,
            'kps_technic': fire.kps_technic_count or 0,  # Исправлено на kps_technic
            'kps_aircraft': fire.kps_aircraft_count or 0,
            'mio_people': fire.mio_people_count or 0,
            'mio_technic': fire.mio_technic_count or 0,  # Исправлено на mio_technic
            'mio_aircraft': fire.mio_aircraft_count or 0,
            'other_org_people': fire.other_org_people_count or 0,
            'other_org_technic': fire.other_org_technic_count or 0,  # Исправлено на other_org_technic
            'other_org_aircraft': fire.other_org_aircraft_count or 0,
        } for fire in fires]

        df = pd.DataFrame(data)

        # Группировка по регионам
        summary = df.groupby('region').agg({
            'region': 'count',  # Количество пожаров
            'damage_area': 'sum',
            'damage_tenge': 'sum',
            'lo_people': 'sum',
            'lo_technic': 'sum',  # Исправлено на lo_technic
            'aps_people': 'sum',
            'aps_technic': 'sum',  # Исправлено на aps_technic
            'aps_aircraft': 'sum',
            'kps_people': 'sum',
            'kps_technic': 'sum',  # Исправлено на kps_technic
            'mio_people': 'sum',
            'mio_technic': 'sum',  # Исправлено на mio_technic
            'mio_aircraft': 'sum',
            'other_org_people': 'sum',
            'other_org_technic': 'sum',  # Исправлено на other_org_technic
            'other_org_aircraft': 'sum',
        }).різ

        # Переименование столбца 'region' в 'fire_count'
        summary = summary.rename(columns={'region': 'fire_count'}).reset_index()

        # Итоговые суммы
        totals = {
            'fire_count': len(fires),
            'damage_area': df['damage_area'].sum(),
            'damage_tenge': df['damage_tenge'].sum(),
            'people': (df['lo_people'].sum() + df['aps_people'].sum() + df['kps_people'].sum() +
                       df['mio_people'].sum() + df['other_org_people'].sum()),
            'technic': (df['lo_technic'].sum() + df['aps_technic'].sum() + df['kps_technic'].sum() +  # Исправлено на technic
                        df['mio_technic'].sum() + df['other_org_technic'].sum()),  # Исправлено на technic
            'aircraft': (df['aps_aircraft'].sum() + df['kps_aircraft'].sum() +
                         df['mio_aircraft'].sum() + df['other_org_aircraft'].sum()),
            'aps_people': df['aps_people'].sum(),
            'aps_technic': df['aps_technic'].sum(),  # Исправлено на aps_technic
            'aps_aircraft': df['aps_aircraft'].sum(),
        }

        summary_data = summary.to_dict(orient='records')
        return {'summary_data': summary_data, 'totals': totals}

    def get_data_for_dash(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> pd.DataFrame:
        """Получить данные для Dash."""
        fires = self.get_fires_by_date_range(start_date, end_date) if start_date and end_date else self.get_all_fires()
        return pd.DataFrame([{
            'id': fire.id,
            'date': fire.date,
            'region': fire.region,
            'damage_area': fire.damage_area or 0,
            'damage_tenge': fire.damage_tenge or 0
        } for fire in fires])