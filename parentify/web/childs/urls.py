from django.urls import re_path, include
from parentify.web.childs.views import childs
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', childs.all, name='childs'),
    re_path(r'^0/new/$', childs.create, name='create_childs'),
    re_path(r'^(\d+)/edit/$', childs.edit, name='edit_childs'),
    re_path(r'^(\d+)/$', childs.view, name='view_childs'),
]