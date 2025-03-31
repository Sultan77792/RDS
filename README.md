**Описание**:  
- `README.md` содержит:  
  - Описание проекта и его возможностей.  
  - Используемые технологии.  
  - Структуру проекта.  
  - Инструкции по установке, запуску и тестированию.  
  - Примечания о дополнительных настройках (например, GeoJSON).

# Аналитика лесных пожаров

Это веб-приложение для учета, анализа и визуализации данных о лесных пожарах в Казахстане. Проект построен с использованием чистой архитектуры (Clean Architecture), что обеспечивает разделение бизнес-логики, интерфейсов и инфраструктуры.

## Основные возможности
- Регистрация и редактирование данных о пожарах (дата, регион, площадь, ущерб, задействованные ресурсы и т.д.).
- Авторизация пользователей с ролями: администратор, инженер, оператор, аналитик.
- Логирование действий пользователей в таблице аудита.
- Интерактивный дашборд с визуализацией данных (карта, графики, индикаторы).
- Экспорт данных в таблицы и загрузка файлов.

## Технологии
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
- **Frontend**: HTML, Dash (Plotly, Pandas)
- **База данных**: MySQL
- **Тестирование**: unittest

## Структура проекта

Хорошо, продолжаем с пунктом 9 — созданием README.md. Этот файл содержит документацию проекта, включая описание, инструкции по установке и запуску, а также структуру.

20. README.md — Документация проекта
markdown

Копировать
# Аналитика лесных пожаров

Это веб-приложение для учета, анализа и визуализации данных о лесных пожарах в Казахстане. Проект построен с использованием чистой архитектуры (Clean Architecture), что обеспечивает разделение бизнес-логики, интерфейсов и инфраструктуры.

## Основные возможности
- Регистрация и редактирование данных о пожарах (дата, регион, площадь, ущерб, задействованные ресурсы и т.д.).
- Авторизация пользователей с ролями: администратор, инженер, оператор, аналитик.
- Логирование действий пользователей в таблице аудита.
- Интерактивный дашборд с визуализацией данных (карта, графики, индикаторы).
- Экспорт данных в таблицы и загрузка файлов.

## Технологии
- **Backend**: Flask, Flask-SQLAlchemy, Flask-Login, Flask-Migrate, Flask-WTF
- **Frontend**: HTML, Dash (Plotly, Pandas)
- **База данных**: MySQL
- **Тестирование**: unittest

## Структура проекта
FIRE
├── app.py                # Точка входа
├── config.py             # Конфигурации
├── requirements.txt      # Зависимости
├── README.md             # Документация
├── regions.py            # Данные регионов
├── forms.py              # Формы WTForms
│
├── core/                 # Бизнес-логика
│   ├── entities.py       # Сущности (FireEntity, UserEntity, AuditLogEntity)
│   ├── models.py         # Модели SQLAlchemy
│
├── use_cases/            # Сценарии использования
│   ├── fire_analysis.py  # Анализ пожаров
│   ├── region_operations.py  # Операции с регионами
│
├── adapters/             # Адаптеры интерфейсов
│   ├── controllers/
│   │   ├── dashboard_controller.py  # Управление дашбордом
│   │   ├── fire_controller.py       # Управление пожарами
│   ├── repositories/
│   │   ├── fire_repository.py       # Доступ к данным пожаров
│   │   ├── region_repository.py     # Доступ к данным регионов
│
├── infrastructure/       # Инфраструктура
│   ├── database.py       # Инициализация базы данных
│   ├── extensions.py     # Расширения Flask
│
├── tests/                # Тесты
│   ├── test_fire_analysis.py
│   ├── test_dashboard.py
│   ├── test_fire_controller.py
│   ├── test_region_operations.py
│   ├── test_repositories.py
│
├── static/               # Статические файлы
│   ├── geojson/          # GeoJSON для карты
│   │   └── regions.geojson
│
├── templates/            # Шаблоны HTML
│   ├── login.html
│   ├── form.html
│   ├── edit_fire.html
│   ├── admin_dashboard.html
│   ├── dashboard.html
│   ├── summary.html
│
└── uploads/              # Папка для загружаемых файлов

## Установка
1. **Клонируйте репозиторий**:
   bash
   git clone <repository-url>
   cd fire-incidents

   
## Создайте виртуальное окружение:
bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows

## Установите зависимости:
bash
pip install -r requirements.txt

## Настройте базу данных:
Установите MySQL и создайте базу данных fire_incidents.
Обновите SQLALCHEMY_DATABASE_URI в config.py, если требуется:
python
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://<username>:<password>@localhost/fire_incidents'

## Инициализируйте базу данных:
bash
flask db init
flask db migrate
flask db upgrade

## Запустите приложение:
bash
python app.py
Откройте браузер и перейдите по адресу:
Flask: http://127.0.0.1:5000/
Dash: http://127.0.0.1:5000/dash/

## Использование
Логин: Используйте учетные данные (например, admin/admin для администратора).
Добавление пожара: Перейдите в /form (доступно для операторов, инженеров, админов).
Админ-панель: /admin-dashboard (для админов и инженеров).
Дашборд: /dash/ (для аналитиков).

## Тестирование
Запустите тесты:
bash
python -m unittest discover -s tests

Лицензия
MIT License