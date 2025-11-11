from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import Place, PlaceCategory
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *
import datetime


class FormPlace(FormBase):
    title = TextInputField(label=_("Название"), required=True)
    rating = NumberInputField(label=_("Рейтинг"), required=False, min=0, max=5)
    phone = TextInputField(label=_("Телефон"), required=False)
    website = TextInputField(label=_("Веб-сайт"), required=False)
    schedule = TextInputField(label=_("Режим работы"), required=True)
    category_id = SelectInputField(label=_("Категория"), required=True)
    address = TextInputField(label=_("Адрес"), required=True)
    coords = CoordinatesInputField(label=_("Координаты"), required=True)
    tags = TextInputField(label=_("Теги"), required=False, multiply=True)
    description = TextAreaInputField(label=_("Описание"), required=False)
    image = FileField(label=_("Изображение"), required=False, images_type=True)

    def __init__(self, request, place_id=None):
        if place_id:
            self.place_id = place_id
            self.place = request.orm_session.query(Place).get(self.place_id)
            place_data = self.place.to_dict()
            super().__init__(request, place_data)
        else:
            self.place = Place()
            super().__init__(request)
        self.fields['category_id'].choices = choise_name_orm(request, PlaceCategory, False)

    def clean(self):
        super(FormPlace, self).clean()

    def cmd_model_create(self, request):
        coords = [float(item) for item in self.cleaned_data.get('coords').split(',')] if self.cleaned_data.get('coords') else [None, None]
        self.place.title = self.cleaned_data.get('title')
        self.place.category_id = self.cleaned_data.get('category_id')
        self.place.description = self.cleaned_data.get('description')
        self.place.address = self.cleaned_data.get('address')
        self.place.phone = self.cleaned_data.get('phone')
        self.place.website = self.cleaned_data.get('website')
        self.place.schedule = self.cleaned_data.get('schedule')
        self.place.latitude = coords[0] if coords[0] else None
        self.place.longitude = coords[1] if coords[1] else None
        self.place.rating = self.cleaned_data.get('rating', 0)
        self.place.tags = self.cleaned_data.get('tags', []) if self.cleaned_data.get('tags') else []
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            self.place.image = image_file.read()
        
        request.orm_session.add(self.place)
        request.orm_session.commit()
        return '/map' 
    def cmd_model_update(self, request):
        coords = [float(item) for item in self.cleaned_data.get('coords').split(',')] if self.cleaned_data.get('coords') else [None, None]
        self.place.title = self.cleaned_data.get('title')
        self.place.category_id = self.cleaned_data.get('category_id')
        self.place.description = self.cleaned_data.get('description')
        self.place.address = self.cleaned_data.get('address')
        self.place.phone = self.cleaned_data.get('phone')
        self.place.website = self.cleaned_data.get('website')
        self.place.schedule = self.cleaned_data.get('schedule')
        self.place.latitude = coords[0] if coords[0] else None
        self.place.longitude = coords[1] if coords[1] else None
        self.place.rating = self.cleaned_data.get('rating', 0)
        self.place.tags = self.cleaned_data.get('tags', []) if self.cleaned_data.get('tags') else []
        
        image_file = self.cleaned_data.get('image')
        if image_file:
            self.place.image = image_file.read()
        
        request.orm_session.commit()
        return f'/map'
    

class FormFilterPlace(FormModelFilter):
    title = TextInputField(label=_('Название'), max_length=255, required=False)
    address = TextInputField(label=_('Адрес'), max_length=255, required=False)
    min_rating = NumberInputField(label=_('Минимальный рейтинг'), required=False)
    max_rating = NumberInputField(label=_('Максимальный рейтинг'), required=False)

    def __init__(self, request):
        super().__init__(request, 'place_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(Place.title.ilike("%" + self.cleaned_data['title'] + "%"))
            
            if self.cleaned_data.get('address'):
                data_query = data_query.filter(Place.address.ilike("%" + self.cleaned_data['address'] + "%"))
            
            min_rating = self.cleaned_data.get('min_rating')
            max_rating = self.cleaned_data.get('max_rating')
            
            if min_rating:
                data_query = data_query.filter(Place.rating >= min_rating)
            if max_rating:
                data_query = data_query.filter(Place.rating <= max_rating)
        
        return data_query
    

# ArticleCategory
class FormCategory(FormBase):
    name = TextInputField(label=_('Название'), max_length=350, required=False)
    def __init__(self, request, category_id=None):
        if category_id:
            self.category_id = category_id
            self.category = request.orm_session.query(PlaceCategory).get(self.category_id)
            super().__init__(request, {
                'name':self.category.name
            })
        else:
            self.category = PlaceCategory()
            super().__init__(request)
    
    def clean(self):
        super(FormCategory, self).clean()
        if self.request.orm_session.query(PlaceCategory).filter(PlaceCategory.name == self.cleaned_data.get('name')).first():
            raise ValidationError(_("Данная категория уже присутствует"))

    def cmd_model_create(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.add(self.category)
        self.request.orm_session.commit()
        return '/map/categories'

    def cmd_model_update(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.commit()
        return f'/map/categories'
class FormFilterCategory(FormModelFilter):
    name = TextInputField(label=_('Название'), max_length=350, required=False)
    def __init__(self, request):
        super().__init__(request, 'category_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('name'):
                data_query = data_query.filter(PlaceCategory.name.ilike("%" + self.cleaned_data['name'] + "%"))
        return data_query