

from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageNewsEditor(PageModelEditor):

    _page_title = _('Новости')

    _record_template = 'records/RecordNews.html'

    _new_item_title = "Новая публикация"

    _default_page_size = 30
    _fields = (   (_('id'), 'news_id'),
                  (_('Дата'), 'news_date'),
                  (_('Заголовок'), 'title'),
                  (_('Тело'), 'body'),
                  (_('Предпросмотр'), 'preview_text'),
                  (_('Важность'), 'important'),
               )
    _fields_sort = ('news_date','title','body','preview_text','important')
    _fields_url = ()
    _fields_event = ('checkbox')