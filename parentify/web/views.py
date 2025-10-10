from django.http                    import HttpResponseRedirect
from django.shortcuts               import render
from parentify.models.models        import GenderEnum, User
from django.contrib.auth.hashers    import *


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
            GenderEnum.MALE if post.get('gender')=='male' else GenderEnum.FEMALE,
        )
        request.session['token'] = make_password(password, salt=User.get_salt(user.email))
        return HttpResponseRedirect('/')
    return render(request, 'pages/register.html')


def logout(request):
    request.session.delete()
    return HttpResponseRedirect('/')

def profile(request):
    return render(request, 'pages/profile.html')