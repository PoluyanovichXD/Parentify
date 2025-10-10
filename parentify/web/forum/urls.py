from django.urls import re_path, include
from parentify.web.forum.views import home
urlpatterns = [
    re_path(r'^$', home, name='home'),
]