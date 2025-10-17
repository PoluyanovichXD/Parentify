from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageForumEditor(PageModelEditor):

    _page_title = _('Форум')

    _record_template = 'records/RecordArticle.html'
    _record_list_template = 'recordlists/RecordListArticle.html'

    _new_item_title = "Новая статья"

    _default_page_size = 30
    _fields = (   
                  (_('Заголовок'), 'title'),
                  (_('Категория'), 'category'),
                  (_('Шаблон'), 'html'),
                  (_('Изображение'), 'image_url'),
                  (_('Дата создания'), 'created_at'),
               )