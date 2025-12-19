from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import Article, ArticleCategory, ChildDevelopmentWeek
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.calendar.forms import FormDevelopmentCalendar, FormFilterDevelopmentCalendar
from parentify.settings           import PROJECT_ROOT
from parentify.web.calendar.pages import PageDevelopmentCalendarEditor



class calendar:
    @common_page()
    @with_form('form_filter', FormFilterDevelopmentCalendar, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/calendar/', request.orm_session.query(ChildDevelopmentWeek), ChildDevelopmentWeek.id)
        return PageDevelopmentCalendarEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @common_page()
    @with_form('form_model', FormDevelopmentCalendar, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/calendar/', request.orm_session.query(ChildDevelopmentWeek), ChildDevelopmentWeek.id)
        page = PageDevelopmentCalendarEditor(modelInfo).new(request, ControlInputs(form_model, classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormDevelopmentCalendar, 'cmd_model_update')
    def edit(request, model_id, form_model):
        modelInfo = PageModelInfo(request.session, '/calendar/', request.orm_session.query(ChildDevelopmentWeek), ChildDevelopmentWeek.id)
        page = PageDevelopmentCalendarEditor(modelInfo)
        return page.edit(request, model_id, ControlInputs(form_model))

    @common_page()
    def view(request, model_id):
        modelInfo = PageModelInfo(request.session, '/calendar/', request.orm_session.query(ChildDevelopmentWeek), ChildDevelopmentWeek.id)
        page = PageDevelopmentCalendarEditor(modelInfo)
        return page.view(request, model_id)