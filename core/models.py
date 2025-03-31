from infrastructure.database import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    roles = db.Column(db.String(50), nullable=False)
    region = db.Column(db.String(255), nullable=False)

    def set_password(self, password):
        """Зашифровать пароль"""
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """Проверить введенный пароль с хранимым хешем"""
        return check_password_hash(self.password, password)

class Fire(db.Model):
    __tablename__ = 'fires'
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.Date, nullable=False)
    region = db.Column(db.String(255), nullable=False)
    location = db.Column(db.String(255), nullable=False)
    branch = db.Column(db.String(255), nullable=True)  # Филиал
    forestry = db.Column(db.String(255), nullable=True)  # Лесничество
    quarter = db.Column(db.String(255), nullable=True)  # Квартал
    allotment = db.Column(db.String(255), nullable=True)  # Выдел
    damage_area = db.Column(db.Numeric(10, 4))
    damage_les = db.Column(db.Numeric(10, 4))
    damage_les_lesopokryt = db.Column(db.Numeric(10, 4))
    damage_les_verh = db.Column(db.Numeric(10, 4))
    damage_not_les = db.Column(db.Numeric(10, 4))
    lo_flag = db.Column(db.Boolean, default=False)
    lo_people_count = db.Column(db.Integer, nullable=True)
    lo_technic_count = db.Column(db.Integer, nullable=True)
    aps_flag = db.Column(db.Boolean, default=False)
    aps_people_count = db.Column(db.Integer, nullable=True)
    aps_technic_count = db.Column(db.Integer, nullable=True)
    aps_aircraft_count = db.Column(db.Integer, nullable=True)
    kps_flag = db.Column(db.Boolean, default=False)
    kps_people_count = db.Column(db.Integer, nullable=True)
    kps_technic_count = db.Column(db.Integer, nullable=True)
    kps_aircraft_count = db.Column(db.Integer, nullable=True)
    mio_flag = db.Column(db.Boolean, default=False)
    mio_people_count = db.Column(db.Integer, nullable=True)
    mio_technic_count = db.Column(db.Integer, nullable=True)
    mio_aircraft_count = db.Column(db.Integer, nullable=True)
    other_org_flag = db.Column(db.Boolean, default=False)
    other_org_people_count = db.Column(db.Integer, nullable=True)
    other_org_technic_count = db.Column(db.Integer, nullable=True)
    other_org_aircraft_count = db.Column(db.Integer, nullable=True)
    description = db.Column(db.Text)
    damage_tenge = db.Column(db.Integer, nullable=True)
    firefighting_costs = db.Column(db.Integer, nullable=True)
    kpo = db.Column(db.Integer, nullable=True)
    file_path = db.Column(db.String(255))
    edited_by_engineer = db.Column(db.Boolean, default=False)

class AuditLog(db.Model):
    __tablename__ = 'audit_logs'
    id = db.Column(db.Integer, primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    action = db.Column(db.String(50), nullable=False)
    table_name = db.Column(db.String(50), nullable=False)
    record_id = db.Column(db.Integer, nullable=False)
    changes = db.Column(db.Text, nullable=True)