from django.urls import re_path, include
from parentify.web.article.views import categories, articles
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', articles.all, name='all_article'),
    re_path(r'^0/new/$', articles.create, name='create_article'),
    re_path(r'^(\d+)/edit/$', articles.edit, name='edit_article'),
    re_path(r'^(\d+)/$', articles.view, name='view_article'),
    re_path(r'^preview/image_(\d+).png$', articles.preview, name='preview_article'),

    re_path(r'^categories/$', categories.all, name='all_categories_article'),
    re_path(r'^categories/0/new/$', categories.create, name='create_category_article'),
    re_path(r'^categories/(\d+)/edit/$', categories.edit, name='edit_category_article'),
    re_path(r'^categories/(\d+)/$', RedirectView.as_view(pattern_name='edit_category_article', permanent=True), name='view_category_article'),
    
]