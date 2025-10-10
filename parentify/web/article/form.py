from django.http import HttpResponseRedirect
from django.utils.translation           import gettext as _
from parentify.ui.forms import FormBase
from parentify.ui.fields import *


class FormArticle(FormBase):
    title = TextInputField(label=_("Заголовок"), required=True)
    html = HtmlEditorField(label=_("Статья"), required=True)
    image = FileField(label=_("Заголовочный файл"), required=True)

    def __init__(self, request, article_id=None):
        pass

    def cmd_create(self):
        self.cleaned_data
        return HttpResponseRedirect('/')

    def cmd_edit(self):
        self.cleaned_data
        return HttpResponseRedirect('/')