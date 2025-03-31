import os
from flask import Flask

class Config:
    SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:asirius77792amatap35@localhost:5432/fire_incidents'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a-default-fallback-secret-key'
    WTF_CSRF_ENABLED = False
    UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'pdf'}
    MAX_CONTENT_LENGTH = 16 * 1024 * 1024  # Ограничение на размер файла: 16MB

    @staticmethod
    def init_app(app):
        pass

app = Flask(__name__)
app.config.from_object(Config)

# Инициализация приложения с конфигурацией
Config.init_app(app)