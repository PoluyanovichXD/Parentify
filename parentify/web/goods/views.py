from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render

from parentify.models.models import Goods, GoodsCategory, UserFavorite
from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, page_has_user, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.goods.forms import FormFavorite, FormFilterGoods, FormGoods, FormFilterCategory, FormCategory
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
        query = request.orm_session.query(Goods)
        if request.path.startswith('/profile'):
            query = query.filter(Goods.favorites.any(UserFavorite.user_id == request.current_user.id))
        modelInfo = PageModelInfo(request.session, '/goods/', query.order_by(Goods.created_at.desc()), Goods.id)
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
    @with_form(None, FormFavorite, 'cmd_add_to_favorites','cmd_remove_from_favorites')
    def view(request, model_id):
        if request.GET.get('delete') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(Goods).get(model_id))
            request.orm_session.commit()
            return HttpResponseRedirect('../')
        modelInfo = PageModelInfo(request.session, '/goods/', request.orm_session.query(Goods), Goods.id)
        page = PageGoodsEditor(modelInfo)
        return page.view(request, model_id)
    

    @common_page()
    def preview(request, model_id):
        try:
            return HttpResponse(request.orm_session.query(Goods).get(model_id).image,
                                content_type='image/*')
        except Exception as ex:
            print(ex)
            raise Http404()
    
    @page_has_user()
    @common_page()
    def favorites_list(request):
        """Страница избранных товаров"""
        favorites = request.current_user.get_favorites(request.orm_session)
        context = {
            'favorites': favorites
        }
        return render(request, 'favorites.html', context)
    
    @page_has_user()
    def add_to_favorites(request, goods_id):
        """Добавить товар в избранное (AJAX)"""
        if request.method == 'POST':
            try:
                favorite = request.current_user.add_to_favorites(request.orm_session, goods_id)
                return JsonResponse({
                    'success': True,
                    'is_favorite': True,
                    'message': 'Товар добавлен в избранное'
                })
            except Exception as e:
                print(e)
                return JsonResponse({
                    'success': False,
                    'message': 'Ошибка при добавлении в избранное'
                })
    
    @page_has_user()
    def remove_from_favorites(request, goods_id):
        """Удалить товар из избранного (AJAX)"""
        if request.method == 'POST':
            try:
                request.current_user.remove_from_favorites(request.orm_session, goods_id)
                return JsonResponse({
                    'success': True,
                    'is_favorite': False,
                    'message': 'Товар удален из избранного'
                })
            except Exception as e:
                print(e)
                return JsonResponse({
                    'success': False,
                    'message': 'Ошибка при удалении из избранного'
                })

class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/goods/categories/', request.orm_session.query(GoodsCategory).order_by(GoodsCategory.created_at.desc()), GoodsCategory.id)
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