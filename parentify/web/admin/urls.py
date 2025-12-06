from django.urls import re_path, include
from django.views.generic.base import RedirectView
from parentify.web.admin.views import admin


urlpatterns = [
    re_path(r'^$', admin.dashboard, name='dashboard'),
    re_path(r'^(\w+)/$', admin.model_list, name='list_model'),
    re_path(r'^(\w+)/0/new/$', admin.model_create, name='create_model'),
    re_path(r'^(\w+)/(\d+)/edit/$', admin.model_edit, name='edit_model'),
    re_path(r'^(\w+)/(\d+)/$', RedirectView.as_view(pattern_name='edit_model', permanent=True), name='view_model')
    # re_path(r'^/(\w+)/(\d+)/$', admin.model_view, name='view_model'),
]