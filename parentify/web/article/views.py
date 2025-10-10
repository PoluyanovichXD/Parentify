from django.shortcuts import render
from django.utils.translation           import gettext as _

from parentify.ui.controls import ControlHtml, ControlInputs
from parentify.ui.decorators import with_form, common_page
from parentify.ui.pages import PageSimple
from parentify.web.article.form import FormArticle
from parentify.settings           import PROJECT_ROOT



@common_page()
def home(request):
    page = PageSimple(_('Статьи'))
    content = {}
    page.add_control('WEB', ControlHtml(content, PROJECT_ROOT + '/parentify/templates/pages/article/home.html'))
    return render(request, 'pages/article/home.html')

@common_page()
@with_form('form_article', FormArticle, 'cmd_create')
def create(request, form_article):
    page = PageSimple(_('Добавить статью'))
    editor = ControlInputs()
    page.add_control('editor', editor)
    return page


@with_form('form_article', FormArticle, 'cmd_edit')
def edit(request, article_id):
    pass

def view(request):
    pass