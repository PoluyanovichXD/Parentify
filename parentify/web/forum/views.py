from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import ForumTopic, ForumComment, ForumTopicCategory
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.forum.forms import FormCategory, FormFilterCategory, FormForum, FormFilterForum, FormForumComment
from parentify.settings           import PROJECT_ROOT
from parentify.web.forum.pages import PageCategoryEditor, PageForumEditor


class forum:
    @common_page()
    @with_form('form_filter', FormFilterForum, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        
        modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic).order_by(ForumTopic.created_at.desc()), ForumTopic.id)
        return PageForumEditor(modelInfo).items(request, p, form_filter, type_list='list')

    @common_page()
    @with_form('form_forum', FormForum, 'cmd_model_create')
    def create(request, form_forum):
        modelInfo = PageModelInfo(request.session, '/forum/', request.orm_session.query(ForumTopic), ForumTopic.id)
        page = PageForumEditor(modelInfo).new(request, ControlInputs(form_forum))
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
        if request.GET.get('delete') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(ForumTopic).get(forum_id))
            request.orm_session.commit()
            return HttpResponseRedirect('../')
        if request.GET.get('delete_comment') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(ForumComment).get(request.GET.get('delete_comment')))
            request.orm_session.commit()
            return HttpResponseRedirect(f"/forum/{forum_id}")
        # page.add_control('form_forum_comment', ControlInputs(form_forum_comment))
        return page.view(request,forum_id)

class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/forum/categories/', request.orm_session.query(ForumTopicCategory).order_by(ForumTopicCategory.created_at.desc()), ForumTopicCategory.id)
        return PageCategoryEditor(modelInfo).items(request, p, form_filter, PageCategoryEditor.toolbar, no_zip=False)

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/forum/categories/', request.orm_session.query(ForumTopicCategory), ForumTopicCategory.id)
        page = PageCategoryEditor(modelInfo).new(request, ControlInputs(form_model, classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_update')
    def edit(request, model_id, form_model):
        modelInfo = PageModelInfo(request.session, '/forum/categories/', request.orm_session.query(ForumTopicCategory), ForumTopicCategory.id)
        page = PageCategoryEditor(modelInfo)
        return page.edit(request,model_id, ControlInputs(form_model))