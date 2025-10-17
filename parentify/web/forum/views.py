from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import ForumTopic
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.forum.forms import FormForum, FormFilterForum
from parentify.settings           import PROJECT_ROOT
from parentify.web.forum.pages import PageForumEditor



@common_page()
@with_form('form_filter', FormFilterForum, 'cmd_filter', 'cmd_discard', 'cmd_store')
@with_get_int('p', 0, 255)
def all(request, p, form_filter):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    return PageForumEditor(modelInfo).items(request, p, form_filter)

@common_page()
@with_form('form_article', FormForum, 'cmd_model_create')
def create(request, form_article):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    page = PageForumEditor(modelInfo).new(request, ControlInputs(form_article, classname='[&]:md:grid-cols-1'))
    return page 

@common_page()
@with_form('form_article', FormForum, 'cmd_model_update')
def edit(request, forum_id, form_article):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    page = PageForumEditor(modelInfo)
    return page.edit(request,forum_id, ControlInputs(form_article))

@common_page()
def view(request, forum_id):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    page = PageForumEditor(modelInfo)
    return page.view(request,forum_id)

@common_page()
def preview(request, forum_id):
    try:
        return HttpResponse(request.orm_session.query(ForumTopic).get(forum_id).image,
                            content_type='image/*')
    except Exception as ex:
        print(ex)
        raise Http404()