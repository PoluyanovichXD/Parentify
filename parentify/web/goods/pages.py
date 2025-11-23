

from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageGoodsEditor(PageModelEditor):

    _page_title = _('Товары')

    _record_template = 'records/RecordGoods.html'
    _record_list_template = 'recordlists/RecordListGoods.html'

    _new_item_title = "Новая товар"

    _default_page_size = 30
    _fields = (   
        (_("id"), "id"),
        (_("title"), "title"),
        (_("image"), "image"),
        (_("image_url"), "image_url"),
        (_("category_id"), "category_id"),
        (_("description"), "description"),
        (_("best_place_to_buy"), "best_place_to_buy"),
        (_("is_active"), "is_active"),
        (_("created_at"), "created_at"),
        (_("updated_at"), "updated_at"),
        (_("category"), "category"),
    )

class PageCategoryEditor(PageModelEditor):

    _page_title = _('Категории статей')

    _new_item_title = "Новая категория"

    _default_page_size = 30
    _fields = ((_('Название'), 'name',),)
    toolbar = ControlButtonsBar()
    toolbar.add_button(_('Добавить новую категорию'), 'add', redirect_url='0/new/',is_admin=True)