from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import ChildDevelopmentCalendar, UserChild, User
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *
from datetime import datetime


class FormChild(FormBase):
    first_name = TextInputField(label=_("Имя"), required=True, max_length=255)
    last_name = TextInputField(label=_("Фамилия"), required=True, max_length=255)
    birth_date = DateInputField(label=_("Дата рождения"), required=True)
    gender = SelectInputField(label=_("Пол"), required=False)

    def __init__(self, request, child_id=None):
        if child_id:
            self.child_id = child_id
            self.child = request.orm_session.query(UserChild).get(self.child_id)
            super().__init__(request, self.child.to_dict())
        else:
            self.child = UserChild()
            super().__init__(request)
        if request.current_user and request.current_user.is_admin:
            self.fields['user_id'] = SelectInputField(label=_("Пользователь"), required=True)
            self.fields['user_id'].choices = choise_name_orm(request, User, True, User.last_name)
        
        self.fields['gender'].choices = [
            ('', _('Не указан')),
            ('MALE', _('Мужской')),
            ('FEMALE', _('Женский'))
        ]

    def clean(self):
        super(FormChild, self).clean()
        
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            if birth_date > datetime.now():
                ValidationError(_('Дата рождения не может быть в будущем'))
        
        return self.cleaned_data

    def cmd_model_create(self, request):
        self.child.first_name = self.cleaned_data.get('first_name')
        self.child.last_name = self.cleaned_data.get('last_name')
        self.child.birth_date = self.cleaned_data.get('birth_date')
        self.child.gender = self.cleaned_data.get('gender')
        self.child.is_active = self.cleaned_data.get('is_active', True)
        self.child.user_id = self.cleaned_data.get('user_id', request.current_user.id)
        
        self.request.orm_session.add(self.child)
        self.request.orm_session.commit()
        
        return request.GET.get('url') if 'url' in request.GET else '../../'
        # return '/childs'

    def cmd_model_update(self, request):
        self.child.first_name = self.cleaned_data.get('first_name')
        self.child.last_name = self.cleaned_data.get('last_name')
        self.child.birth_date = self.cleaned_data.get('birth_date')
        self.child.gender = self.cleaned_data.get('gender')
        self.child.is_active = self.cleaned_data.get('is_active', True)
        self.child.updated_at = datetime.now()
        
        self.request.orm_session.commit()
        
        return request.GET.get('url') if 'url' in request.GET else '../../'
        # return f'/childs/{self.child_id}'


class FormFilterChild(FormModelFilter):
    first_name = TextInputField(label=_('Имя'), max_length=255, required=False)
    last_name = TextInputField(label=_('Фамилия'), max_length=255, required=False)
    gender = SelectInputField(label=_("Пол"), required=False)

    def __init__(self, request):
        super().__init__(request, 'child_filter')
        
        # Устанавливаем choices для поля gender
        self.fields['gender'].choices = [
            ('', _('Все')),
            ('MALE', _('Мужской')),
            ('FEMALE', _('Женский'))
        ]

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('first_name'):
                data_query = data_query.filter(
                    UserChild.first_name.ilike("%" + self.cleaned_data['first_name'] + "%")
                )
            if self.cleaned_data.get('last_name'):
                data_query = data_query.filter(
                    UserChild.last_name.ilike("%" + self.cleaned_data['last_name'] + "%")
                )
            if self.cleaned_data.get('gender'):
                data_query = data_query.filter(
                    UserChild.gender == self.cleaned_data.get('gender')
                )
        
        return data_query
    
# forms.py
class FormDevelopmentCalendar(FormBase):
    week_number = NumberInputField(label=_("Номер недели"), required=True, min_value=1, max_value=260)
    title = TextInputField(label=_("Заголовок совета"), required=True, max_length=500)
    description = TextAreaInputField(label=_("Описание совета"), required=True)
    category = SelectInputField(label=_("Категория"), required=False)
    is_active = SwitchField(label=_("Активный"), required=False, default=True)

    def __init__(self, request, calendar_id=None):
        if calendar_id:
            self.calendar_id = calendar_id
            self.calendar = request.orm_session.query(ChildDevelopmentCalendar).get(self.calendar_id)
            super().__init__(request, self.calendar.to_dict())
        else:
            self.calendar = ChildDevelopmentCalendar()
            super().__init__(request)
        
        self.fields['category'].choices = [
            ('', _('Общее')),
            ('PHYSICAL', _('Физическое развитие')),
            ('MENTAL', _('Умственное развитие')),
            ('SOCIAL', _('Социальное развитие')),
            ('EMOTIONAL', _('Эмоциональное развитие')),
            ('HEALTH', _('Здоровье и уход')),
            ('NUTRITION', _('Питание'))
        ]

    def clean(self):
        super(FormDevelopmentCalendar, self).clean()
        
        week_number = self.cleaned_data.get('week_number')
        if week_number and week_number > 260:
            self.add_error('week_number', _('Номер недели не может превышать 260 (5 лет)'))
        
        return self.cleaned_data

    def cmd_model_create(self, request):
        self.calendar.week_number = self.cleaned_data.get('week_number')
        self.calendar.title = self.cleaned_data.get('title')
        self.calendar.description = self.cleaned_data.get('description')
        self.calendar.category = self.cleaned_data.get('category')
        self.calendar.is_active = self.cleaned_data.get('is_active', True)
        
        self.request.orm_session.add(self.calendar)
        self.request.orm_session.commit()
        
        return '/childs/development/calendar'

    def cmd_model_update(self, request):
        self.calendar.week_number = self.cleaned_data.get('week_number')
        self.calendar.title = self.cleaned_data.get('title')
        self.calendar.description = self.cleaned_data.get('description')
        self.calendar.category = self.cleaned_data.get('category')
        self.calendar.is_active = self.cleaned_data.get('is_active', True)
        self.calendar.updated_at = datetime.now()
        
        self.request.orm_session.commit()
        
        return f'/childs/development/calendar/{self.calendar_id}'


class FormFilterDevelopmentCalendar(FormModelFilter):
    week_number = NumberInputField(label=_('Номер недели'), required=False)
    category = SelectInputField(label=_("Категория"), required=False)
    title = TextInputField(label=_('Заголовок'), max_length=500, required=False)

    def __init__(self, request):
        super().__init__(request, 'calendar_filter')
        
        self.fields['category'].choices = [
            ('', _('Все категории')),
            ('PHYSICAL', _('Физическое развитие')),
            ('MENTAL', _('Умственное развитие')),
            ('SOCIAL', _('Социальное развитие')),
            ('EMOTIONAL', _('Эмоциональное развитие')),
            ('HEALTH', _('Здоровье и уход')),
            ('NUTRITION', _('Питание'))
        ]

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('week_number'):
                data_query = data_query.filter(
                    ChildDevelopmentCalendar.week_number == self.cleaned_data['week_number']
                )
            if self.cleaned_data.get('category'):
                data_query = data_query.filter(
                    ChildDevelopmentCalendar.category == self.cleaned_data.get('category')
                )
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(
                    ChildDevelopmentCalendar.title.ilike("%" + self.cleaned_data['title'] + "%")
                )
        
        return data_query