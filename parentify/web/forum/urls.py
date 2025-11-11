from django.urls import re_path, include
from parentify.web.forum.views import forum, categories
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', forum.all, name='forum'),
    re_path(r'^0/new/$', forum.create, name='create_forum'),
    re_path(r'^(\d+)/edit/$', forum.edit, name='edit_forum'),
    re_path(r'^(\d+)/$', forum.view, name='view_forum'),
    
    re_path(r'^categories/$', categories.all, name='all_categories_article'),
    re_path(r'^categories/0/new/$', categories.create, name='create_category_article'),
    re_path(r'^categories/(\d+)/edit/$', categories.edit, name='edit_category_article'),
    re_path(r'^categories/(\d+)/$', RedirectView.as_view(pattern_name='edit_category_article', permanent=True), name='view_category_article'),
    
]