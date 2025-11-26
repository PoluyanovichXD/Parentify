from datetime import date
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django.forms import Form
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
import re
from parentify.models.models import User
from parentify.ui import *
from parentify.ui.forms import FormBase
from django.contrib.auth.hashers    import *


class FormLogin(FormBase):
    email = TextInputField(label=_("Почта"), required=True)
    password = PasswordInputField(label=_("Пароль"), required=True)

    def __init__(self, request):
        super().__init__(request)

    def clean(self):
        super(FormLogin, self).clean()
        email = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')

        if email and password:
            user = self.request.orm_session.query(User).filter(User.password==User.create_password(password, email)).first()
            if not user:
                raise forms.ValidationError(
                    _('Неверный email или пароль')
                )
            self.user = user
            
    def cmd_login(self, request):
        request.session['token'] = make_password(self.cleaned_data['password'], salt=User.get_salt(self.cleaned_data['email']))
        return '/'



class FormRegister(FormBase):
    last_name = TextInputField(label=_("Фамилия"), required=True)
    first_name = TextInputField(label=_("Имя"), required=True)
    birth_date = DateInputField(label=_("Дата рождения"), required=True)
    gender = SelectInputField(
        label=_('Пол'),
        required=True
    )
    email = EmailInputField(
        label=_('Email'),
        required=True
    )
    
    password = PasswordInputField(
        label=_('Пароль'),
        required=True
    )
    
    confirm_password = PasswordInputField(
        label=_('Подтверждение пароля'),
        required=True
    )

    def __init__(self, request):
        super().__init__(request)
        self.fields['gender'].choices=[
            (None, _('Выберите пол')),
            ('male', _('Мужской')),
            ('female', _('Женский')),
        ]

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.request.orm_session.query(User).filter(User.email==email).first():
            raise ValidationError(_('Пользователь с таким email уже существует'))
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        if len(password) < 8:
            raise ValidationError(_('Пароль должен содержать минимум 8 символов'))
        
        if not re.search(r'\d', password):
            raise ValidationError(_('Пароль должен содержать хотя бы одну цифру'))
        
        if not re.search(r'[a-zA-Zа-яА-Я]', password):
            raise ValidationError(_('Пароль должен содержать хотя бы одну букву'))
        
        return password

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age > 120 or age < 0:
                raise ValidationError(_('Пожалуйста, укажите корректную дату рождения'))
        
        return birth_date

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError(_('Пароли не совпадают'))

    def cmd_register(self, request=None):
        del self.cleaned_data['confirm_password']
        user = User.create(
            self.request.orm_session,
            **self.cleaned_data
        )
        request.session['token'] = make_password(self.cleaned_data['password'], salt=User.get_salt(self.cleaned_data['email']))
        return '/'
    


class FormProfile(FormBase):
    last_name = TextInputField(label=_("Фамилия"))
    first_name = TextInputField(label=_("Имя"))
    birth_date = DateInputField(label=_("Дата рождения"))
    email = EmailInputField(label=_('Email'))
    gender = SelectInputField(label=_('Пол'))
    
    def __init__(self, request, user_id=None):
        if request.current_user:
            self.user = request.orm_session.query(User).get(request.current_user.id)
        else:
            self.user = None
        super().__init__(request, self.user.to_dict() if self.user else {})
        self.fields['gender'].choices=[
            (None, _('Выберите пол')),
            ('male', _('Мужской')),
            ('female', _('Женский')),
        ]

    def clean(self):
        pass


    def cmd_profile_edit(self, request):
        self.user.last_name = self.cleaned_data.get('last_name')
        self.user.first_name = self.cleaned_data.get('first_name')
        self.user.birth_date = self.cleaned_data.get('birth_date')
        self.user.gender = self.cleaned_data.get('gender')
        self.user.email = self.cleaned_data.get('email')
        request.orm_session.commit()
        return '/profile/'

    

class FormPassword(FormBase):
    current_password = PasswordInputField(label=_('Текущий пароль'))
    new_password = PasswordInputField(label=_('Новый пароль'))
    confirm_password = PasswordInputField(label=_('Подтвердите новый пароль'))
    def __init__(self, request, user_id=None):
        self.user = request.orm_session.query(User).get(request.current_user.id) if request.current_user else None
        super().__init__(request, {})
    def clean(self):
        if 'cmd_password_edit' in self.request.POST:
            if User.create_password(self.cleaned_data.get('current_password'), self.user.email) != self.user.password:
                raise ValidationError(_("Не верный пароль"))
            if self.cleaned_data.get('new_password') != self.cleaned_data.get('confirm_password'):
                raise ValidationError(_("Пароли не совпадают"))
            
    def cmd_password_edit(self, request):
        self.cleaned_data.get('current_password')
        self.cleaned_data.get('new_password')
        self.cleaned_data.get('confirm_password')
        request.session['token'] = make_password(self.cleaned_data['new_password'], salt=User.get_salt(self.user.email))
        return '/profile/'