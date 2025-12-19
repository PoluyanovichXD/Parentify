from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageTreckerEditor(PageModelEditor):

    _page_title = _('Трекер')

    _record_template = 'records/RecordTrecker.html'
    _record_list_template = 'recordlists/RecordListTrecker.html'

    _new_item_title = "Новый трекер"

    _default_page_size = 30
    _fields = (   
        (_("id"), "id"),
        (_("date_trecker"), "date_trecker"),
        (_("created_at"), "created_at"),
        (_("content"), "content"),
        (_("comment"), "comment"),
        (_("category_id"), "category_id"),
        (_("children_id"), "children_id"),
        (_("category"), "category"),
        (_("children"), "children"),
    )

class PageCategoryEditor(PageModelEditor):

    _page_title = _('Категории статей')

    _new_item_title = "Новая категория"

    _default_page_size = 30
    _fields = ((_('Название'), 'name',),)
    toolbar = ControlButtonsBar()
    toolbar.add_button(_('Добавить новую категорию'), 'add', redirect_url='0/new/',is_admin=True)