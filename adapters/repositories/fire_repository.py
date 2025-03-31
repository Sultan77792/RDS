from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from core.entities import FireEntity
from infrastructure.database import db
from core.models import Fire

class FireRepository(ABC):
    @abstractmethod
    def get_all(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[FireEntity]:
        pass

    @abstractmethod
    def get_by_id(self, fire_id: int) -> Optional[FireEntity]:
        pass

    @abstractmethod
    def get_by_region(self, region: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[FireEntity]:
        pass

    @abstractmethod
    def add(self, fire: FireEntity) -> FireEntity:
        pass

    @abstractmethod
    def update(self, fire: FireEntity) -> FireEntity:
        pass

    @abstractmethod
    def delete(self, fire_id: int) -> None:
        pass

    @abstractmethod
    def get_all_regions(self) -> List[str]:
        pass

class SQLAlchemyFireRepository(FireRepository):
    def get_all(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[FireEntity]:
        query = db.session.query(Fire)
        if start_date:
            query = query.filter(Fire.date >= start_date)
        if end_date:
            query = query.filter(Fire.date <= end_date)
        fires = query.order_by(Fire.date.desc()).all()
        return [self._to_entity(fire) for fire in fires]

    def get_by_id(self, fire_id: int) -> Optional[FireEntity]:
        fire = db.session.query(Fire).get(fire_id)
        return self._to_entity(fire) if fire else None

    def get_by_region(self, region: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> List[FireEntity]:
        query = db.session.query(Fire).filter_by(region=region)
        if start_date:
            query = query.filter(Fire.date >= start_date)
        if end_date:
            query = query.filter(Fire.date <= end_date)
        fires = query.order_by(Fire.date.desc()).all()
        return [self._to_entity(fire) for fire in fires]

    def add(self, fire: FireEntity) -> FireEntity:
        db_fire = Fire(
            date=fire.date,
            region=fire.region,
            location=fire.location,
            branch=fire.branch,
            forestry=fire.forestry,
            quarter=fire.quarter,
            allotment=fire.allotment,
            damage_area=fire.damage_area,
            damage_les=fire.damage_les,
            damage_les_lesopokryt=fire.damage_les_lesopokryt,
            damage_les_verh=fire.damage_les_verh,
            damage_not_les=fire.damage_not_les,
            lo_flag=fire.lo_flag,
            lo_people_count=fire.lo_people_count,
            lo_technic_count=fire.lo_technic_count,
            aps_flag=fire.aps_flag,
            aps_people_count=fire.aps_people_count,
            aps_technic_count=fire.aps_technic_count,
            aps_aircraft_count=fire.aps_aircraft_count,
            kps_flag=fire.kps_flag,
            kps_people_count=fire.kps_people_count,
            kps_technic_count=fire.kps_technic_count,
            kps_aircraft_count=fire.kps_aircraft_count,
            mio_flag=fire.mio_flag,
            mio_people_count=fire.mio_people_count,
            mio_technic_count=fire.mio_technic_count,
            mio_aircraft_count=fire.mio_aircraft_count,
            other_org_flag=fire.other_org_flag,
            other_org_people_count=fire.other_org_people_count,
            other_org_technic_count=fire.other_org_technic_count,
            other_org_aircraft_count=fire.other_org_aircraft_count,
            description=fire.description,
            damage_tenge=fire.damage_tenge,
            firefighting_costs=fire.firefighting_costs,
            kpo=fire.kpo,
            file_path=fire.file_path,
            edited_by_engineer=False
        )
        db.session.add(db_fire)
        db.session.commit()
        return self._to_entity(db_fire)

    def update(self, fire: FireEntity) -> FireEntity:
        db_fire = db.session.query(Fire).get(fire.id)
        if not db_fire:
            raise ValueError(f"Пожар с ID {fire.id} не найден")
        
        for key, value in vars(fire).items():
            if key != 'id':
                setattr(db_fire, key, value)
        
        db.session.commit()
        return self._to_entity(db_fire)

    def delete(self, fire_id: int) -> None:
        db_fire = db.session.query(Fire).get(fire_id)
        if db_fire:
            db.session.delete(db_fire)
            db.session.commit()

    def get_all_regions(self) -> List[str]:
        regions = db.session.query(Fire.region).distinct().all()
        return [region[0] for region in regions]

    def _to_entity(self, fire: Fire) -> FireEntity:
        """Преобразование модели Fire в сущность FireEntity."""
        if not fire:
            return None
        return FireEntity(
            id=fire.id,
            date=fire.date,
            region=fire.region,
            location=fire.location,
            branch=fire.branch,
            forestry=fire.forestry,
            quarter=fire.quarter,
            allotment=fire.allotment,
            damage_area=float(fire.damage_area) if fire.damage_area else None,
            damage_les=float(fire.damage_les) if fire.damage_les else None,
            damage_les_lesopokryt=float(fire.damage_les_lesopokryt) if fire.damage_les_lesopokryt else None,
            damage_les_verh=float(fire.damage_les_verh) if fire.damage_les_verh else None,
            damage_not_les=float(fire.damage_not_les) if fire.damage_not_les else None,
            lo_flag=fire.lo_flag,
            lo_people_count=fire.lo_people_count,
            lo_technic_count=fire.lo_technic_count,
            aps_flag=fire.aps_flag,
            aps_people_count=fire.aps_people_count,
            aps_technic_count=fire.aps_technic_count,
            aps_aircraft_count=fire.aps_aircraft_count,
            kps_flag=fire.kps_flag,
            kps_people_count=fire.kps_people_count,
            kps_technic_count=fire.kps_technic_count,
            kps_aircraft_count=fire.kps_aircraft_count,
            mio_flag=fire.mio_flag,
            mio_people_count=fire.mio_people_count,
            mio_technic_count=fire.mio_technic_count,
            mio_aircraft_count=fire.mio_aircraft_count,
            other_org_flag=fire.other_org_flag,
            other_org_people_count=fire.other_org_people_count,
            other_org_technic_count=fire.other_org_technic_count,
            other_org_aircraft_count=fire.other_org_aircraft_count,
            description=fire.description,
            damage_tenge=fire.damage_tenge,
            firefighting_costs=fire.firefighting_costs,
            kpo=fire.kpo,
            file_path=fire.file_path,
            edited_by_engineer=fire.edited_by_engineer
        )