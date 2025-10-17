from django.http import HttpResponseRedirect
from django.utils.translation           import gettext as _
from parentify.models.models import ForumTopic
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *


class FormForum(FormBase):
    title = TextInputField(label=_("Заголовок"), required=True)
    category_id = SelectInputField(label=_("Категория"), required=False)
    html = HtmlEditorField(label=_("Статья"), required=True)
    image = FileField(label=_("Заголовочное изображение"), required=True, images_type=True)

    def __init__(self, request, article_id=None):
        if article_id:
            self.article_id = article_id
            self.article = request.orm_session.query(ForumTopic).get(self.article_id)
            super().__init__(request, self.article.to_dict())
        else:
            self.article = ForumTopic()
            super().__init__(request)
    
    def clean(self):
        super(FormForum, self).clean()

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
    


class FormFilterForum(FormModelFilter):
    title = TextInputField(label=_('Заголовок'), max_length=350, required=False)

    def __init__(self, request):
        super().__init__(request, 'article_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(ForumTopic.title.ilike("%" + self.cleaned_data['title'] + "%"))
        return data_query