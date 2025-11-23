from django.urls import re_path, include
from parentify.web.childs.views import child_development, childs
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', childs.all, name='childs'),
    re_path(r'^0/new/$', childs.create, name='create_childs'),
    re_path(r'^(\d+)/edit/$', childs.edit, name='edit_childs'),
    re_path(r'^(\d+)/$', childs.view, name='view_childs'),
    # Календарь развития - общий и для конкретного ребенка
    re_path(r'^development/$', child_development.calendar, name='child_development_general'),
    re_path(r'^(\d+)/development/$', child_development.calendar, name='child_development'),
    
    # Админка для управления календарем (только для админов)
    re_path(r'^development/calendar/$', child_development.calendar_list, name='development_calendar_list'),
    re_path(r'^development/calendar/0/new/$', child_development.calendar_create, name='create_development_calendar'),
    re_path(r'^development/calendar/(\d+)/edit/$', child_development.calendar_edit, name='edit_development_calendar'),
]