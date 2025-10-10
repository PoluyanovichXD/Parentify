from django.urls import re_path, include
from parentify.web.views import home, login, register, logout, profile
urlpatterns = [
    re_path(r'^admin/$', include('parentify.web.admin.urls')),
    re_path(r'^article/$', include('parentify.web.article.urls')),
    re_path(r'^forum/$', include('parentify.web.forum.urls')),
    re_path(r'^map/$', include('parentify.web.map.urls')),
    re_path(r'^login/$', login, name='login'),
    re_path(r'^register/$', register, name='register'),
    re_path(r'^logout/$', logout, name='logout'),
    re_path(r'^profile/$', profile, name='profile'),
    re_path(r'^$', home, name='home'),
]
