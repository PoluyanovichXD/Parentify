from django.http import Http404, HttpResponse
from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.models.models import Article, ArticleCategory
from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import with_form, common_page, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.article.forms import FormArticle, FormCategory, FormFilterArticle, FormFilterCategory
from parentify.settings           import PROJECT_ROOT
from parentify.web.article.pages import PageArticleEditor, PageCategoryEditor


class articles:
    @common_page()
    @with_form('form_filter', FormFilterArticle, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/article/', request.orm_session.query(Article), Article.id)
        return PageArticleEditor(modelInfo).items(request, p, form_filter)

    @common_page()
    @with_form('form_article', FormArticle, 'cmd_model_create')
    def create(request, form_article):
        modelInfo = PageModelInfo(request.session, '/article/', request.orm_session.query(Article), Article.id)
        page = PageArticleEditor(modelInfo).new(request, ControlInputs(form_article, classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_article', FormArticle, 'cmd_model_update')
    def edit(request, article_id, form_article):
        modelInfo = PageModelInfo(request.session, '/article/', request.orm_session.query(Article), Article.id)
        page = PageArticleEditor(modelInfo)
        return page.edit(request,article_id, ControlInputs(form_article))

    @common_page()
    def view(request, article_id):
        modelInfo = PageModelInfo(request.session, '/article/', request.orm_session.query(Article), Article.id)
        page = PageArticleEditor(modelInfo)
        return page.view(request,article_id)

    @common_page()
    def preview(request, article_id):
        try:
            return HttpResponse(request.orm_session.query(Article).get(article_id).image,
                                content_type='image/*')
        except Exception as ex:
            print(ex)
            raise Http404()
    
class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/article/categories/', request.orm_session.query(ArticleCategory), ArticleCategory.id)
        return PageCategoryEditor(modelInfo).items(request, p, form_filter, PageCategoryEditor.toolbar, no_zip=False)

    @common_page()
    @with_form('form_category', FormCategory, 'cmd_model_create')
    def create(request, form_category):
        modelInfo = PageModelInfo(request.session, '/article/categories/', request.orm_session.query(ArticleCategory), ArticleCategory.id)
        page = PageCategoryEditor(modelInfo).new(request, ControlInputs(form_category, classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_category', FormCategory, 'cmd_model_update')
    def edit(request, article_id, form_category):
        modelInfo = PageModelInfo(request.session, '/article/categories/', request.orm_session.query(ArticleCategory), ArticleCategory.id)
        page = PageCategoryEditor(modelInfo)
        return page.edit(request,article_id, ControlInputs(form_category))