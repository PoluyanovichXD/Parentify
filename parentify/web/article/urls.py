from django.urls import re_path, include
from parentify.web.article.views import all, create, edit, view, preview
urlpatterns = [
    re_path(r'^$', all, name='home'),
    re_path(r'^0/new/$', create, name='create_article'),
    re_path(r'^(\d+)/edit/$', edit, name='edit_article'),
    re_path(r'^(\d+)/$', view, name='view_article'),
    re_path(r'^preview/image_(\d+).png$', preview, name='preview_article'),
    
]