from django.urls import re_path, include
from parentify.web.map.views import home
urlpatterns = [
    re_path(r'^$', home, name='home'),
]