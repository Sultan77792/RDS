from flask import Blueprint, render_template, request
from flask_login import login_required
from use_cases.fire_analysis import FireAnalysis
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from datetime import datetime

dashboard_bp = Blueprint('dashboard', __name__)

# Глобальная переменная для передачи зависимости (временное решение)
fire_analysis = None

def init_dashboard(fire_repo: SQLAlchemyFireRepository):
    global fire_analysis
    fire_analysis = FireAnalysis(fire_repo)

class DashboardController:
    def __init__(self, fire_repository: SQLAlchemyFireRepository):
        self.fire_analysis = FireAnalysis(fire_repository)
        init_dashboard(fire_repository)  # Инициализируем глобальную переменную

    @staticmethod
    @dashboard_bp.route('/dashboard', methods=['GET', 'POST'])
    @login_required
    def dashboard():
        """Отображение дашборда с аналитикой пожаров."""
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        summary_data = []
        regions = fire_analysis.fire_repository.get_all_regions()
        for region in regions:
            fires = fire_analysis.get_fires_by_region(region, start_date, end_date)
            region_summary = {
                'region': region,
                'fire_count': len(fires),
                'total_damage_area': sum(fire.damage_area or 0 for fire in fires),
                'total_damage_tenge': sum(fire.damage_tenge or 0 for fire in fires),
                'total_people': sum(
                    (fire.lo_people_count or 0) + (fire.aps_people_count or 0) +
                    (fire.kps_people_count or 0) + (fire.mio_people_count or 0) +
                    (fire.other_org_people_count or 0) for fire in fires
                ),
                'total_technic': sum(
                    (fire.lo_technic_count or 0) + (fire.aps_technic_count or 0) +
                    (fire.kps_technic_count or 0) + (fire.mio_technic_count or 0) +
                    (fire.other_org_technic_count or 0) for fire in fires
                ),
                'total_aircraft': sum(
                    (fire.aps_aircraft_count or 0) + (fire.kps_aircraft_count or 0) +
                    (fire.mio_aircraft_count or 0) + (fire.other_org_aircraft_count or 0)
                    for fire in fires
                ),
                'aps_people': sum(fire.aps_people_count or 0 for fire in fires),
                'aps_technic': sum(fire.aps_technic_count or 0 for fire in fires),
                'aps_aircraft': sum(fire.aps_aircraft_count or 0 for fire in fires),
            }
            summary_data.append(region_summary)

        totals = {
            'fire_count': sum(row['fire_count'] for row in summary_data),
            'damage_area': sum(row['total_damage_area'] for row in summary_data),
            'damage_tenge': sum(row['total_damage_tenge'] for row in summary_data),
            'people': sum(row['total_people'] for row in summary_data),
            'technic': sum(row['total_technic'] for row in summary_data),
            'aircraft': sum(row['total_aircraft'] for row in summary_data),
            'aps_people': sum(row['aps_people'] for row in summary_data),
            'aps_technic': sum(row['aps_technic'] for row in summary_data),
            'aps_aircraft': sum(row['aps_aircraft'] for row in summary_data),
        }

        return render_template(
            'dashboard.html',
            summary_data=summary_data,
            totals=totals,
            start_date=start_date,
            end_date=end_date
        )

    @staticmethod
    @dashboard_bp.route('/summary', methods=['GET', 'POST'])
    @login_required
    def summary():
        """Отображение сводной информации по регионам."""
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')

        if start_date:
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if end_date:
            end_date = datetime.strptime(end_date, '%Y-%m-%d')

        summary_data = []
        regions = fire_analysis.fire_repository.get_all_regions()
        for region in regions:
            fires = fire_analysis.get_fires_by_region(region, start_date, end_date)
            region_summary = {
                'region': region,
                'fire_count': len(fires),
                'total_damage_area': sum(fire.damage_area or 0 for fire in fires),
                'total_damage_tenge': sum(fire.damage_tenge or 0 for fire in fires),
                'total_people': sum(
                    (fire.lo_people_count or 0) + (fire.aps_people_count or 0) +
                    (fire.kps_people_count or 0) + (fire.mio_people_count or 0) +
                    (fire.other_org_people_count or 0) for fire in fires
                ),
                'total_technic': sum(
                    (fire.lo_technic_count or 0) + (fire.aps_technic_count or 0) +
                    (fire.kps_technic_count or 0) + (fire.mio_technic_count or 0) +
                    (fire.other_org_technic_count or 0) for fire in fires
                ),
                'total_aircraft': sum(
                    (fire.aps_aircraft_count or 0) + (fire.kps_aircraft_count or 0) +
                    (fire.mio_aircraft_count or 0) + (fire.other_org_aircraft_count or 0)
                    for fire in fires
                ),
                'lo_people': sum(fire.lo_people_count or 0 for fire in fires),
                'lo_technic': sum(fire.lo_technic_count or 0 for fire in fires),
                'aps_people': sum(fire.aps_people_count or 0 for fire in fires),
                'aps_technic': sum(fire.aps_technic_count or 0 for fire in fires),
                'aps_aircraft': sum(fire.aps_aircraft_count or 0 for fire in fires),
                'kps_people': sum(fire.kps_people_count or 0 for fire in fires),
                'kps_technic': sum(fire.kps_technic_count or 0 for fire in fires),
                'kps_aircraft': sum(fire.kps_aircraft_count or 0 for fire in fires),
                'mio_people': sum(fire.mio_people_count or 0 for fire in fires),
                'mio_technic': sum(fire.mio_technic_count or 0 for fire in fires),
                'mio_aircraft': sum(fire.mio_aircraft_count or 0 for fire in fires),
                'other_org_people': sum(fire.other_org_people_count or 0 for fire in fires),
                'other_org_technic': sum(fire.other_org_technic_count or 0 for fire in fires),
                'other_org_aircraft': sum(fire.other_org_aircraft_count or 0 for fire in fires),
            }
            summary_data.append(region_summary)

        totals = {
            'fire_count': sum(row['fire_count'] for row in summary_data),
            'damage_area': sum(row['total_damage_area'] for row in summary_data),
            'damage_tenge': sum(row['total_damage_tenge'] for row in summary_data),
            'people': sum(row['total_people'] for row in summary_data),
            'technic': sum(row['total_technic'] for row in summary_data),
            'aircraft': sum(row['total_aircraft'] for row in summary_data),
            'aps_people': sum(row['aps_people'] for row in summary_data),
            'aps_technic': sum(row['aps_technic'] for row in summary_data),
            'aps_aircraft': sum(row['aps_aircraft'] for row in summary_data),
        }

        return render_template(
            'summary.html',
            summary_data=summary_data,
            start_date=start_date,
            end_date=end_date,
            totals=totals
        )