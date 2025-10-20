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