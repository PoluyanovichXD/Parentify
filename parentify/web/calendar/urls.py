from django.urls import re_path, include
from parentify.web.calendar.views import calendar
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', calendar.all, name='all_calendar'),
    re_path(r'^0/new/$', calendar.create, name='create_calendar'),
    re_path(r'^(\d+)/edit/$', calendar.edit, name='edit_calendar'),
    re_path(r'^(\d+)/$', calendar.view, name='view_calendar'),
]