from datetime import datetime
from parentify.models.models import ChildDevelopmentWeek
from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation import gettext as _

class PageDevelopmentCalendarEditor(PageModelEditor):

    _page_title = _('Календарь развития')

    _record_template = 'records/RecordDevelopmentCalendar.html'
    _record_list_template = 'recordlists/RecordListDevelopmentCalendar.html'

    _new_item_title = "Добавление недели развития"

    _default_page_size = 30
    _fields = (   
        (_("id"), "id"),
        (_("Номер недели"), "week_number"),
        (_("Заголовок"), "title"),
        (_("Текст"), "description"),
        (_("Советы родителям"), "parent_tips"),
        (_("Ключевые навыки"), "key_skills"),
        (_("Создано"), "created_at"),
        (_("Обновлено"), "updated_at"),
    )