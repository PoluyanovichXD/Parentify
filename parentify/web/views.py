from django.http                    import HttpResponseRedirect
from django.shortcuts               import render
from parentify.models.models        import User
from django.contrib.auth.hashers    import *

from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, with_form
from parentify.ui.pages import PageSimple
from parentify.web.forms import FormPassword, FormProfile


def home(request):
    return render(request, 'pages/home.html')

def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    if email and password:
        user = request.orm_session.query(User).filter(User.email==email).first()
        if user and user.check_password(password):
            request.session['token'] = make_password(password, salt=User.get_salt(user.email))
            return HttpResponseRedirect('/')
    return render(request, 'pages/login.html')

def register(request):
    post = request.POST
    if post and post.get('password')==post.get('confirm_password'):
        User.create(request.orm_session,
            post.get('email'),
            post.get('first_name'),
            post.get('last_name'),
            post.get('password'),
            True,
            False,
            post.get('birth_date'),
            'male' if post.get('gender')=='male' else 'female',
        )
        request.session['token'] = make_password(password, salt=User.get_salt(user.email))
        return HttpResponseRedirect('/')
    return render(request, 'pages/register.html')


def logout(request):
    request.session.delete()
    return HttpResponseRedirect('/')

@common_page()
@with_form('form_profile', FormProfile, 'cmd_profile_edit')
@with_form('form_password', FormPassword, 'cmd_password_edit')
def profile(request, form_profile, form_password):
    page = PageSimple('Профиль пользователя', 'pages/profile.html')
    page.add_control('form_profile', ControlInputs(form_profile))
    page.add_control('form_password', ControlInputs(form_password))
    return page