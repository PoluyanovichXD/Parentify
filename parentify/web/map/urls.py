from django.urls import re_path, include
from parentify.web.map.views import home, place
urlpatterns = [
    # re_path(r'^$', home, name='home'),
    re_path(r'^$', place.all, name='map'),
    re_path(r'^0/new/$', place.create, name='create_map'),
    re_path(r'^(\d+)/edit/$', place.edit, name='edit_map'),
    re_path(r'^(\d+)/$', place.view, name='view_map'),
    re_path(r'^(\d+)/image.png$', place.image_url, name='image_map'),
]