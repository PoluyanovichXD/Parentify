from django.urls import re_path, include
from parentify.web.reminders.views import reminders
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', reminders.all, name='reminder'),
    re_path(r'^0/new/$', reminders.create, name='create_reminder'),
    re_path(r'^(\d+)/edit/$', reminders.edit, name='edit_reminder'),
    re_path(r'^(\d+)/$', reminders.view, name='view_reminder'),
]