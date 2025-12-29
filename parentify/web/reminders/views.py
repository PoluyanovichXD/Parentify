from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from parentify.models.models import Reminder
from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, page_has_user, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.reminders.forms import FormFilterReminder, FormReminder
from parentify.web.reminders.pages import PageReminderEditor

class reminders:
    @common_page()
    @with_form('form_filter', FormFilterReminder, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        query = request.orm_session.query(Reminder).filter(Reminder.user_id==request.current_user.id)
        # if request.path.startswith('/profile'):
        #     query = query.filter(Goods.favorites.any(UserFavorite.user_id == request.current_user.id))
        modelInfo = PageModelInfo(request.session, '/reminder/', query, Reminder.id)
        return PageReminderEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @common_page()
    @with_form('form_model', FormReminder, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/reminder/', request.orm_session.query(Reminder), Reminder.id)
        page = PageReminderEditor(modelInfo).new(request, ControlInputs(form_model, classname='grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormReminder, 'cmd_model_update')
    def edit(request, model_id, form_model):
        modelInfo = PageModelInfo(request.session, '/reminder/', request.orm_session.query(Reminder), Reminder.id)
        page = PageReminderEditor(modelInfo)
        return page.edit(request, model_id, ControlInputs(form_model, classname='grid-cols-1'))

    @common_page()
    def view(request, model_id):
        modelInfo = PageModelInfo(request.session, '/reminder/', request.orm_session.query(Reminder), Reminder.id)
        page = PageReminderEditor(modelInfo)
        return page.view(request, model_id)