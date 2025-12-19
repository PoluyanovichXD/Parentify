from django.http import HttpResponseRedirect
from django.utils.translation import gettext as _
from parentify.models.models import UserChild, Trecker, TreckerCategory
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *
import datetime


class FormTrecker(FormBase):
    category_id = SelectInputField(label=_("Категория"), required=True)
    children_id = SelectInputField(label=_("Ребёнок"), required=True)
    date_trecker = DateTimeInputField(label=_("Дата и время"),required=True)
    value = NumberInputField(label=_("Значение"), required=True)
    comment = TextAreaInputField(label=_("Коментарий"), required=False)
    
    def __init__(self, request, *args):
        if not request.path.startswith('/profile/'):
            trecker_id = None if not args else (args[0] if len(args)==1 else args[1])
        else:
            trecker_id = None
            if args and len(args)==2:
                trecker_id = args[1]
            elif args and len(args)==1:
                trecker_id = args[0]
        if trecker_id:
            self.trecker_id = trecker_id
            self.trecker = request.orm_session.query(Trecker).get(self.trecker_id)
            data = self.trecker.to_dict()
            super().__init__(request, data)
        else:
            self.trecker = Trecker()
            super().__init__(request)
        self.fields['category_id'].choices = choise_name_orm(request, TreckerCategory, False)
        childrens = request.orm_session.query(UserChild).filter(UserChild.user_id==request.current_user.id)
        self.fields['children_id'].choices = choise_name_orm(request, UserChild, False, ['first_name', 'last_name']) if request.current_user.is_admin else [(item.full_name, item.id,) for item in childrens]

    def clean(self):
        super(FormTrecker, self).clean()

    def cmd_model_create(self, request):
        self.trecker.category_id = self.cleaned_data.get('category_id')
        self.trecker.children_id = self.cleaned_data.get('children_id')
        self.trecker.value = self.cleaned_data.get('value')
        self.trecker.comment = self.cleaned_data.get('comment')
        self.trecker.date_trecker = self.cleaned_data.get('date_trecker')
        
        request.orm_session.add(self.trecker)
        request.orm_session.commit()
        return '../../'

    def cmd_model_update(self, request):
        self.trecker.category_id = self.cleaned_data.get('category_id')
        self.trecker.children_id = self.cleaned_data.get('children_id')
        self.trecker.value = self.cleaned_data.get('value')
        self.trecker.comment = self.cleaned_data.get('comment')
        self.trecker.date_trecker = self.cleaned_data.get('date_trecker')
        
        request.orm_session.commit()
        return f'../'


class FormFilterTrecker(FormModelFilter):
    content = TextInputField(label=_('Значение трекера'), required=False)
    category_id = SelectInputField(label=_("Категория"), required=False)

    def __init__(self, request, *args):
        super().__init__(request, 'trecker_filter')
        self.fields['category_id'].choices = choise_name_orm(request, TreckerCategory, True)

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('content'):
                data_query = data_query.filter(Trecker.content.ilike("%" + self.cleaned_data['content'] + "%"))
            
            if self.cleaned_data.get('category_id'):
                data_query = data_query.filter(Trecker.category_id == self.cleaned_data.get('category_id'))
            
        return data_query
    
class FormCategory(FormBase):
    name = TextInputField(label=_('Название категории'), max_length=255, required=True)
    unit = TextInputField(label=_('Единица измерения'), max_length=255, required=False)

    def __init__(self, request, *args):
        if not request.path.startswith('/profile/'):
            category_id = None if not args else (args[0] if len(args)==1 else args[1])
        else:
            category_id = None
            if args and len(args)==2:
                category_id = args[1]
            elif args and len(args)==1:
                category_id = args[0]
        if category_id:
            self.category_id = category_id
            self.category = request.orm_session.query(TreckerCategory).get(self.category_id)
            super().__init__(request, {
                'name': self.category.name,
                'unit': self.category.unit
            })
        else:
            self.category = TreckerCategory()
            super().__init__(request)
    
    def clean(self):
        super(FormCategory, self).clean()
        
        name = self.cleaned_data.get('name')
        if name:
            query = self.request.orm_session.query(TreckerCategory).filter(
                TreckerCategory.name == name
            )
            
            if self.category_id:
                query = query.filter(TreckerCategory.id != self.category_id)
            
            existing_category = query.first()
            
            if existing_category:
                raise ValidationError(_("Категория с таким названием уже существует"))

    def cmd_model_create(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.category.unit = self.cleaned_data.get('unit')
        self.request.orm_session.add(self.category)
        self.request.orm_session.commit()
        return '../../'

    def cmd_model_update(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.category.unit = self.cleaned_data.get('unit')
        self.request.orm_session.commit()
        return f'../../'


class FormFilterCategory(FormModelFilter):
    name = TextInputField(label=_('Название категории'), max_length=255, required=False)

    def __init__(self, request, *args):
        super().__init__(request, 'trecker_category_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('name'):
                data_query = data_query.filter(TreckerCategory.name.ilike("%" + self.cleaned_data['name'] + "%"))
        return data_query
    