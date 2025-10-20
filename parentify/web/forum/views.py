from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import ForumTopic
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.forum.forms import FormForum, FormFilterForum, FormForumComment
from parentify.settings           import PROJECT_ROOT
from parentify.web.forum.pages import PageForumEditor



@common_page()
@with_form('form_filter', FormFilterForum, 'cmd_filter', 'cmd_discard', 'cmd_store')
@with_get_int('p', 0, 255)
def all(request, p, form_filter):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    return PageForumEditor(modelInfo).items(request, p, form_filter)

@common_page()
@with_form('form_forum', FormForum, 'cmd_model_create')
def create(request, form_forum):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    page = PageForumEditor(modelInfo).new(request, ControlInputs(form_forum, classname='[&]:md:grid-cols-1'))
    return page 

@common_page()
@with_form('form_forum', FormForum, 'cmd_model_update')
def edit(request, forum_id, form_forum):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    page = PageForumEditor(modelInfo)
    return page.edit(request,forum_id, ControlInputs(form_forum))

@common_page()
@with_form('form_forum_comment', FormForumComment, 'cmd_model_create')
def view(request, forum_id, form_forum_comment):
    modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
    page = PageForumEditor(modelInfo)
    # page.add_control('form_forum_comment', ControlInputs(form_forum_comment))
    return page.view(request,forum_id)
