from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import ChildDevelopmentCalendar, UserChild
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import page_has_user, with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.childs.forms import FormChild, FormDevelopmentCalendar, FormFilterChild, FormFilterDevelopmentCalendar
from parentify.settings           import PROJECT_ROOT
from parentify.web.childs.pages import PageChildEditor, PageDevelopmentCalendarEditor


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
    
# views.py
class child_development:

    @page_has_user()
    @common_page()
    def calendar(request, child_id=None):
        """Календарь развития - может отображаться как общий, так и для конкретного ребенка"""
        page = PageDevelopmentCalendarEditor()
        return page.render(request, child_id)

    @page_has_user()
    @common_page()
    @with_form('form_filter', FormFilterDevelopmentCalendar, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def calendar_list(request, p, form_filter):
        """Админка - список всех советов по развитию"""
        if not request.current_user or not request.current_user.is_admin:
            raise Http404("Page not found")
            
        query = request.orm_session.query(ChildDevelopmentCalendar)
        modelInfo = PageModelInfo(request.session, '/childs/development/calendar/', query, ChildDevelopmentCalendar.id)
        return PageDevelopmentCalendarEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @page_has_user()
    @common_page()
    @with_form('form_model', FormDevelopmentCalendar, 'cmd_model_create')
    def calendar_create(request, form_model):
        """Админка - создание нового совета"""
        if not request.current_user or not request.current_user.is_admin:
            raise Http404("Page not found")
            
        modelInfo = PageModelInfo(request.session, '/childs/development/calendar/', 
                                request.orm_session.query(ChildDevelopmentCalendar), 
                                ChildDevelopmentCalendar.id)
        page = PageDevelopmentCalendarEditor(modelInfo)
        return page.new(request, ControlInputs(form_model))

    @page_has_user()
    @common_page()
    @with_form('form_model', FormDevelopmentCalendar, 'cmd_model_update')
    def calendar_edit(request, model_id, form_model):
        """Админка - редактирование совета"""
        if not request.current_user or not request.current_user.is_admin:
            raise Http404("Page not found")
            
        modelInfo = PageModelInfo(request.session, '/childs/development/calendar/', 
                                request.orm_session.query(ChildDevelopmentCalendar), 
                                ChildDevelopmentCalendar.id)
        page = PageDevelopmentCalendarEditor(modelInfo)
        return page.edit(request, model_id, ControlInputs(form_model))