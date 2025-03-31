from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from alembic import context
import sys
import os

# Добавляем корневую папку проекта в sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

# Импортируем Flask-приложение и базовые классы
from app import app  # Flask-приложение в корне
from infrastructure.database import db  # Подключение базы данных
from infrastructure.models import Base  # Импорт моделей (или заменить на конкретный путь)

# Настройки Alembic
config = context.config

# Подключаем конфигурацию логирования из alembic.ini
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Метаданные для миграций
target_metadata = Base.metadata  

# Функция для миграций в "offline" режиме
def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

# Функция для миграций в "online" режиме
def run_migrations_online():
    with app.app_context():  # Включаем контекст Flask
        connectable = db.engine  # SQLAlchemy engine

        with connectable.connect() as connection:
            context.configure(
                connection=connection,
                target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()

# Запуск нужного режима
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
