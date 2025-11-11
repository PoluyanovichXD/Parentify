from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from parentify.models.models import Goods, GoodsCategory
from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.goods.forms import FormFilterGoods, FormGoods, FormFilterCategory, FormCategory
from parentify.web.goods.pages import PageGoodsEditor, PageCategoryEditor

class goods:
    @common_page()
    @with_form('form_filter', FormFilterGoods, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        if request.GET.get('delete') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(Goods).get(request.GET.get('delete')))
            request.orm_session.commit()
            return HttpResponseRedirect('/goods/')
        modelInfo = PageModelInfo(request.session, '/goods/', request.orm_session.query(Goods), Goods.id)
        return PageGoodsEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @common_page()
    @with_form('form_model', FormGoods, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/goods/', request.orm_session.query(Goods), Goods.id)
        page = PageGoodsEditor(modelInfo).new(request, ControlInputs(form_model))
        return page 

    @common_page()
    @with_form('form_model', FormGoods, 'cmd_model_update')
    def edit(request, model_id, form_model):
        modelInfo = PageModelInfo(request.session, '/goods/', request.orm_session.query(Goods), Goods.id)
        page = PageGoodsEditor(modelInfo)
        return page.edit(request, model_id, ControlInputs(form_model))

    @common_page()
    def view(request, model_id):
        modelInfo = PageModelInfo(request.session, '/goods/', request.orm_session.query(Goods), Goods.id)
        page = PageGoodsEditor(modelInfo)
        return page.view(request, model_id)
    
        

class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/goods/categories/', request.orm_session.query(GoodsCategory), GoodsCategory.id)
        return PageCategoryEditor(modelInfo).items(request, p, form_filter, PageCategoryEditor.toolbar, no_zip=False)

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/goods/categories/', request.orm_session.query(GoodsCategory), GoodsCategory.id)
        page = PageCategoryEditor(modelInfo).new(request, ControlInputs(form_model, classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_update')
    def edit(request, model_id, form_model):
        modelInfo = PageModelInfo(request.session, '/goods/categories/', request.orm_session.query(GoodsCategory), GoodsCategory.id)
        page = PageCategoryEditor(modelInfo)
        return page.edit(request,model_id, ControlInputs(form_model))