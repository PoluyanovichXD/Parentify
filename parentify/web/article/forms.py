from django.http import HttpResponseRedirect
from django.utils.translation           import gettext as _
from parentify.models.models import Article, ArticleCategory
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *


class FormArticle(FormBase):
    title = TextInputField(label=_("Заголовок"), required=True)
    category_id = SelectInputField(label=_("Категория"), required=True)
    html = HtmlEditorField(label=_("Статья"), required=True)
    image = FileField(label=_("Заголовочное изображение"), required=True, images_type=True)

    def __init__(self, request, article_id=None):
        if article_id:
            self.article_id = article_id
            self.article = request.orm_session.query(Article).get(self.article_id)
            super().__init__(request, self.article.to_dict())
        else:
            self.article = Article()
            super().__init__(request)
        self.fields['category_id'].choices = choise_name_orm(request, ArticleCategory, False)
    
    def clean(self):
        super(FormArticle, self).clean()

    def cmd_model_create(self, request):
        self.article.title = self.cleaned_data.get('title')
        self.article.category_id = self.cleaned_data.get('category_id')
        self.article.html = self.cleaned_data.get('html')
        self.article.image = self.cleaned_data.get('image').read()
        self.request.orm_session.add(self.article)
        self.request.orm_session.commit()
        return '/article'

    def cmd_model_update(self, request):
        self.article.title = self.cleaned_data.get('title')
        self.article.category_id = self.cleaned_data.get('category_id')
        self.article.html = self.cleaned_data.get('html')
        self.article.image = self.cleaned_data.get('image').read()
        self.article.updated_at = datetime.datetime.now()
        self.request.orm_session.commit()
        return f'/article/{self.article_id}'
    


class FormFilterArticle(FormModelFilter):
    title = TextInputField(label=_('Заголовок'), max_length=350, required=False)
    category_id = SelectInputField(label=_("Категория"), required=True)

    def __init__(self, request):
        super().__init__(request, 'article_filter')
        self.fields['category_id'].choices = choise_name_orm(request, ArticleCategory, False)

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(Article.title.ilike("%" + self.cleaned_data['title'] + "%"))
            if self.cleaned_data.get('category_id'):
                data_query = data_query.filter(Article.category_id==self.cleaned_data.get('category_id'))
        return data_query
    

# ArticleCategory
class FormCategory(FormBase):
    name = TextInputField(label=_('Название'), max_length=350, required=False)
    def __init__(self, request, category_id=None):
        self.category_id = category_id
        if category_id:
            self.category = request.orm_session.query(ArticleCategory).get(self.category_id)
            super().__init__(request, {
                'name':self.category.name
            })
        else:
            self.category = ArticleCategory()
            super().__init__(request)
    def clean(self):
        super(FormCategory, self).clean()
        
        name = self.cleaned_data.get('name')
        if name:
            query = self.request.orm_session.query(ArticleCategory).filter(
                ArticleCategory.name == name
            )
            
            if hasattr(self, 'category_id') and self.category_id:
                query = query.filter(ArticleCategory.id != self.category_id)
            
            existing_category = query.first()
            
            if existing_category:
                raise ValidationError(_("Категория с таким названием уже существует"))

    def cmd_model_create(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.add(self.category)
        self.request.orm_session.commit()
        return '/article/categories'

    def cmd_model_update(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.commit()
        return f'/article/categories'
class FormFilterCategory(FormModelFilter):
    name = TextInputField(label=_('Название'), max_length=350, required=False)
    def __init__(self, request):
        super().__init__(request, 'category_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('name'):
                data_query = data_query.filter(ArticleCategory.name.ilike("%" + self.cleaned_data['name'] + "%"))
        return data_query