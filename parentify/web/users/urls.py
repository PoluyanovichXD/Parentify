from django.urls import re_path, include
from parentify.web.users.views import users
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^(\d+)/avatar.png$', users.avatar, name='user_avatar'),
]

