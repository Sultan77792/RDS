from flask import render_template, flash, redirect, url_for, request, send_file, abort, Response, jsonify
from flask_login import login_required, current_user, login_user, logout_user
import logging
import io
import csv
from datetime import datetime
from werkzeug.utils import secure_filename
import os
from services.fire_service import UserService
from schemas.fire_schema import FireCreateSchema, FireUpdateSchema
from forms import FireForm, LoginForm
from utils.decorators import roles_required
from config import Config
import sys
print(sys.path)

logger = logging.getLogger(__name__)

class FireController:
    def __init__(self, fire_service: UserService):
        self.fire_service = fire_service
        logger.info("FireController initialized")

    # --- Аутентификация ---
    def home(self):
        logger.debug("Rendering home page")
        form = LoginForm()
        return render_template('login.html', form=form)

    def login(self):
        logger.debug("Processing login request")
        form = LoginForm()
        if form.validate_on_submit():
            try:
                user = self.fire_service.authenticate(form.username.data, form.password.data)
                if user:
                    login_user(user)
                    self.fire_service.log_event(
                        user.username,
                        "Вход",
                        "User",
                        user.id,
                        "Успешный вход"
                    )
                    flash('Успешный вход в систему.', 'success')
                    return self._redirect_by_role(user.roles)
                
                self.fire_service.log_event(
                    form.username.data,
                    "Вход",
                    "User",
                    None,
                    "Неуспешная попытка"
                )
                flash('Неверное имя пользователя или пароль', 'danger')
            except Exception as e:
                logger.error(f"Login error: {str(e)}")
                flash('Ошибка при входе. Попробуйте позже.', 'danger')
        return render_template('login.html', form=form)

    @login_required  # Если не нужен логин, удали эту строку
    def get_fires(self):
        """Получить список пожаров"""
        logger.debug("Fetching all fires")
        fires = self.fire_service.get_all_fires()
        return jsonify([fire.to_dict() for fire in fires])

    @login_required
    def logout(self):
        logger.info(f"User {current_user.username} logging out")
        self.fire_service.log_event(
            current_user.username,
            "Выход",
            "User",
            current_user.id,
            "Успешный выход"
        )
        logout_user()
        flash('Вы вышли из системы.', 'success')
        return redirect(url_for('fire.login'))

    # --- Управление пожарами ---
    @roles_required('analyst', 'admin', 'engineer')
    def add_fire(self):
        logger.debug("Processing add_fire request")
        form = FireForm()
        self._populate_form_choices(form)

        if form.validate_on_submit():
            try:
                fire_data = FireCreateSchema(**form.data)
                saved_fire = self.fire_service.add_fire(
                    fire_data,
                    request.files.get('file'),
                    current_user.username
                )
                flash('Данные успешно добавлены!', 'success')
                logger.info(f"Added fire ID {saved_fire.id}")
                return redirect(url_for('dashboard.dashboard'))
            except Exception as e:
                logger.error(f"Error adding fire: {str(e)}")
                flash(f'Ошибка при добавлении: {str(e)}', 'danger')

        regions_and_locations = self.fire_service.get_region_location_mapping()
        return render_template(
            'add_fire.html',
            form=form,
            regions_and_locations=regions_and_locations
        )

    @roles_required('admin', 'engineer')
    def edit_fire(self, fire_id):
        logger.debug(f"Editing fire ID {fire_id}")
        fire = self.fire_service.get_fire_by_id(fire_id)
        if not fire:
            flash('Пожар не найден.', 'danger')
            return redirect(url_for('fire.admin_dashboard'))

        # Проверка доступа инженера к региону
        if 'engineer' in current_user.roles.split(',') and fire.region != current_user.region:
            flash('Нет прав на редактирование этого пожара.', 'danger')
            return redirect(url_for('fire.admin_dashboard'))

        form = FireForm(obj=fire)
        self._populate_form_choices(form)

        if form.validate_on_submit():
            try:
                fire_data = FireUpdateSchema(**form.data, id=fire_id)
                updated_fire = self.fire_service.update_fire(
                    fire_data,
                    request.files.get('file'),
                    current_user.username
                )
                flash('Данные обновлены!', 'success')
                return redirect(url_for('fire.admin_dashboard'))
            except Exception as e:
                logger.error(f"Error updating fire {fire_id}: {str(e)}")
                flash(f'Ошибка при обновлении: {str(e)}', 'danger')

        return render_template(
            'edit_fire.html',
            form=form,
            fire=fire,
            regions_and_locations=self.fire_service.get_region_location_mapping()
        )

    @roles_required('admin')
    def delete_fire(self, fire_id):
        logger.debug(f"Deleting fire ID {fire_id}")
        try:
            self.fire_service.delete_fire(fire_id, current_user.username)
            flash('Пожар удален.', 'success')
        except Exception as e:
            logger.error(f"Error deleting fire {fire_id}: {str(e)}")
            flash(f'Ошибка при удалении: {str(e)}', 'danger')
        return redirect(url_for('fire.admin_dashboard'))

    # --- Dashboard и отчеты ---
    @roles_required('admin', 'engineer', 'analyst')
    def admin_dashboard(self):
        logger.debug("Rendering admin dashboard")
        if 'engineer' in current_user.roles.split(','):
            fires = self.fire_service.get_fires_by_region(current_user.region)
        else:
            fires = self.fire_service.get_all_fires()

        audit_logs = []
        if 'admin' in current_user.roles.split(','):
            audit_logs = self.fire_service.export_audit_logs()

        return render_template(
            'admin_dashboard.html',
            fires=fires,
            audit_logs=audit_logs,
            current_role=current_user.roles
        )

    @roles_required('admin')
    def export_audit(self):
        logger.debug("Exporting audit logs")
        try:
            csv_data = self.fire_service.export_audit_logs()
            return Response(
                csv_data,
                mimetype="text/csv",
                headers={"Content-Disposition": "attachment;filename=audit_log.csv"}
            )
        except Exception as e:
            logger.error(f"Export error: {str(e)}")
            flash('Ошибка при экспорте', 'danger')
            return redirect(url_for('fire.admin_dashboard'))

    # --- Вспомогательные методы ---
    @roles_required('analyst', 'admin', 'engineer')
    def get_locations(self):
        region = request.args.get('region')
        if not region:
            return jsonify({'error': 'Регион не указан'}), 400
        locations = self.fire_service.get_locations_by_region(region)
        return jsonify({'locations': locations})

    @login_required
    def download_file(self, filename):
        logger.debug(f"Downloading file {filename}")
        try:
            file_path = os.path.join(Config.UPLOAD_FOLDER, secure_filename(filename))
            if not os.path.exists(file_path):
                flash('Файл не найден', 'danger')
                return redirect(url_for('dashboard.dashboard'))
            return send_file(file_path, as_attachment=True)
        except Exception as e:
            logger.error(f"Download error: {str(e)}")
            flash('Ошибка при загрузке файла', 'danger')
            return redirect(url_for('dashboard.dashboard'))

    def _populate_form_choices(self, form):
        """Заполняет выпадающие списки в форме на основе роли пользователя."""
        if 'admin' in current_user.roles.split(','):
            form.region.choices = [(r, r) for r in self.fire_service.get_all_regions()]
        else:
            form.region.choices = [(current_user.region, current_user.region)]

        selected_region = request.form.get('region', form.region.data) or current_user.region
        if selected_region:
            form.location.choices = [
                (loc, loc) 
                for loc in self.fire_service.get_locations_by_region(selected_region)
            ]

    def _redirect_by_role(self, roles):
        """Перенаправляет пользователя в зависимости от роли."""
        if 'engineer' in roles or 'analyst' in roles:
            return redirect(url_for('dashboard.dashboard'))
        elif 'admin' in roles:
            return redirect(url_for('fire.admin_dashboard'))
        return redirect(url_for('dashboard.dashboard'))