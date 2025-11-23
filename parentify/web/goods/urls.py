from django.urls import re_path, include
from parentify.web.goods.views import goods, categories
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', goods.all, name='goods'),
    re_path(r'^0/new/$', goods.create, name='create_goods'),
    re_path(r'^(\d+)/edit/$', goods.edit, name='edit_goods'),
    re_path(r'^(\d+)/add_to_favorites/$', goods.add_to_favorites, name='add_to_favorites_goods'),
    re_path(r'^(\d+)/remove_from_favorites/$', goods.remove_from_favorites, name='remove_from_favorites_goods'),
    re_path(r'^(\d+)/$', goods.view, name='view_goods'),
    re_path(r'^preview/image_(\d+).png$', goods.preview, name='preview_goods'),
    
    re_path(r'^categories/$', categories.all, name='all_categories_goods'),
    re_path(r'^categories/0/new/$', categories.create, name='create_category_goods'),
    re_path(r'^categories/(\d+)/edit/$', categories.edit, name='edit_category_goods'),
    re_path(r'^categories/(\d+)/$', RedirectView.as_view(pattern_name='edit_category_goods', permanent=True), name='view_category_goods'),
]