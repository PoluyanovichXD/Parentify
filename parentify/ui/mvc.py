from parentify.ui.pages import *


class PageModelEditor(PageSimple):

    _record_template = 'controls/ControlRecord.html'
    _record_fields = None
    _target = "_self"

    def __init__(self, model_info):
        self._model_info = model_info
        r = super().__init__(self._page_title)
        static_tabs = []
        static_tabs.extend(self._default_tabs)
        static_tabs.extend(self._model_info.static_tabs)
        self.control_tabs = ControlTabs(self._model_info.base_url, static_tabs, self._model_info.dynamic_tabs)
        tabs_bar = ControlBase()
        tabs_bar.add_control('cmd_close_tabs', ControlButton('Закрыть все', self._model_info.base_url + '?closeall'))
        tabs_bar.add_control('tabs', self.control_tabs)
        self.add_control('tabs_bar', tabs_bar)
        return r

    def __check_close(self, request):
        if 'close' in request.GET:
            self._model_info.model_editor_close_tabs([request.path, ])
            raise HttpRedirectException(request.GET['close'])

    def items(self, request, page_number, filter_form=None, toobar_buttons=None, list_name=None,
              recordlist_template='controls/ControlRecordlist.html'):
        if 'closeall' in request.GET:
            self._model_info.model_editor_close_alltabs()
            raise HttpRedirectException(request.path)

        if list_name:
            self.control_tabs.change_active(self._model_info.base_url + list_name + '/')

        page_size = request.session.get(self._model_info.keyname + '_page_size', self._default_page_size)

        recordsForm = ControlForm()

        if filter_form:
            recordsForm.add_control('default_button', ControlEnterCommand(submit_name='cmd_filter'))

        if toobar_buttons:
            recordsForm.add_control('users_toolbar', toobar_buttons)

        if filter_form:
            controlsFilter = ControlBase()

# class ModelEditorController:
#     def list():
#         pass
#     def view():
#         pass
#     def create():
#         pass
#     def edit():
#         pass