from django.contrib import admin
from django.urls import re_path, include
from web.views import home, login, register
urlpatterns = [
    re_path(r'^admin/$', include('web.admin.urls')),
    re_path(r'^article/$', include('web.article.urls')),
    re_path(r'^forum/$', include('web.forum.urls')),
   # re_path(r'^', home, name='home'),
   re_path(r'^login/$', login, name='login'),
   re_path(r'^register/$', register, name='register'),
]
