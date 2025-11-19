from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import UserChild, User
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
        
        return '/childs'

    def cmd_model_update(self, request):
        self.child.first_name = self.cleaned_data.get('first_name')
        self.child.last_name = self.cleaned_data.get('last_name')
        self.child.birth_date = self.cleaned_data.get('birth_date')
        self.child.gender = self.cleaned_data.get('gender')
        self.child.is_active = self.cleaned_data.get('is_active', True)
        self.child.updated_at = datetime.now()
        
        self.request.orm_session.commit()
        
        return f'/childs/{self.child_id}'


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