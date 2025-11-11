from django.http import HttpResponseRedirect
from django.utils.translation           import gettext as _
from parentify.models.models import ForumTopic, ForumComment, ForumLikedComment, ForumTopicCategory
from parentify.ui.forms import FormBase, FormModelFilter, choise_name_orm
from parentify.ui.fields import *


class FormForum(FormBase):
    title = TextInputField(label=_("Заголовок"), required=True)
    category_id = SelectInputField(label=_("Категория"), required=True)
    content = HtmlEditorField(label=_("Ваш вопрос"), required=True)

    def __init__(self, request, forum_id=None):
        if forum_id:
            self.forum_id = forum_id
            self.forum = request.orm_session.query(ForumTopic).get(self.forum_id)
            super().__init__(request, self.forum.to_dict())
        else:
            self.forum = ForumTopic()
            super().__init__(request)
        self.fields['category_id'].choices = choise_name_orm(request, ForumTopicCategory, False)
    
    def clean(self):
        super(FormForum, self).clean()

    def cmd_model_create(self, request):
        self.forum.title = self.cleaned_data.get('title')
        self.forum.category_id = self.cleaned_data.get('category_id')
        self.forum.content = self.cleaned_data.get('content')
        self.forum.user_id = request.current_user.id
        self.request.orm_session.add(self.forum)
        self.request.orm_session.commit()
        return '/forum'

    def cmd_model_update(self, request):
        self.forum.title = self.cleaned_data.get('title')
        self.forum.category_id = self.cleaned_data.get('category_id')
        self.forum.content = self.cleaned_data.get('content')
        self.forum.updated_at = datetime.datetime.now()
        self.request.orm_session.commit()
        return f'/forum/{self.article_id}'
    


class FormFilterForum(FormModelFilter):
    title = TextInputField(label=_('Заголовок'), max_length=350, required=False)
    category_id = SelectInputField(label=_("Категория"), required=False)

    def __init__(self, request):
        super().__init__(request, 'article_filter')
        self.fields['category_id'].choices = choise_name_orm(request, ForumTopicCategory, False)

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('title'):
                data_query = data_query.filter(ForumTopic.title.ilike("%" + self.cleaned_data['title'] + "%"))
            if self.cleaned_data.get('category_id'):
                data_query = data_query.filter(ForumTopic.category_id == self.cleaned_data.get('category_id'))
        return data_query
    
class FormForumComment(FormBase):
    content = TextAreaInputField(label=_("Напишите ваш ответ..."), required=True)

    def __init__(self, request, forum_id=None):
        self.forum_id = forum_id
        self.comment = ForumComment()
        super().__init__(request)
    
    def clean(self):
        super(FormForumComment, self).clean()

    def cmd_model_create(self, request):
        self.comment.content = self.cleaned_data.get('content')
        self.comment.user_id = request.current_user.id
        self.comment.topic_id = self.forum_id
        self.request.orm_session.add(self.comment)
        self.request.orm_session.commit()
        return f'/forum/{self.forum_id}'

    def cmd_model_update(self, request):
        self.comment.content = self.cleaned_data.get('content')
        self.comment.updated_at = datetime.datetime.now()
        self.request.orm_session.commit()
        return f'/forum/{self.forum_id}'
    


class FormCategory(FormBase):
    name = TextInputField(label=_('Название'), max_length=350, required=False)
    def __init__(self, request, category_id=None):
        if category_id:
            self.category_id = category_id
            self.category = request.orm_session.query(ForumTopicCategory).get(self.category_id)
            super().__init__(request, {
                'name':self.category.name
            })
        else:
            self.category = ForumTopicCategory()
            super().__init__(request)
    
    def clean(self):
        super(FormCategory, self).clean()
        if self.request.orm_session.query(ForumTopicCategory).filter(ForumTopicCategory.name == self.cleaned_data.get('name')).first():
            raise ValidationError(_("Данная категория уже присутствует"))

    def cmd_model_create(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.add(self.category)
        self.request.orm_session.commit()
        return '/forum/categories'

    def cmd_model_update(self, request):
        self.category.name = self.cleaned_data.get('name')
        self.request.orm_session.commit()
        return f'/forum/categories'
class FormFilterCategory(FormModelFilter):
    name = TextInputField(label=_('Название'), max_length=350, required=False)
    def __init__(self, request):
        super().__init__(request, 'category_filter')

    def filter(self, data_query):
        if self.is_valid():
            if self.cleaned_data.get('name'):
                data_query = data_query.filter(ForumTopicCategory.name.ilike("%" + self.cleaned_data['name'] + "%"))
        return data_query