from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageForumEditor(PageModelEditor):

    _page_title = _('Форум')

    _record_template = 'records/RecordForum.html'
    _record_list_template = 'recordlists/RecordListForum.html'

    _new_item_title = "Новая статья"

    _default_page_size = 30
    _fields = (   
        (_('Заголовок'), 'title'),
        (_('Категория'), 'category'),
        (_('Контент'), 'content'),
        (_('Тег'), 'tags'),
        (_('Создатель'), 'user'),
        (_('Коментарии'), 'comments'),
        (_('Дата создания'), 'created_at'),
        (_('Дата изменения'), 'updated_at'),
    )

class PageCategoryEditor(PageModelEditor):

    _page_title = _('Категории мест')

    _new_item_title = "Новая категория"

    _default_page_size = 30
    _fields = ((_('Название'), 'name',),)
    toolbar = ControlButtonsBar()
    toolbar.add_button(_('Добавить новую категорию'), 'add', redirect_url='0/new/',is_admin=True)