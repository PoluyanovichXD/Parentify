from django.http                    import HttpResponseRedirect
from django.shortcuts               import render
from parentify.models.models        import User
from django.contrib.auth.hashers    import *


def home(request):
    return render(request, 'pages/home.html')

def login(request):
    email = request.POST.get('email')
    password = request.POST.get('password')
    if email and password:
        user = request.orm_session.query(User).filter(User.email==email).first()
        print(request.orm_session.query(User).first().password, make_password(password, salt=User.get_salt(email)))
        if user and user.check_password(password):
            request.session['token'] = make_password(password, salt=User.get_salt(user.email))
            return HttpResponseRedirect('/')
    return render(request, 'pages/login.html')

def register(request):
    return render(request, 'pages/register.html')


def logout(request):
    request.session.delete()
    return HttpResponseRedirect('/')

