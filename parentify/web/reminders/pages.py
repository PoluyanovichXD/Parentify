from parentify.ui.controls import ControlButtonsBar
from parentify.ui.mvc import PageModelEditor
from django.utils.translation   import gettext as _



class PageReminderEditor(PageModelEditor):

    _page_title = _('Трекер')

    _record_template = 'records/RecordReminder.html'
    _record_list_template = 'recordlists/RecordListReminder.html'

    _new_item_title = "Новый трекер"

    _default_page_size = 30
    _fields = (   
        (_("id"), "id"),
        (_("message"), "message"),
        (_("scheduled_datetime"), "scheduled_datetime"),
        (_("is_sent"), "is_sent"),
        (_("user_id"), "user_id"),
        (_("created_at"), "created_at"),
        (_("time_until_now"), "time_until_now"),
        (_("time_until_now_display"), "time_until_now_display"),
        (_("time_status_color"), "time_status_color"),
        (_("is_overdue"), "is_overdue"),
        (_("time_until_now_simple"), "time_until_now_simple"),
        (_("user"), "user"),
    )
