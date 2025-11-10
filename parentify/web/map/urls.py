from django.urls import re_path, include
from parentify.web.map.views import home, place, categories
from django.views.generic.base import RedirectView

urlpatterns = [
    # re_path(r'^$', home, name='home'),
    re_path(r'^$', place.all, name='map'),
    re_path(r'^0/new/$', place.create, name='create_map'),
    re_path(r'^(\d+)/edit/$', place.edit, name='edit_map'),
    re_path(r'^(\d+)/$', place.view, name='view_map'),
    re_path(r'^(\d+)/image.png$', place.image_url, name='image_map'),

    re_path(r'^categories/$', categories.all, name='all_categories_map'),
    re_path(r'^categories/0/new/$', categories.create, name='create_category_map'),
    re_path(r'^categories/(\d+)/edit/$', categories.edit, name='edit_category_map'),
    re_path(r'^categories/(\d+)/$', RedirectView.as_view(pattern_name='edit_category_map', permanent=True), name='view_category_map'),
]