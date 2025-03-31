from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, DateField, FloatField, IntegerField, BooleanField, TextAreaField, SelectField, FileField
from wtforms.validators import DataRequired, Length, Optional, ValidationError

class LoginForm(FlaskForm):
    """Форма для входа пользователя в систему."""
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(min=2, max=150)])
    password = PasswordField('Пароль', validators=[DataRequired()])

class FireForm(FlaskForm):
    """Форма для добавления и редактирования данных о пожаре."""
    date = DateField('Дата', format='%Y-%m-%d', validators=[DataRequired()])
    region = SelectField('Регион', validators=[DataRequired()], choices=[('', 'Выберите регион')])
    location = SelectField('Местоположение', validators=[DataRequired()], choices=[('', 'Выберите КГУ/ООПТ')])
    branch = StringField('Филиал', validators=[Optional(), Length(max=255)])
    forestry = StringField('Лесничество', validators=[Optional(), Length(max=255)])
    quarter = StringField('Квартал', validators=[Optional(), Length(max=255)])
    allotment = StringField('Выдел', validators=[Optional(), Length(max=255)])
    damage_area = FloatField('Площадь поражения', validators=[Optional()])
    damage_les = FloatField('Ущерб лесу', validators=[Optional()])
    damage_les_lesopokryt = FloatField('Ущерб лесопокрытой территории', validators=[Optional()])
    damage_les_verh = FloatField('Ущерб верховий', validators=[Optional()])
    damage_not_les = FloatField('Ущерб нелесной территории', validators=[Optional()])
    lo_flag = BooleanField('ЛО задействованы', default=False)
    lo_people_count = IntegerField('Количество людей (ЛО)', validators=[Optional()])
    lo_technic_count = IntegerField('Количество техники (ЛО)', validators=[Optional()])
    aps_flag = BooleanField('АПС задействованы', default=False)
    aps_people_count = IntegerField('Количество людей (АПС)', validators=[Optional()])
    aps_technic_count = IntegerField('Количество техники (АПС)', validators=[Optional()])
    aps_aircraft_count = IntegerField('Количество авиации (АПС)', validators=[Optional()])
    kps_flag = BooleanField('КПС задействованы', default=False)
    kps_people_count = IntegerField('Количество людей (КПС)', validators=[Optional()])
    kps_technic_count = IntegerField('Количество техники (КПС)', validators=[Optional()])
    kps_aircraft_count = IntegerField('Количество авиации (КПС)', validators=[Optional()])
    mio_flag = BooleanField('МИО задействованы', default=False)
    mio_people_count = IntegerField('Количество людей (МИО)', validators=[Optional()])
    mio_technic_count = IntegerField('Количество техники (МИО)', validators=[Optional()])
    mio_aircraft_count = IntegerField('Количество авиации (МИО)', validators=[Optional()])
    other_org_flag = BooleanField('Другие организации задействованы', default=False)
    other_org_people_count = IntegerField('Количество людей (другие орг.)', validators=[Optional()])
    other_org_technic_count = IntegerField('Количество техники (другие орг.)', validators=[Optional()])
    other_org_aircraft_count = IntegerField('Количество авиации (другие орг.)', validators=[Optional()])
    description = TextAreaField('Описание', validators=[Optional()])
    damage_tenge = IntegerField('Ущерб в тенге', validators=[Optional()])
    firefighting_costs = IntegerField('Затраты на тушение', validators=[Optional()])
    kpo = IntegerField('КПО', validators=[Optional()])
    file = FileField('Прикрепить файл', validators=[Optional()])
    edited_by_engineer = BooleanField('Отредактировано инженером', default=False)

    def __init__(self, regions_and_locations=None, *args, **kwargs):
        """Инициализация формы с опциональным словарем регионов и локаций."""
        super(FireForm, self).__init__(*args, **kwargs)
        if regions_and_locations:
            self.region.choices = [('', 'Выберите регион')] + [(r, r) for r in regions_and_locations.keys()]

    def validate(self, extra_validators=None):
        """Кастомная валидация формы с проверкой зависимостей."""
        if not super().validate(extra_validators):
            return False

        # Список групп флагов и связанных полей
        flag_groups = [
            ('lo_flag', ['lo_people_count', 'lo_technic_count']),
            ('aps_flag', ['aps_people_count', 'aps_technic_count', 'aps_aircraft_count']),
            ('kps_flag', ['kps_people_count', 'kps_technic_count', 'kps_aircraft_count']),
            ('mio_flag', ['mio_people_count', 'mio_technic_count', 'mio_aircraft_count']),
            ('other_org_flag', ['other_org_people_count', 'other_org_technic_count', 'other_org_aircraft_count']),
        ]

        # Проверка каждой группы
        for flag_name, related_fields in flag_groups:
            flag_value = getattr(self, flag_name).data
            if flag_value:  # Если флаг установлен
                related_values = [getattr(self, field).data for field in related_fields]
                if all(val is None or val == 0 for val in related_values):
                    self.errors[flag_name] = [
                        f"Если '{getattr(self, flag_name).label.text}' отмечено, укажите хотя бы одно из: "
                        f"{', '.join(getattr(self, f).label.text for f in related_fields)}."
                    ]
                    return False
        return True