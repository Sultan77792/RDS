from flask import Blueprint, render_template, request, flash, redirect, url_for, send_file, abort, Response, jsonify
from flask_login import login_required, current_user, login_user, logout_user
from functools import wraps
from werkzeug.utils import secure_filename
from datetime import datetime
import os
import csv
import io
import logging
from tenacity import retry, stop_after_attempt, wait_fixed, retry_if_exception_type
from config import Config
from core.entities import FireEntity, AuditLogEntity
from core.models import AuditLog, User
from use_cases.fire_analysis import FireAnalysis
from use_cases.region_operations import RegionOperations
from adapters.repositories.fire_repository import SQLAlchemyFireRepository
from adapters.repositories.region_repository import SQLAlchemyRegionRepository
from forms import FireForm, LoginForm
from infrastructure.database import db

# Настройка логирования только для нашего приложения
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Создаем обработчик для вывода логов в консоль
handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)

# Формат логов с полем username
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(username)s - %(message)s')
handler.setFormatter(formatter)

# Добавляем обработчик к логгеру
logger.addHandler(handler)

# Фильтр для добавления имени пользователя
class UserFilter(logging.Filter):
    """Фильтр логов по текущему пользователю."""
    def filter(self, record):
        from flask_login import current_user
        try:
            if current_user and hasattr(current_user, 'is_authenticated') and current_user.is_authenticated:
                record.username = getattr(current_user, 'username', 'anonymous')
            else:
                record.username = 'anonymous'
        except Exception:
            record.username = 'anonymous'
        return True

logger.addFilter(UserFilter())

fire_bp = Blueprint('fire', __name__)

def roles_required(*roles):
    """Декоратор для проверки ролей пользователя."""
    def decorator(func):
        @wraps(func)
        @login_required
        def wrapper(*args, **kwargs):
            user_roles = getattr(current_user, 'roles', '') or ''
            logger.debug(f"Checking roles: {user_roles} against required {roles}")
            if not any(role in roles for role in user_roles.split(',')):
                logger.warning(f"Access denied with roles {user_roles}")
                flash("Доступ запрещен.", "danger")
                return abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator

class FireController:
    def __init__(self, fire_repository: SQLAlchemyFireRepository, region_repository: SQLAlchemyRegionRepository):
        """Инициализация контроллера с репозиториями пожаров и регионов."""
        self.fire_analysis = FireAnalysis(fire_repository)
        self.region_ops = RegionOperations(region_repository)
        logger.info("FireController initialized")

    @staticmethod
    def home():
        """Отображение главной страницы с формой логина."""
        logger.debug("Rendering home page")
        form = LoginForm()
        return render_template('login.html', form=form)

    @staticmethod
    def login():
        """Обработка входа пользователя в систему."""
        logger.debug("Processing login request")
        form = LoginForm()
        if form.validate_on_submit():
            user = User.query.filter_by(username=form.username.data).first()
            if user and user.check_password(form.password.data):
                login_user(user)
                FireController._log_event(user.username, "Вход", "User", user.id, "Успешный вход")
                flash('Успешный вход в систему.', 'success')
                roles = user.roles or ""
                logger.info(f"Logged in with roles: {roles}")
                if 'engineer' in roles.split(',') or 'analyst' in roles.split(','):
                    return redirect(url_for('dashboard.dashboard'))
                elif 'admin' in roles.split(','):
                    return redirect(url_for('fire.admin_dashboard'))
                return redirect(url_for('dashboard.dashboard'))
            else:
                FireController._log_event(form.username.data, "Вход", "User", None, "Неуспешная попытка")
                logger.warning(f"Failed login attempt for {form.username.data}")
                flash('Неверное имя пользователя или пароль', 'danger')
        return render_template('login.html', form=form)

    @staticmethod
    def logout():
        """Выход пользователя из системы."""
        logger.info("Logging out")
        FireController._log_event(current_user.username, "Выход", "User", current_user.id, "Успешный выход")
        logout_user()
        flash('Вы вышли из системы.', 'success')
        return redirect(url_for('fire.login'))

    @roles_required('operator', 'admin', 'engineer')
    def add_fire(self):
        """Добавление нового пожара."""
        logger.debug("Processing add_fire request")
        form = FireForm()
        self._populate_form_choices(form)

        if form.validate_on_submit():
            try:
                file = request.files.get('file')
                filename = None
                if file and self._allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = Config.UPLOAD_FOLDER
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, filename))
                    logger.debug(f"File uploaded: {filename}")

                fire = FireEntity(
                    id=0,
                    date=form.date.data,
                    region=form.region.data,
                    location=form.location.data,
                    branch=form.branch.data,
                    forestry=form.forestry.data,
                    quarter=form.quarter.data,
                    allotment=form.allotment.data,
                    damage_area=form.damage_area.data or 0.0,
                    damage_les=form.damage_les.data,
                    damage_les_lesopokryt=form.damage_les_lesopokryt.data,
                    damage_les_verh=form.damage_les_verh.data,
                    damage_not_les=form.damage_not_les.data,
                    lo_flag=form.lo_flag.data,
                    lo_people_count=form.lo_people_count.data,
                    lo_technic_count=form.lo_technic_count.data,
                    aps_flag=form.aps_flag.data,
                    aps_people_count=form.aps_people_count.data,
                    aps_technic_count=form.aps_technic_count.data,
                    aps_aircraft_count=form.aps_aircraft_count.data,
                    kps_flag=form.kps_flag.data,
                    kps_people_count=form.kps_people_count.data,
                    kps_technic_count=form.kps_technic_count.data,
                    kps_aircraft_count=form.kps_aircraft_count.data,
                    mio_flag=form.mio_flag.data,
                    mio_people_count=form.mio_people_count.data,
                    mio_technic_count=form.mio_technic_count.data,
                    mio_aircraft_count=form.mio_aircraft_count.data,
                    other_org_flag=form.other_org_flag.data,
                    other_org_people_count=form.other_org_people_count.data,
                    other_org_technic_count=form.other_org_technic_count.data,
                    other_org_aircraft_count=form.other_org_aircraft_count.data,
                    description=form.description.data,
                    damage_tenge=form.damage_tenge.data,
                    firefighting_costs=form.firefighting_costs.data,
                    kpo=form.kpo.data,
                    file_path=filename,
                    edited_by_engineer=False
                )
                saved_fire = self.fire_analysis.add_fire(fire)
                self._log_event(current_user.username, "Создание", "Fire", saved_fire.id, "Добавлен новый пожар")
                flash('Данные успешно добавлены!', 'success')
                logger.info(f"Fire added with ID {saved_fire.id}")
                return redirect(url_for('dashboard.dashboard'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error adding fire: {str(e)}")
                flash(f'Ошибка при добавлении данных: {str(e)}', 'danger')
        return render_template('add_fire.html', form=form, regions_and_locations=self.region_ops.region_repository.get_region_location_mapping())

    @roles_required('admin', 'engineer')
    def edit_fire(self, fire_id):
        """Редактирование существующего пожара."""
        logger.debug(f"Processing edit_fire request for fire_id: {fire_id}")
        fire = self.fire_analysis.fire_repository.get_by_id(fire_id)
        if not fire:
            logger.warning(f"Fire with ID {fire_id} not found")
            flash('Пожар не найден.', 'danger')
            return redirect(url_for('fire.admin_dashboard'))

        if 'engineer' in (current_user.roles or '').split(',') and fire.region != current_user.region:
            logger.warning(f"No permission to edit fire {fire_id} in region {fire.region}")
            flash('У вас нет прав редактировать этот пожар.', 'danger')
            return redirect(url_for('fire.admin_dashboard'))

        old_data = vars(fire).copy()
        form = FireForm(obj=fire)
        self._populate_form_choices(form)

        if form.validate_on_submit():
            try:
                file = request.files.get('file')
                if file and self._allowed_file(file.filename):
                    filename = secure_filename(file.filename)
                    upload_folder = Config.UPLOAD_FOLDER
                    os.makedirs(upload_folder, exist_ok=True)
                    file.save(os.path.join(upload_folder, filename))
                    fire.file_path = filename
                    logger.debug(f"New file uploaded: {filename}")

                form.populate_obj(fire)
                updated_fire = self.fire_analysis.update_fire(fire)
                changes = [
                    f"{key}: {old_data[key]} -> {getattr(updated_fire, key)}"
                    for key in old_data
                    if old_data[key] != getattr(updated_fire, key) and key != '_sa_instance_state'
                ]
                if changes:
                    self._log_event(
                        current_user.username,
                        "Обновление",
                        "Fire",
                        fire_id,
                        "; ".join(changes)
                    )
                    logger.info(f"Fire {fire_id} updated: {changes}")
                flash('Данные успешно обновлены!', 'success')
                return redirect(url_for('fire.admin_dashboard'))
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error updating fire {fire_id}: {str(e)}")
                flash(f'Ошибка при обновлении данных: {str(e)}', 'danger')
        return render_template(
            'edit_fire.html',
            form=form,
            fire=fire,
            regions_and_locations=self.region_ops.region_repository.get_region_location_mapping()
        )

    @roles_required('admin')
    def delete_fire(self, fire_id):
        """Удаление пожара."""
        logger.debug(f"Processing delete_fire request for fire_id: {fire_id}")
        fire = self.fire_analysis.fire_repository.get_by_id(fire_id)
        if fire:
            try:
                self.fire_analysis.delete_fire(fire_id)
                self._log_event(
                    current_user.username,
                    "Удаление",
                    "Fire",
                    fire_id,
                    f"Удалена запись о пожаре с ID {fire_id}"
                )
                flash(f'Запись о пожаре с ID {fire_id} успешно удалена.', 'success')
                logger.info(f"Fire {fire_id} deleted")
            except Exception as e:
                db.session.rollback()
                logger.error(f"Error deleting fire {fire_id}: {str(e)}")
                flash(f'Ошибка при удалении: {str(e)}', 'danger')
        else:
            logger.warning(f"Fire with ID {fire_id} not found")
            flash(f'Пожар с ID {fire_id} не найден.', 'danger')
        return redirect(url_for('fire.admin_dashboard'))

    @roles_required('admin', 'engineer', 'analyst')
    def admin_dashboard(self):
        """Отображение админ-панели с данными о пожарах и логами."""
        logger.debug("Rendering admin_dashboard")
        if 'engineer' in (current_user.roles or '').split(','):
            fires = self.fire_analysis.get_fires_by_region(current_user.region)
        else:
            fires = self.fire_analysis.fire_repository.get_all()
        audit_logs = db.session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all() if 'admin' in (current_user.roles or '').split(',') else []
        logger.info(f"Fires count: {len(fires)}, Audit logs count: {len(audit_logs)}")
        return render_template(
            'admin_dashboard.html',
            fires=fires,
            audit_logs=audit_logs,
            current_role=current_user.roles if current_user.is_authenticated else None
        )

    @staticmethod
    @login_required
    def download_file(filename):
        """Скачивание прикрепленного файла."""
        logger.debug(f"Processing download request for file: {filename}")
        file_path = os.path.join(Config.UPLOAD_FOLDER, filename)
        if os.path.exists(file_path):
            logger.info(f"File {filename} downloaded")
            return send_file(file_path, as_attachment=True)
        logger.warning(f"File {filename} not found")
        flash('Файл не найден.', 'danger')
        return redirect(url_for('dashboard.dashboard'))

    @roles_required('admin')
    def export_audit(self):
        """Экспорт журнала аудита в CSV."""
        logger.debug("Processing export_audit request")
        audit_logs = db.session.query(AuditLog).order_by(AuditLog.timestamp.desc()).all()
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Timestamp', 'Username', 'Action', 'Table Name', 'Record ID', 'Changes'])
        for log in audit_logs:
            writer.writerow([log.timestamp, log.username, log.action, log.table_name, log.record_id, log.changes])
        output.seek(0)
        logger.info(f"Exported {len(audit_logs)} audit logs to CSV")
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment;filename=audit_log.csv"}
        )

    @roles_required('operator', 'admin', 'engineer')
    def get_locations(self):
        """Получение списка локаций для выбранного региона (для AJAX)."""
        region = request.args.get('region')
        if not region:
            return jsonify({'error': 'Регион не указан'}), 400
        locations = self.region_ops.get_locations_by_region(region)
        logger.debug(f"Fetched {len(locations)} locations for region {region}")
        return jsonify({'locations': locations})

    def _populate_form_choices(self, form):
        """Заполнение полей формы в зависимости от роли пользователя."""
        logger.debug("Populating form choices")
        if 'admin' in (current_user.roles or '').split(','):
            regions = self.region_ops.get_all_regions()
            form.region.choices = [(r, r) for r in regions]
        else:
            form.region.choices = [(current_user.region, current_user.region)]

        selected_region = request.form.get('region', form.region.data) or current_user.region
        if selected_region:
            locations = self.region_ops.get_locations_by_region(selected_region)
            form.location.choices = [(loc, loc) for loc in locations]
            logger.debug(f"Populated {len(locations)} locations for region {selected_region}")
        else:
            form.location.choices = []
            logger.debug("No region selected, location choices empty")

    def _allowed_file(self, filename):
        """Проверка допустимого расширения файла."""
        allowed = '.' in filename and filename.rsplit('.', 1)[1].lower() in Config.ALLOWED_EXTENSIONS
        logger.debug(f"Checking file {filename}: Allowed={allowed}")
        return allowed

    @retry(stop_after_attempt(3), wait_fixed(1), retry_if_exception_type(Exception))
    @staticmethod
    def _log_event(username: str, action: str, table_name: str, record_id: int, changes: str = None):
        """Запись события в лог аудита с повторными попытками."""
        logger.debug(f"Logging event: {action} on {table_name} ID {record_id}")
        try:
            audit_log = AuditLog(
                timestamp=datetime.utcnow(),
                username=username,
                action=action,
                table_name=table_name,
                record_id=record_id,
                changes=changes
            )
            db.session.add(audit_log)
            db.session.commit()
            logger.info(f"Audit log entry created: {action} on {table_name} ID {record_id}")
        except Exception as e:
            db.session.rollback()
            logger.error(f"Failed to log event after retries: {str(e)}")
            raise