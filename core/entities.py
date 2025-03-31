from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional
import json

@dataclass
class FireEntity:
    """Сущность, представляющая данные о пожаре."""
    id: int
    date: datetime
    region: str
    location: str
    branch: Optional[str] = None
    forestry: Optional[str] = None
    quarter: Optional[str] = None
    allotment: Optional[str] = None
    damage_area: float = 0.0
    damage_les: Optional[float] = None
    damage_les_lesopokryt: Optional[float] = None
    damage_les_verh: Optional[float] = None
    damage_not_les: Optional[float] = None
    lo_flag: bool = False
    lo_people_count: Optional[int] = None
    lo_technic_count: Optional[int] = None
    aps_flag: bool = False
    aps_people_count: Optional[int] = None
    aps_technic_count: Optional[int] = None
    aps_aircraft_count: Optional[int] = None
    kps_flag: bool = False
    kps_people_count: Optional[int] = None
    kps_technic_count: Optional[int] = None
    kps_aircraft_count: Optional[int] = None
    mio_flag: bool = False
    mio_people_count: Optional[int] = None
    mio_technic_count: Optional[int] = None
    mio_aircraft_count: Optional[int] = None
    other_org_flag: bool = False
    other_org_people_count: Optional[int] = None
    other_org_technic_count: Optional[int] = None
    other_org_aircraft_count: Optional[int] = None
    description: Optional[str] = None
    damage_tenge: Optional[int] = None
    firefighting_costs: Optional[int] = None
    kpo: Optional[int] = None
    file_path: Optional[str] = None
    edited_by_engineer: bool = False

    def __post_init__(self):
        """Валидация и обработка данных после инициализации."""
        # Проверка, что регион и локация не пустые
        if not self.region or not self.location:
            raise ValueError("Поля 'region' и 'location' должны быть заполнены")

        # Список количественных полей для обработки
        quantitative_fields = [
            'damage_area', 'damage_les', 'damage_les_lesopokryt', 'damage_les_verh', 'damage_not_les',
            'lo_people_count', 'lo_technic_count', 'aps_people_count', 'aps_technic_count', 'aps_aircraft_count',
            'kps_people_count', 'kps_technic_count', 'kps_aircraft_count', 'mio_people_count', 'mio_technic_count',
            'mio_aircraft_count', 'other_org_people_count', 'other_org_technic_count', 'other_org_aircraft_count',
            'damage_tenge', 'firefighting_costs', 'kpo'
        ]

        # Преобразование отрицательных значений в положительные
        for field in quantitative_fields:
            value = getattr(self, field)
            if value is not None and isinstance(value, (int, float)):
                setattr(self, field, abs(value))  # Используем abs() для получения модуля

    def to_dict(self) -> dict:
        """Преобразование сущности в словарь."""
        data = asdict(self)
        data['date'] = self.date.isoformat()  # Преобразование datetime в строку
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'FireEntity':
        """Создание сущности из словаря."""
        data = data.copy()
        data['date'] = datetime.fromisoformat(data['date'])  # Преобразование строки в datetime
        return cls(**data)

# Остальные классы (UserEntity, AuditLogEntity) остаются без изменений
@dataclass
class UserEntity:
    """Сущность, представляющая пользователя."""
    id: int
    username: str
    password: str  # Хэшированный пароль
    roles: str
    region: str

    def __post_init__(self):
        """Валидация данных после инициализации."""
        if not self.username or not self.password or not self.region:
            raise ValueError("Поля 'username', 'password' и 'region' должны быть заполнены")
        if not self.roles:
            self.roles = ""  # Пустая строка вместо None для согласованности

    def to_dict(self) -> dict:
        """Преобразование сущности в словарь."""
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict) -> 'UserEntity':
        """Создание сущности из словаря."""
        return cls(**data)

@dataclass
class AuditLogEntity:
    """Сущность, представляющая запись в журнале аудита."""
    id: int
    timestamp: datetime
    username: str
    action: str
    table_name: str
    record_id: int
    changes: Optional[str] = None

    def __post_init__(self):
        """Валидация данных после инициализации."""
        if not self.username or not self.action or not self.table_name:
            raise ValueError("Поля 'username', 'action' и 'table_name' должны быть заполнены")
        if self.record_id < 0:
            raise ValueError(f"Поле 'record_id' не может быть отрицательным: {self.record_id}")

    def to_dict(self) -> dict:
        """Преобразование сущности в словарь."""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()  # Преобразование datetime в строку
        return data

    @classmethod
    def from_dict(cls, data: dict) -> 'AuditLogEntity':
        """Создание сущности из словаря."""
        data = data.copy()
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])  # Преобразование строки в datetime
        return cls(**data)