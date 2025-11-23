

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
        (_("gender"), "gender"),
        (_("created_at"), "created_at"),
        (_("updated_at"), "updated_at"),
        (_("user"), "user"),
    )

# pages.py - добавьте эти классы страниц
class PageDevelopmentCalendarEditor(PageModelEditor):
    _page_title = _('Календарь развития')
    _record_template = 'records/RecordDevelopmentCalendar.html'
    _record_list_template = 'recordlists/RecordListDevelopmentCalendar.html'
    _new_item_title = "Добавление совета по развитию"
    _default_page_size = 50
    
    _fields = (   
        (_("id"), "id"),
        (_("Номер недели"), "week_number"),
        (_("Заголовок"), "title"),
        (_("Описание"), "description"),
        (_("Категория"), "category"),
        (_("Активный"), "is_active"),
        (_("Создан"), "created_at"),
        (_("Обновлен"), "updated_at"),
    )

# pages.py
class PageDevelopmentCalendarEditor(PageModelEditor):
    _page_title = _('Календарь развития')
    _record_template = 'records/RecordDevelopmentCalendar.html'
    _record_list_template = 'recordlists/RecordListDevelopmentCalendar.html'
    _new_item_title = "Добавление совета по развитию"
    _default_page_size = 50
    
    _fields = (   
        (_("id"), "id"),
        (_("Номер недели"), "week_number"),
        (_("Заголовок"), "title"),
        (_("Описание"), "description"),
        (_("Категория"), "category"),
        (_("Активный"), "is_active"),
        (_("Создан"), "created_at"),
        (_("Обновлен"), "updated_at"),
    )


class PageDevelopmentCalendarEditor(PageModelEditor):
    _page_title = _('Календарь развития')
    _record_template = 'records/RecordDevelopmentCalendar.html'
    _record_list_template = 'recordlists/RecordListDevelopmentCalendar.html'
    _new_item_title = "Добавление совета по развитию"
    _default_page_size = 50
    
    _fields = (   
        (_("id"), "id"),
        (_("Номер недели"), "week_number"),
        (_("Заголовок"), "title"),
        (_("Описание"), "description"),
        (_("Категория"), "category"),
        (_("Активный"), "is_active"),
        (_("Создан"), "created_at"),
        (_("Обновлен"), "updated_at"),
    )