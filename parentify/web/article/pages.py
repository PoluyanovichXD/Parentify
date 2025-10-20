

from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageArticleEditor(PageModelEditor):

    _page_title = _('Статьи')

    _record_template = 'records/RecordArticle.html'
    _record_list_template = 'recordlists/RecordListArticle.html'

    _new_item_title = "Новая статья"

    _default_page_size = 30
    _fields = (   
        (_('Заголовок'), 'title'),
        (_('Категория'), 'category'),
        (_('Шаблон'), 'html'),
        (_('Изображение'), 'image_url'),
        (_('Дата создания'), 'created_at')
    )

class PageCategoryEditor(PageModelEditor):

    _page_title = _('Категории статей')

    _new_item_title = "Новая категория"

    _default_page_size = 30
    _fields = ((_('Название'), 'name',),)
    toolbar = ControlButtonsBar()
    toolbar.add_button(_('Добавить новую категорию'), 'add', redirect_url='0/new/',is_admin=True)