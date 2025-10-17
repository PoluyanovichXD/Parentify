from django.urls import re_path, include
from parentify.web.forum.views import all, create, edit, view, preview
urlpatterns = [
    re_path(r'^$', all, name='home'),
    re_path(r'^0/new/$', create, name='create_forum'),
    re_path(r'^(\d+)/edit/$', edit, name='edit_forum'),
    re_path(r'^(\d+)/$', view, name='view_forum'),
    re_path(r'^preview/image_(\d+).png$', preview, name='preview_forum'),
    
]