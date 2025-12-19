

from datetime import datetime
from parentify.models.models import UserChild
from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageChildEditor(PageModelEditor):

    _page_title = _('Дети')

    _record_template = 'records/RecordChild.html'
    _record_list_template = 'recordlists/RecordListChild.html'

    _new_item_title = "Добавление ребёнка"

    _default_page_size = 30
    _fields = (   
        (_("id"), "id"),
        (_("user_id"), "user_id"),
        (_("first_name"), "first_name"),
        (_("last_name"), "last_name"),
        (_("is_active"), "is_active"),
        (_("birth_date"), "birth_date"),
        (_("birth_year"), "birth_year"),
        (_("zodiac_sign"), "zodiac_sign"),
        (_("gender"), "gender"),
        (_("created_at"), "created_at"),
        (_("updated_at"), "updated_at"),
        (_("user"), "user"),
    )