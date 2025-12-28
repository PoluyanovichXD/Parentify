from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import Goods, GoodsCategory
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *
import datetime


class FormGoods(FormBase):
    title = TextInputField(label=_("Название товара"), required=True, max_length=500)
    category_id = SelectInputField(label=_("Категория"), required=True)
    description = TextAreaInputField(label=_("Описание"), required=False)
    best_place_to_buy = TextInputField(label=_("Лучшее место покупки"), required=False, max_length=500)
    image = FileField(label=_("Изображение"), required=False, images_type=True)
    # is_active = SwitchField(label=_("Активный"), required=False, default=True)

    def __init__(self, request, goods_id=None):
        if goods_id:
            self.goods_id = goods_id
            self.goods = request.orm_session.query(Goods).get(self.goods_id)
            goods_data = self.goods.to_dict()
            super().__init__(request, goods_data)
        else:
            self.goods = Goods()
            super().__init__(request)
        self.fields['category_id'].choices = choise_name_orm(request, GoodsCategory, False)

    def clean(self):
        super(FormGoods, self).clean()

    def cmd_model_create(self, request):
        self.goods.title = self.cleaned_data.get('title')
        self.goods.category_id = self.cleaned_data.get('category_id')
        self.goods.description = self.cleaned_data.get('description')
        self.goods.best_place_to_buy = self.cleaned_data.get('best_place_to_buy')
        self.goods.is_active = self.cleaned_data.get('is_active', True)
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            self.goods.image = image_file.read()
        
        request.orm_session.add(self.goods)
        request.orm_session.commit()
        return '/goods'

    def cmd_model_update(self, request):
        self.goods.title = self.cleaned_data.get('title')
        self.goods.category_id = self.cleaned_data.get('category_id')
        self.goods.description = self.cleaned_data.get('description')
        self.goods.best_place_to_buy = self.cleaned_data.get('best_place_to_buy')
        self.goods.is_active = self.cleaned_data.get('is_active', True)
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            self.goods.image = image_file.read()
        
        request.orm_session.commit()
        return f'/goods/{self.goods_id}'


class FormFilterGoods(FormModelFilter):
    title = TextInputField(label=_('Название товара'), max_length=500, required=False)
    category_id = SelectInputField(label=_("Категория"), required=False)
    best_place_to_buy = TextInputField(label=_('Место покупки'), max_length=500, required=False)

    def __init__(self, request):
        super().__init__(request, 'goods_filter')
        self.fields['category_id'].choices = choise_name_orm(request, GoodsCategory, True)

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(Goods.title.ilike("%" + self.cleaned_data['title'] + "%"))
            
            if self.cleaned_data.get('category_id'):
                data_query = data_query.filter(Goods.category_id == self.cleaned_data.get('category_id'))
            
            if self.cleaned_data.get('best_place_to_buy'):
                data_query = data_query.filter(Goods.best_place_to_buy.ilike("%" + self.cleaned_data['best_place_to_buy'] + "%"))
        
        return data_query
    
class FormCategory(FormBase):
    name = TextInputField(label=_('Название категории'), max_length=255, required=True)

    def __init__(self, request, category_id=None):
        self.category_id = category_id
        print(category_id)
        if category_id:
            self.category = request.orm_session.query(GoodsCategory).get(self.category_id)
            super().__init__(request, {
                'name': self.category.name
            })
        else:
            self.category = GoodsCategory()
            super().__init__(request)
    
    def clean(self):
        super(FormCategory, self).clean()
        
        name = self.cleaned_data.get('name')
        if name:
            query = self.request.orm_session.query(GoodsCategory).filter(
                GoodsCategory.name == name
            )
            
            if hasattr(self, 'category_id') and self.category_id:
                query = query.filter(GoodsCategory.id != self.category_id)
            
            existing_category = query.first()
            
            if existing_category:
                raise ValidationError(_("Категория с таким названием уже существует"))

    def cmd_model_create(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.add(self.category)
        self.request.orm_session.commit()
        return '/goods/categories'

    def cmd_model_update(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.commit()
        return f'/goods/categories'


class FormFilterCategory(FormModelFilter):
    name = TextInputField(label=_('Название категории'), max_length=255, required=False)

    def __init__(self, request):
        super().__init__(request, 'goods_category_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('name'):
                data_query = data_query.filter(GoodsCategory.name.ilike("%" + self.cleaned_data['name'] + "%"))
        return data_query
    
class FormFavorite(FormBase):
    """Форма для добавления/удаления из избранного"""
    
    def __init__(self, request, goods_id):
        self.goods_id = goods_id
        super().__init__(request)
    
    def cmd_add_to_favorites(self, request):
        if request.current_user:
            favorite = request.current_user.add_to_favorites(request.orm_session, self.goods_id)
            return f'/goods/{self.goods_id}'
        return request.path
    
    def cmd_remove_from_favorites(self, request):
        if request.current_user:
            request.current_user.remove_from_favorites(request.orm_session, self.goods_id)
        return request.path