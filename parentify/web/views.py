from django.http                    import HttpResponseRedirect
from django.shortcuts               import render
from parentify.models.models        import User
from django.contrib.auth.hashers    import *

from parentify.ui.controls import ControlInputs, ControlRecord, ControlRecordlist
from parentify.ui.decorators import common_page, page_has_user, with_form
from parentify.ui.pages import PageSimple
from parentify.web.forms import FormLogin, FormPassword, FormProfile, FormRegister


def home(request):
    return render(request, 'pages/home.html')

@common_page()
@with_form('form_login', FormLogin, 'cmd_login')
def login(request, form_login):
    page = PageSimple('Авторизация', 'pages/login.html')
    page.add_control('form_login', ControlInputs(form_login))
    return page

@common_page()
@with_form('form_register', FormRegister, 'cmd_register')
def register(request, form_register):
    page = PageSimple('Регистрация', 'pages/register.html')
    page.add_control('form_register', ControlInputs(form_register))
    return page


def logout(request):
    request.session.delete()
    return HttpResponseRedirect('/')

@page_has_user()
@common_page()
@with_form('form_profile', FormProfile, 'cmd_profile_edit')
@with_form('form_password', FormPassword, 'cmd_password_edit')
def profile(request, form_profile, form_password):
    if request.FILES.get('user_avatar'):
        user = request.orm_session.query(User).get(request.current_user.id)
        user.avatar = request.FILES.get('user_avatar').read()
        request.orm_session.commit()
        return HttpResponseRedirect('/profile/')
    page = PageSimple('Профиль пользователя', 'pages/profile.html')
    page.add_control('form_profile', ControlInputs(form_profile))
    page.add_control('form_password', ControlInputs(form_password))
    page.add_control('record', ControlRecord(request.orm_session.query(User).filter(User.id==request.current_user.id)))
    return page

@page_has_user()
@common_page()
def goods_favorites(request):
    page = PageSimple('Избранные товары', 'pages/favorites.html')
    page.add_control('record', ControlRecordlist(request.current_user.get_favorites(request.orm_session)))
    return page

@page_has_user()
@common_page()
def settings(request):
    page = PageSimple('Профиль пользователя', 'pages/settings.html')
    return page


@common_page()
def reference(request):
    page = PageSimple('Профиль пользователя', 'pages/reference.html')
    return page