from datetime import date
from django import forms
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import authenticate
from django.utils.translation import gettext_lazy as _
from django import forms
from django.contrib.auth import authenticate, login
from django.core.exceptions import ValidationError
import re
from parentify.models.models import User
from parentify.ui import *

class FormLogin(forms.Form):
    email = TextInputField(label=_("Почта"))
    
    password = PasswordInputField(label=_("Пароль"))

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(
                self.request, 
                username=email, 
                password=password
            )
            if self.user_cache is None:
                raise forms.ValidationError(
                    _('Неверный email или пароль')
                )
            elif not self.user_cache.is_active:
                raise forms.ValidationError(
                    _('Аккаунт деактивирован')
                )

        return cleaned_data

    def get_user(self):
        return self.user_cache
    



class FormRegister(forms.Form):
    lastName = TextInputField(label=_("Фамилия"))
    
    firstName = TextInputField(label=_("Имя"))
    
    middleName = TextInputField(label=_("Отчество"))
    
    birth_date = DateInputField(label=_("Дата рождения"))
    
    GENDER_CHOICES = [
        ('', _('Выберите пол')),
        ('M', _('Мужской')),
        ('F', _('Женский')),
        ('O', _('Другой')),
    ]
    
    gender = forms.ChoiceField(
        label=_('Пол'),
        choices=GENDER_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    email = forms.EmailField(
        label=_('Email'),
        max_length=254,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': _('example@mail.com')
        })
    )
    
    password = forms.CharField(
        label=_('Пароль'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Придумайте надежный пароль')
        }),
        help_text=_('Минимум 8 символов, включая буквы и цифры')
    )
    
    confirmPassword = forms.CharField(
        label=_('Подтверждение пароля'),
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': _('Повторите пароль')
        })
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError(_('Пользователь с таким email уже существует'))
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        
        # Проверка минимальной длины
        if len(password) < 8:
            raise ValidationError(_('Пароль должен содержать минимум 8 символов'))
        
        # Проверка на наличие цифр
        if not re.search(r'\d', password):
            raise ValidationError(_('Пароль должен содержать хотя бы одну цифру'))
        
        # Проверка на наличие букв
        if not re.search(r'[a-zA-Zа-яА-Я]', password):
            raise ValidationError(_('Пароль должен содержать хотя бы одну букву'))
        
        return password

    def clean_birth_date(self):
        birth_date = self.cleaned_data.get('birth_date')
        if birth_date:
            # Проверка что пользователю至少 13 лет
            today = date.today()
            age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
            
            if age < 13:
                raise ValidationError(_('Вам должно быть至少 13 лет для регистрации'))
            
            if age > 120:
                raise ValidationError(_('Пожалуйста, укажите корректную дату рождения'))
        
        return birth_date

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirmPassword')
        
        if password and confirm_password and password != confirm_password:
            raise ValidationError(_('Пароли не совпадают'))
        
        return cleaned_data

    def save(self, request=None):
        # Создаем пользователя
        email = self.cleaned_data['email']
        password = self.cleaned_data['password']
        
        username = email.split('@')[0]
        base_username = username
        counter = 1
        while User.objects.filter(username=username).exists():
            username = f"{base_username}{counter}"
            counter += 1
        
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=self.cleaned_data['firstName'],
            last_name=self.cleaned_data['lastName']
        )
        
        profile = user.profile
        profile.middle_name = self.cleaned_data['middleName']
        profile.birth_date = self.cleaned_data['birth_date']
        profile.gender = self.cleaned_data['gender']
        profile.save()
        
        if request:
            user = authenticate(
                username=username,
                password=password
            )
            if user:
                login(request, user)
        
        return user
    
