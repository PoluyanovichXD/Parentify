

from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _


class PageAdminEditor(PageModelEditor):

    _page_title = _('Категории статей')

    _new_item_title = "Новая категория"

    _default_page_size = 30
    _fields = ((_('Название'), 'name',),)
    _fields_event = ['delete']
    toolbar = ControlButtonsBar()
    toolbar.add_button(_('Добавить'), 'add', redirect_url='0/new/')
