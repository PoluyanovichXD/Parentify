from django.urls import re_path, include
from parentify.web.trecker.views import trecker, categories
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', trecker.all, name='trecker'),
    re_path(r'^0/new/$', trecker.create, name='create_trecker'),
    re_path(r'^(\d+)/edit/$', trecker.edit, name='edit_trecker'),
    re_path(r'^(\d+)/$', trecker.view, name='view_trecker'),

    re_path(r'^categories/$', categories.all, name='all_categories_trecker'),
    re_path(r'^categories/0/new/$', categories.create, name='create_category_trecker'),
    re_path(r'^categories/(\d+)/edit/$', categories.edit, name='edit_category_trecker'),
    re_path(r'^categories/(\d+)/$', RedirectView.as_view(pattern_name='edit_category_trecker', permanent=True), name='view_category_trecker'),
]