

from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PagePlaceEditor(PageModelEditor):

    _page_title = _('Места')

    _record_template = 'records/RecordPlace.html'
    _record_list_template = 'recordlists/RecordListMap.html'

    _new_item_title = "Новое место"

    _default_page_size = 30
    _fields = (   
        (_('id'), 'id'),
        (_('title'), 'title'),
        (_('description'), 'description'),
        # (_('image'), 'image'),
        (_('category'), 'category'),
        (_('image_url'), 'image_url'),
        (_('rating'), 'rating'),
        (_('tags'), 'tags'),
        (_('latitude'), 'latitude'),
        (_('longitude'), 'longitude'),
        (_('address'), 'address'),
        (_('phone'), 'phone'),
        (_('website'), 'website'),
        (_('schedule'), 'schedule')
    )

class PageCategoryEditor(PageModelEditor):

    _page_title = _('Категории мест')

    _new_item_title = "Новая категория"

    _default_page_size = 30
    _fields = ((_('Название'), 'name',),)
    toolbar = ControlButtonsBar()
    toolbar.add_button(_('Добавить новую категорию'), 'add', redirect_url='0/new/',is_admin=True)