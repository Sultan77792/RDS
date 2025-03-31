from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Инициализация SQLAlchemy
db = SQLAlchemy()

# Инициализация миграций
migrate = Migrate()

def init_db(app):
    """Инициализация базы данных и миграций для приложения."""
    db.init_app(app)
    migrate.init_app(app, db)
    with app.app_context():
        db.create_all()