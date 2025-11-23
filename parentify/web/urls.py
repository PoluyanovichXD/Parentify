from django.urls import re_path, include
from parentify.web.views import home, login, register, logout, profile, settings
from django.views.generic.base import RedirectView

urlpatterns = [
    re_path(r'^$', home, name='home'),
    re_path(r'^admin/', include('parentify.web.admin.urls')),
    re_path(r'^article/', include('parentify.web.article.urls')),
    re_path(r'^forum/', include('parentify.web.forum.urls')),
    re_path(r'^map/', include('parentify.web.map.urls')),
    re_path(r'^childs/', include('parentify.web.childs.urls')),
    re_path(r'^goods/', include('parentify.web.goods.urls')),
    re_path(r'^login/$', login, name='login'),
    re_path(r'^register/$', register, name='register'),
    re_path(r'^logout/$', logout, name='logout'),
    re_path(r'^settings/$', settings, name='settings'),

    re_path(r'^profile/$', profile, name='profile'),
    re_path(r'^profile/childs/', include('parentify.web.childs.urls')),
    re_path(r'^profile/favorites/', include('parentify.web.goods.urls')),
    # re_path(r'^profile/childs/0/new/$', RedirectView.as_view(pattern_name='create_childs', permanent=False), name='profile_create_childs'),
    # re_path(r'^profile/childs/(\d+)/edit/$', RedirectView.as_view(pattern_name='edit_childs', permanent=False), name='profile_edit_childs'),
    # re_path(r'^profile/childs/(\d+)/$', RedirectView.as_view(pattern_name='view_childs', permanent=False), name='profile_view_childs'),

]
