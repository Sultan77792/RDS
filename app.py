from flask import Flask, jsonify, request, render_template
from flask_login import LoginManager, current_user, login_required
from infrastructure.database import db
from adapters.controllers.fire_controller import FireController, fire_bp
from adapters.controllers.dashboard_controller import dashboard_bp, DashboardController, init_dashboard
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from adapters.repositories.region_repository import SQLAlchemyRegionRepository
from core.models import User
from sqlalchemy.sql import text
from datetime import datetime
import json
import logging
from adapters.controllers import user_controller

# Настройка логирования
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def create_app():
    app = Flask(__name__)
    app.config.from_object('config.Config')

    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'fire.login'

    @login_manager.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    @app.template_filter('format_number')
    def format_number(value):
        if value is None:
            return '—'
        return "{:,.2f}".format(float(value)).replace(',', ' ').replace('.00', '')

    fire_repository = SQLAlchemyFireRepository()
    region_repository = SQLAlchemyRegionRepository()

    fire_controller = FireController(fire_repository, region_repository)
    dashboard_controller = DashboardController(fire_repository)
    init_dashboard(fire_repository)

    fire_bp.add_url_rule('/', 'home', FireController.home)
    fire_bp.add_url_rule('/login', 'login', FireController.login, methods=['GET', 'POST'])
    fire_bp.add_url_rule('/logout', 'logout', FireController.logout)
    fire_bp.add_url_rule('/form', 'add_fire', fire_controller.add_fire, methods=['GET', 'POST'])
    fire_bp.add_url_rule('/edit/<int:fire_id>', 'edit_fire', fire_controller.edit_fire, methods=['GET', 'POST'])
    fire_bp.add_url_rule('/delete/<int:fire_id>', 'delete_fire', fire_controller.delete_fire, methods=['POST'])
    fire_bp.add_url_rule('/admin-dashboard', 'admin_dashboard', fire_controller.admin_dashboard)
    fire_bp.add_url_rule('/download/<filename>', 'download_file', FireController.download_file, methods=['GET'])
    fire_bp.add_url_rule('/export-audit', 'export_audit', fire_controller.export_audit)

    app.register_blueprint(fire_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(user_controller.user_bp, url_prefix='/users')


    @app.route('/api/fires', methods=['GET'])
    @login_required
    def get_fires_data():
        try:
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            regions = request.args.getlist('regions')

            logger.debug(f"Получены параметры: start_date={start_date}, end_date={end_date}, regions={regions}")

            fires = fire_repository.get_all()

            # Приведение типов дат к datetime.date
            if start_date:
                start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
                fires = [f for f in fires if f.date and f.date >= start_date]
            if end_date:
                end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
                fires = [f for f in fires if f.date and f.date <= end_date]
            if regions and 'all' not in regions:
                fires = [f for f in fires if f.region in regions]

            logger.debug(f"API /api/fires: Найдено {len(fires)} пожаров после фильтрации")

            region_data = {}
            for fire in fires:
                region = fire.region
                if region not in region_data:
                    region_data[region] = {
                        'region': region,
                        'fire_count': 0,
                        'total_damage_area': 0,
                        'total_damage_tenge': 0,
                        'total_people': 0,
                        'total_technic': 0,
                        'total_aircraft': 0,
                        'aps_people': 0,
                        'aps_technic': 0,
                        'aps_aircraft': 0,
                        'date': fire.date.strftime('%Y-%m-%d') if fire.date else None
                    }
                region_data[region]['fire_count'] += 1
                region_data[region]['total_damage_area'] += fire.damage_area or 0
                region_data[region]['total_damage_tenge'] += fire.damage_tenge or 0
                region_data[region]['total_people'] += (
                    (fire.lo_people_count or 0) + (fire.aps_people_count or 0) +
                    (fire.kps_people_count or 0) + (fire.mio_people_count or 0) +
                    (fire.other_org_people_count or 0)
                )
                region_data[region]['total_technic'] += (
                    (fire.lo_technic_count or 0) + (fire.aps_technic_count or 0) +
                    (fire.kps_technic_count or 0) + (fire.mio_technic_count or 0) +
                    (fire.other_org_technic_count or 0)
                )
                region_data[region]['total_aircraft'] += (
                    (fire.aps_aircraft_count or 0) + (fire.kps_aircraft_count or 0) +
                    (fire.mio_aircraft_count or 0) + (fire.other_org_aircraft_count or 0)
                )
                region_data[region]['aps_people'] += fire.aps_people_count or 0
                region_data[region]['aps_technic'] += fire.aps_technic_count or 0
                region_data[region]['aps_aircraft'] += fire.aps_aircraft_count or 0

            summary_data = list(region_data.values())
            totals = {
                'fire_count': sum(row['fire_count'] for row in summary_data),
                'damage_area': sum(row['total_damage_area'] for row in summary_data),
                'damage_tenge': sum(row['total_damage_tenge'] for row in summary_data),
                'people': sum(row['total_people'] for row in summary_data),
                'technic': sum(row['total_technic'] for row in summary_data),
                'aircraft': sum(row['total_aircraft'] for row in summary_data),
                'aps_people': sum(row['aps_people'] for row in summary_data),
                'aps_technic': sum(row['aps_technic'] for row in summary_data),
                'aps_aircraft': sum(row['aps_aircraft'] for row in summary_data)
            }

            try:
                with open('static/regions.geojson', 'r', encoding='utf-8') as f:
                    geojson_data = json.load(f)
                region_damage = {row['region']: row['total_damage_area'] for row in summary_data}
                for feature in geojson_data['features']:
                    region = feature['properties']['region']
                    feature['properties']['damage_area'] = region_damage.get(region, 0)
                with open('static/regions.geojson', 'w', encoding='utf-8') as f:
                    json.dump(geojson_data, f, ensure_ascii=False)
                logger.debug("GeoJSON успешно обновлён")
            except Exception as e:
                logger.error(f"Ошибка при обновлении GeoJSON: {str(e)}")

            return jsonify({'summary_data': summary_data, 'totals': totals})
        except Exception as e:
            logger.error(f"Ошибка в API /api/fires: {str(e)}")
            return jsonify({'error': 'Внутренняя ошибка сервера', 'details': str(e)}), 500

    @app.route('/dashboard')
    @login_required
    def dashboard():
        fires = fire_repository.get_all()
        region_data = {}
        for fire in fires:
            region = fire.region
            if region not in region_data:
                region_data[region] = {
                    'region': region,
                    'fire_count': 0,
                    'total_damage_area': 0,
                    'total_damage_tenge': 0,
                    'total_people': 0,
                    'total_technic': 0,
                    'total_aircraft': 0,
                    'aps_people': 0,
                    'aps_technic': 0,
                    'aps_aircraft': 0,
                    'date': fire.date.strftime('%Y-%m-%d') if fire.date else None
                }
            region_data[region]['fire_count'] += 1
            region_data[region]['total_damage_area'] += fire.damage_area or 0
            region_data[region]['total_damage_tenge'] += fire.damage_tenge or 0
            region_data[region]['total_people'] += (
                (fire.lo_people_count or 0) + (fire.aps_people_count or 0) +
                (fire.kps_people_count or 0) + (fire.mio_people_count or 0) +
                (fire.other_org_people_count or 0)
            )
            region_data[region]['total_technic'] += (
                (fire.lo_technic_count or 0) + (fire.aps_technic_count or 0) +
                (fire.kps_technic_count or 0) + (fire.mio_technic_count or 0) +
                (fire.other_org_technic_count or 0)
            )
            region_data[region]['total_aircraft'] += (
                (fire.aps_aircraft_count or 0) + (fire.kps_aircraft_count or 0) +
                (fire.mio_aircraft_count or 0) + (fire.other_org_aircraft_count or 0)
            )
            region_data[region]['aps_people'] += fire.aps_people_count or 0
            region_data[region]['aps_technic'] += fire.aps_technic_count or 0
            region_data[region]['aps_aircraft'] += fire.aps_aircraft_count or 0

        summary_data = list(region_data.values())
        totals = {
            'fire_count': sum(row['fire_count'] for row in summary_data),
            'damage_area': sum(row['total_damage_area'] for row in summary_data),
            'damage_tenge': sum(row['total_damage_tenge'] for row in summary_data),
            'people': sum(row['total_people'] for row in summary_data),
            'technic': sum(row['total_technic'] for row in summary_data),
            'aircraft': sum(row['total_aircraft'] for row in summary_data)
        }

        return render_template(
            'dashboard.html',
            summary_data=summary_data,
            totals=totals,
            start_date=None,
            end_date=None
        )

    with app.app_context():
        db.create_all()
        inspector = db.inspect(db.engine)
        columns = inspector.get_columns('fires')
        column_names = [col['name'] for col in columns]
        renames = {
            'lo_tecnic_count': 'lo_technic_count',
            'aps_tecnic_count': 'aps_technic_count',
            'kps_tecnic_count': 'kps_technic_count',
            'mio_tecnic_count': 'mio_technic_count',
            'other_org_tecnic_count': 'other_org_technic_count'
        }
        for old_name, new_name in renames.items():
            if old_name in column_names and new_name not in column_names:
                sql = text(f'ALTER TABLE fires RENAME COLUMN {old_name} TO {new_name};')
                db.session.execute(sql)
                logger.info(f"Переименован столбец {old_name} в {new_name}")
        db.session.commit()

        admin_user = User.query.filter_by(username="admin").first()
        if not admin_user:
            admin = User(username="admin", roles="admin", region="default_region")
            admin.set_password("admin123")
            db.session.add(admin)
            logger.info("Создан пользователь 'admin' с паролем 'admin123' и ролью 'admin'")
        elif admin_user.roles != "admin":
            admin_user.roles = "admin"
            logger.info("Обновлены роли пользователя 'admin' на 'admin'")
        db.session.commit()

    return app

if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)