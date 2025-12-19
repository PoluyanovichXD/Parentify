from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import ChildDevelopmentWeek
from parentify.ui.forms import FormBase, FormModelFilter
from parentify.ui.fields import *
from datetime import datetime

class FormDevelopmentCalendar(FormBase):
    week_number = NumberInputField(label=_("Номер недели"), required=True, min_value=1, max_value=260)
    title = TextInputField(label=_("Заголовок"), required=True, max_length=255)
    parent_tips = TextAreaInputField(label=_("Советы родителям"), required=False, multiply=True)
    key_skills = TextAreaInputField(label=_("Ключевые навыки"), required=False, multiply=True)
    description = TextAreaInputField(label=_("Текст"), required=False)

    def __init__(self, request, week_id=None):
        if week_id:
            self.week_id = week_id
            self.week = request.orm_session.query(ChildDevelopmentWeek).get(self.week_id)
            super().__init__(request, self.week.to_dict())
        else:
            self.week = ChildDevelopmentWeek()
            super().__init__(request)

    def clean(self):
        super(FormDevelopmentCalendar, self).clean()
        
        week_number = self.cleaned_data.get('week_number')
        if week_number:
            # Проверяем уникальность номера недели при создании
            if not hasattr(self, 'week_id') or (hasattr(self, 'week_id') and self.week.week_number != week_number):
                existing = self.request.orm_session.query(ChildDevelopmentWeek).filter(
                    ChildDevelopmentWeek.week_number == week_number
                ).first()
                if existing:
                    raise ValidationError(_('Неделя с таким номером уже существует'))
        
        return self.cleaned_data


    def cmd_model_create(self, request):
        self.week.week_number = self.cleaned_data.get('week_number')
        self.week.title = self.cleaned_data.get('title')
        self.week.description = self.cleaned_data.get('description')
        self.week.parent_tips = self.cleaned_data.get('parent_tips')
        self.week.key_skills = self.cleaned_data.get('key_skills')
        
        self.request.orm_session.add(self.week)
        self.request.orm_session.commit()
        
        return request.GET.get('url') if 'url' in request.GET else '../../'

    def cmd_model_update(self, request):
        self.week.week_number = self.cleaned_data.get('week_number')
        self.week.title = self.cleaned_data.get('title')
        self.week.description = self.cleaned_data.get('description')
        self.week.parent_tips = self.cleaned_data.get('parent_tips')
        self.week.key_skills = self.cleaned_data.get('key_skills')
        self.week.updated_at = datetime.now()
        
        self.request.orm_session.commit()
        
        return request.GET.get('url') if 'url' in request.GET else '../../'

class FormFilterDevelopmentCalendar(FormModelFilter):
    week_number = NumberInputField(label=_("Номер недели"), required=False)
    title = TextInputField(label=_("Заголовок"), required=False)


    def __init__(self, request):
        super().__init__(request, 'calendar_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(ChildDevelopmentWeek.name.ilike("%" + self.cleaned_data['title'] + "%"))
            if self.cleaned_data.get('week_number'):
                data_query = data_query.filter(ChildDevelopmentWeek.week_number <= self.cleaned_data.get('week_number'))
        return data_query