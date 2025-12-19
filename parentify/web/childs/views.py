from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import UserChild
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import page_has_user, with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.childs.forms import FormChild, FormFilterChild
from parentify.settings           import PROJECT_ROOT
from parentify.web.childs.pages import PageChildEditor


class childs:

    @page_has_user()
    @common_page()
    @with_form('form_filter', FormFilterChild, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        query = request.orm_session.query(UserChild)
        if request.current_user and not request.current_user.is_admin:
            query = query.filter(UserChild.user_id==request.current_user.id)
        modelInfo = PageModelInfo(request.session, '/childs/', query, UserChild.id)
        return PageChildEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @page_has_user()
    @common_page()
    @with_form('form_model', FormChild, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/childs/', request.orm_session.query(UserChild), UserChild.id)
        page = PageChildEditor(modelInfo).new(request, ControlInputs(form_model))
        return page 

    @page_has_user()
    @common_page()
    @with_form('form_model', FormChild, 'cmd_model_update')
    def edit(request, model_id, form_model):
        query = request.orm_session.query(UserChild)
        if request.current_user and not request.current_user.is_admin:
            query = query.filter(UserChild.user_id==request.current_user.id)
        modelInfo = PageModelInfo(request.session, '/childs/', query, UserChild.id)
        page = PageChildEditor(modelInfo)
        return page.edit(request, model_id, ControlInputs(form_model))

    @page_has_user()
    @common_page()
    def view(request, model_id):
        query = request.orm_session.query(UserChild)
        if request.current_user and not request.current_user.is_admin:
            query = query.filter(UserChild.user_id==request.current_user.id)
        modelInfo = PageModelInfo(request.session, '/childs/', query, UserChild.id)
        page = PageChildEditor(modelInfo)
        return page.view(request, model_id)
    