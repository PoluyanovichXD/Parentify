from django.urls import re_path, include
from parentify.web.article.views import home, create, edit, view
urlpatterns = [
    re_path(r'^$', home, name='home'),
    re_path(r'^create/', create, name='create_article'),
    re_path(r'^edit/', edit, name='edit_article'),
    re_path(r'^view/', view, name='view_article'),
]