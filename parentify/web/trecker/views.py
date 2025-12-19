from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from parentify.models.models import Goods, GoodsCategory, UserFavorite, Trecker, TreckerCategory, UserChild
from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, page_has_user, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.trecker.forms import FormFilterTrecker, FormTrecker, FormFilterCategory, FormCategory
from parentify.web.trecker.pages import PageTreckerEditor, PageCategoryEditor

class trecker:
    @common_page()
    @with_form('form_filter', FormFilterTrecker, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, *args, **kwargs):
        p = kwargs.get('p')
        form_filter = kwargs.get('form_filter')
        query = request.orm_session.query(Trecker)
        
        if args:
            query = query.filter(Trecker.children_id==args[0])
        elif request.current_user or not request.current_user.is_admin:
             childrens = request.orm_session.query(UserChild).filter(UserChild.user_id==request.current_user.id)
             query = query.filter(Trecker.children_id.in_([item.id for item in childrens]))
        if request.GET.get('delete') and request.current_user:
            request.orm_session.delete(query.get(request.GET.get('delete')))
            request.orm_session.commit()
            return HttpResponseRedirect('/trecker/')
        
        # if request.path.startswith('/profile'):
        #     query = query.filter(Goods.favorites.any(UserFavorite.user_id == request.current_user.id))
        modelInfo = PageModelInfo(request.session, '/trecker/', query, Trecker.id)
        return PageTreckerEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @common_page()
    @with_form('form_model', FormTrecker, 'cmd_model_create')
    def create(request, *args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/', request.orm_session.query(Trecker), Trecker.id)
        page = PageTreckerEditor(modelInfo).new(request, ControlInputs(kwargs.get('form_model')))
        return page 

    @common_page()
    @with_form('form_model', FormTrecker, 'cmd_model_update')
    def edit(request, *args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/', request.orm_session.query(Trecker), Trecker.id)
        page = PageTreckerEditor(modelInfo)
        return page.edit(request, args[0] if len(args)==1 else args[1], ControlInputs(kwargs.get('form_model')))

    @common_page()
    def view(request, *args):
        model_id = args[0] if len(args)==1 else args[1]
        if request.GET.get('delete') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(Trecker).get(model_id))
            request.orm_session.commit()
            return HttpResponseRedirect('../')
        modelInfo = PageModelInfo(request.session, '/trecker/', request.orm_session.query(Trecker), Trecker.id)
        page = PageTreckerEditor(modelInfo)
        return page.view(request, args[0] if len(args)==1 else args[1])
    

class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, *args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/categories/', request.orm_session.query(TreckerCategory), TreckerCategory.id)
        return PageCategoryEditor(modelInfo).items(request, kwargs.get('p'), kwargs.get('form_filter'), PageCategoryEditor.toolbar, no_zip=False)

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_create')
    def create(request,*args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/categories/', request.orm_session.query(TreckerCategory), TreckerCategory.id)
        page = PageCategoryEditor(modelInfo).new(request, ControlInputs(kwargs.get('form_model'), classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_update')
    def edit(request, *args, **kwargs):
        model_id = args[0] if len(args)==1 else args[1]
        modelInfo = PageModelInfo(request.session, '/trecker/categories/', request.orm_session.query(TreckerCategory), TreckerCategory.id)
        page = PageCategoryEditor(modelInfo)
        return page.edit(request,model_id, ControlInputs(kwargs.get('form_model')))