from flask import Flask
from infrastructure.database import init_db, db
from adapters.controllers.fire_controller import fire_bp, FireController
from adapters.controllers.dashboard_controller import dashboard_bp, DashboardController
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from config import Config

app = Flask(__name__)
app.config.from_object(Config)
init_db(app)

# Инициализация репозиториев и контроллеров
fire_repo = SQLAlchemyFireRepository()
fire_controller = FireController(fire_repo)
dashboard_controller = DashboardController(fire_repo)

# Регистрация blueprints
app.register_blueprint(fire_bp)
app.register_blueprint(dashboard_bp)

if __name__ == '__main__':
    app.run(debug=True)