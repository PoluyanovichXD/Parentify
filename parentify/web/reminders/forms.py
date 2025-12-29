from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import Reminder, UserChild
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *
import datetime


class FormReminder(FormBase):
    scheduled_datetime = DateTimeInputField(label=_("Дата и время"),required=True)
    children_id = SelectInputField(_label=("Ребёнок(необязательно)"), required=False)
    name = TextAreaInputField(label=_("Название"),required=True)
    message = TextAreaInputField(label=_("Комментарий"),required=True)
    
    def __init__(self, request, reminder_id=None):
        if reminder_id:
            self.reminder_id = reminder_id
            self.reminder = request.orm_session.query(Reminder).get(self.reminder_id)
            data = self.reminder.to_dict()
            super().__init__(request, data)
        else:
            self.reminder = Reminder()
            super().__init__(request)
        self.fields['children_id'].choices = [(None, None,)] + [(item.id,item.full_name) for item in request.orm_session.query(UserChild).filter(UserChild.user_id==request.current_user.id)]

    def clean(self):
        super(FormReminder, self).clean()

    def cmd_model_create(self, request):
        self.reminder.message = self.cleaned_data.get('message')
        self.reminder.name = self.cleaned_data.get('name')
        
        scheduled_datetime = self.cleaned_data.get('scheduled_datetime')
        
        self.reminder.scheduled_datetime = scheduled_datetime - timedelta(hours=24)
        
        self.reminder.children_id = self.cleaned_data.get('children_id')
        self.reminder.user_id = request.current_user.id
        
        request.orm_session.add(self.reminder)
        request.orm_session.commit()
        return '../../'

    def cmd_model_update(self, request):
        self.reminder.message = self.cleaned_data.get('message')
        self.reminder.name = self.cleaned_data.get('name')
        self.reminder.scheduled_datetime = self.cleaned_data.get('scheduled_datetime')
        self.reminder.user_id = request.current_user.id
        self.reminder.children_id = self.cleaned_data.get('children_id')
        
        request.orm_session.commit()
        return f'../../'


class FormFilterReminder(FormModelFilter):
    name = TextInputField(label=_('Название'), required=False)
    message = TextInputField(label=_('Комментарий'), required=False)

    def __init__(self, request, *args):
        super().__init__(request, 'reminder_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('message'):
                data_query = data_query.filter(Reminder.message.ilike("%" + self.cleaned_data['message'] + "%"))
            if self.cleaned_data.get('name'):
                data_query = data_query.filter(Reminder.name.ilike("%" + self.cleaned_data['name'] + "%"))
            
        return data_query