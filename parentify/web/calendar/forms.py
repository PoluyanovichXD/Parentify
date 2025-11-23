from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import ChildDevelopmentWeek
from parentify.ui.forms import FormBase, FormModelFilter
from parentify.ui.fields import *
from datetime import datetime

class FormDevelopmentCalendar(FormBase):
    week_number = IntegerInputField(label=_("Номер недели"), required=True, min_value=1, max_value=260)
    title = TextInputField(label=_("Заголовок"), required=True, max_length=255)
    description = TextAreaField(label=_("Текст"), required=False)
    parent_tips = TextAreaField(label=_("Советы родителям"), required=False, 
                               help_text=_("Каждый совет с новой строки"))
    key_skills = TextAreaField(label=_("Ключевые навыки"), required=False,
                              help_text=_("Каждый навык с новой строки"))

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

    def _process_array_field(self, field_name):
        """Обрабатывает текстовые поля в массивы"""
        value = self.cleaned_data.get(field_name, '')
        if value:
            # Разделяем по переносам строк, убираем пустые элементы
            items = [item.strip() for item in value.split('\n') if item.strip()]
            return items
        return []

    def cmd_model_create(self, request):
        self.week.week_number = self.cleaned_data.get('week_number')
        self.week.title = self.cleaned_data.get('title')
        self.week.description = self.cleaned_data.get('description')
        self.week.parent_tips = self._process_array_field('parent_tips')
        self.week.key_skills = self._process_array_field('key_skills')
        
        self.request.orm_session.add(self.week)
        self.request.orm_session.commit()
        
        return request.GET.get('url') if 'url' in request.GET else '../../'

    def cmd_model_update(self, request):
        self.week.week_number = self.cleaned_data.get('week_number')
        self.week.title = self.cleaned_data.get('title')
        self.week.description = self.cleaned_data.get('description')
        self.week.parent_tips = self._process_array_field('parent_tips')
        self.week.key_skills = self._process_array_field('key_skills')
        self.week.updated_at = datetime.now()
        
        self.request.orm_session.commit()
        
        return request.GET.get('url') if 'url' in request.GET else '../../'

class FormFilterDevelopmentCalendar(FormModelFilter):
    week_number = IntegerInputField(label=_("Номер недели"), required=False)
    title = TextInputField(label=_("Заголовок"), required=False)