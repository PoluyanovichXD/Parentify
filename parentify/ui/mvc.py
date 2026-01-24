from django.http import HttpResponseRedirect
from django.template.loader import render_to_string
from django.utils.translation           import gettext as _
from parentify.ui.controls import ControlBase, ControlButtonsBar, ControlExeption, ControlForm, ControlHtml, ControlInputs, ControlPagerFull, ControlRecord, ControlRecordlist
from parentify.ui.decorators import HttpRedirectException
from parentify.ui.pages import *


class PageModelInfo:
    def __init__(self, session, base_url, query, primary_key, format_url=None):
        #TODO: use user instead session to save tabs
        self.primary_key = primary_key
        self.base_url = base_url
        self.format_url = format_url if format_url else self.base_url
        self.keyname = base_url.lstrip('/').replace('/', '_')
        self.query = query
        session.modified = True
        self.session = session


class PageModelEditor(PageSimple):

    _record_template = 'controls/ControlRecord.html'
    _record_fields = None
    _target = "_self"

    def __init__(self, model_info):
        self._model_info = model_info
        r = super().__init__(self._page_title)
        return r

    def default_view_control(self, itemId):
        primary_key = self._model_info.primary_key if type(self._model_info.primary_key) == str else self._model_info.primary_key
        if not hasattr(self._model_info.query, 'filter') and hasattr(self._model_info.query, 'filter_by'):
            return ControlRecord(self._model_info.query.filter_by(**{primary_key: itemId}), self._record_fields, self._record_template)
        return ControlRecord(self._model_info.query.filter(primary_key == itemId), self._record_fields,
                             self._record_template)

    def items(self, request, page_number, filter_form=None, toobar_buttons=None, list_name=None, get = None, controls=None,recordlist_template='controls/ControlRecordList.html',*args,**kwargs):
        if 'closeall' in request.GET:
            self._model_info.model_editor_close_alltabs()
            raise HttpRedirectException(request.path)
            

        page_size = request.session.get(self._model_info.keyname + '_page_size', self._default_page_size)

        recordsForm = ControlForm()
        # if filter_form:
            # recordsForm.add_control('default_button', ControlEnterCommand(submit_name='cmd_filter'))
        if filter_form:
            controlsFilter = ControlBase()
            inputs = ControlInputs(filter_form, 'forms/FilterForm.html')
            
            bt_bar = ControlButtonsBar()
            bt_bar.add_button(_('Фильтровать'),'Default', submit_name='cmd_filter')
            bt_bar.add_button(_('Очистить фильтр'),'Default', submit_name='cmd_discard')
            inputs.add_botton_control('bt_bar', bt_bar)
            controlsFilter.add_control("filter_inputs", inputs)
            if toobar_buttons:
                controlsFilter.add_botton_control('users_toolbar', toobar_buttons)
            recordsForm.add_control('formFilter', controlsFilter)
        else:
            if toobar_buttons:
                recordsForm.add_control('users_toolbar', toobar_buttons)
        if isinstance(self._model_info.query,ControlExeption):
            recordsForm.add_control(self._model_info.query.classname,self._model_info.query.control)
            self.add_control('recordForm', recordsForm)
            return self
        try:
            all_count = self._model_info.query.count()
        except Exception as ex:
            all_count = len(self._model_info.query)
        if filter_form:
            try:
                query = filter_form.filter(self._model_info.query)
            except:
                query = self._model_info.query
        else:
            query = self._model_info.query
        try:
            filter_count = query.count()
        except:
            filter_count = len(query)
        
        if controls != None:
            count_control = 0
            if type(controls) == list or type(controls) == tuple:
                for control in controls:
                    recordsForm.add_control(f"{count_control}-control",control)
                    count_control=count_control+1
            else:
                recordsForm.add_control(f"{count_control}-control",controls)

        if kwargs.get('btn_controls'):
            count_control = 0
            if type(kwargs.get('btn_controls')) == list or type(kwargs.get('btn_controls')) == tuple:
                for control in kwargs.get('btn_controls', []):
                    recordsForm.add_botton_control(f"{count_control}-control-btn",control)
                    count_control=count_control+1
            else:
                recordsForm.add_botton_control(f"{count_control}-control-btn",kwargs.get('btn_controls'))

        
        control_name = list_name if list_name else 'recordslist'
        url_primary = '{%%}'
        
        if get != None:
            url_primary = self._model_info.base_url+get
            if get[0] != '/':
                url_primary = get
            elif get[0] != '&' or get[0] != '?':
                url_primary = get

        primary_key = self._model_info.primary_key if type(self._model_info.primary_key) == str else self._model_info.primary_key.name

        if filter_count < (page_number * page_size):
            count_def = filter_count%page_size
            page_number = (filter_count-count_def)/page_size

        if 'approved' in request.GET:
            q = query.filter_by(**{primary_key:request.GET['approved']})
            if q.count() != 0:
                q = q.first()
                if hasattr(q,'approved'):
                    q.approved = True
                    request.orm_session.commit()
                if 'func_approved' in kwargs:
                    kwargs['func_approved'](request, q)
            return HttpResponseRedirect(request.path)

        if 'disapproved' in request.GET:
            q = query.filter_by(**{primary_key:request.GET['disapproved']})
            if q.count() != 0:
                q = q.first()
                if hasattr(q,'approved'):
                    q.approved = False
                    request.orm_session.commit()
                if 'func_disapproved' in kwargs:
                    kwargs['func_disapproved'](request, q)
            return HttpResponseRedirect(request.path)

        if 'active' in request.GET:
            q = query.filter_by(**{primary_key:request.GET['active']})
            if q.count() != 0:
                q = q.first()
                if hasattr(q,'active'):
                    q.active = True
                    request.orm_session.commit()
                if 'func_active' in kwargs:
                    kwargs['func_active'](request, q)
            return HttpResponseRedirect(request.path)

        if 'delete' in request.GET:
            q = query.filter_by(**{primary_key:request.GET['delete']})
            w = request.current_user
            if q.count() != 0:
                if w and w.is_admin:
                    q = q.first()
                    try:
                        request.orm_session.delete(q)
                        request.orm_session.commit()
                    except:
                        try:
                            q.delete()
                        except:
                            pass
                    if 'func_delete' in kwargs:
                        kwargs['func_delete'](request, q)
            return HttpResponseRedirect(request.path)
        recordList = ControlRecordlist(query[page_number * page_size: (page_number + 1) * page_size],
                                                self._fields, primary_key,
                                                primary_key,
                                                url_primary, self._target,
                                                control_template=getattr(self, '_record_list_template',recordlist_template),
                                                fields_url=getattr(self,'_fields_url',[]),
                                                fields_sort=getattr(self,'_fields_sort',[]),
                                                fields_event=getattr(self,'_fields_event',[]),*args, **kwargs)
        recordList.add_pager('bottom_pager', ControlPagerFull(query, page_number, page_size, all_count, filter_count))
        recordsForm.add_control(control_name,recordList)
        
        self.add_control('recordForm', recordsForm)
        return self
    

    def view(self, request, itemId, control=None):
        if 'closeall' in request.GET:
            self._model_info.model_editor_close_alltabs()
            raise HttpRedirectException(request.path)
        primary_key = self._model_info.primary_key if type(self._model_info.primary_key) == str else self._model_info.primary_key
        if not self._model_info.query.filter(primary_key == itemId).first():
            # self.clear_controls()
            return self.add_control('NotFound',ControlExeption(control_template="controls/catch/NotFound.html"))
            raise Http404()
        if not control:
            control = self.default_view_control(itemId)
        self.add_control('record', control)
        try:
            if not hasattr(self._model_info.query, 'filter') and hasattr(self._model_info.query, 'filter_by'):
                self.change_title(str(self._model_info.query.filter_by(**{primary_key: itemId})[0]))
            else:
                self.change_title(str(self._model_info.query.filter(primary_key == itemId)[0]))
        except Exception as ex:
            pass
        return self

    def edit(self, request, itemId, control_editor,bt_append=[],cancel_url='../../'):
        primary_key = self._model_info.primary_key if type(self._model_info.primary_key) == str else self._model_info.primary_key
        if 'closeall' in request.GET:
            self._model_info.model_editor_close_alltabs()
            raise HttpRedirectException(request.path)
        if 'iframe_form' in request.GET and 'iframe_close' in request.GET:
            self.add_control('iframe_close',ControlHtml(render_to_string('iframes/FormIframeEditClose.html')))
            self.change_template('wrappers/clear.html')
            return self.render(request)
        if not 'iframe_form' in request.GET and not 'iframe_close' in request.GET:
            if not self._model_info.query.filter(primary_key == itemId).first():
                # self.clear_controls()
                return self.add_control('NotFound',ControlExeption(control_template="controls/catch/NotFound.html"))
            
        formControl = ControlForm()
        
        bt_bar = ControlButtonsBar()
        for bt in bt_append:
            if type(bt) == dict:
                getattr(bt_bar,'add_button')(btn_type='Default',**bt)
            else:
                getattr(bt_bar,'add_button')(bt[0],'Default',redirect_url=bt[1])
        if 'iframe_form' in request.GET:
            bt_bar.add_button(_('Отмена'),'Default', js_action='CloseIframeModal,null,element=event.target')
            bt_bar.add_button(_('Сохранить'),'Default', js_action='"cmd_model_update","submit_iframe"')
        else:
            bt_bar.add_button(_('Отмена'),'Default', redirect_url=cancel_url)
            bt_bar.add_button(_('Сохранить'),'Default', submit_name='cmd_model_update')
        control_editor.add_botton_control('bt_bar', bt_bar)
        formControl.add_control('editor', control_editor)
        self.add_control('form_edit_model', formControl)
        try:
            if not hasattr(self._model_info.query, 'filter') and hasattr(self._model_info.query, 'filter_by'):
                self.change_title(str(self._model_info.query.filter_by(**{primary_key: itemId})[0]))
            else:
                self.change_title(str(self._model_info.query.filter(primary_key == itemId)[0]))
        except Exception as ex:
            pass
        if 'iframe_form' in request.GET:
            self.change_template('wrappers/clear.html')
            return self.render(request)
        return self


    def new(self, request, control_editor, url=None, wizard=False,cancel_url='../../'):
        if 'iframe_form' in request.GET and 'iframe_close' in request.GET:
            self.add_control('iframe_close',ControlHtml(render_to_string('iframes/FormIframeNewClose.html')))
            self.change_template('wrappers/clear.html')
            return self.render(request)

        formControl = ControlForm()
        bt_bar = ControlButtonsBar()
        if wizard:
            bt_bar.add_button(_('Отмена'),'Default', redirect_url='?close=../../../')
            i = request.path.find('new/')
            if i != -1:
                if int(request.path[i+4:len(request.path)-1]) != 0:
                    bt_bar.add_button(_('Назад'),'Default', submit_name='cmd_model_back')
            bt_bar.add_button(_('Далее'),'Default', submit_name='cmd_model_next')
        else:
            if 'iframe_form' in request.GET:
                bt_bar.add_button(_('Отмена'),'Default', js_action='CloseIframeModal,null,element=event.target')
                bt_bar.add_button(_('Сохранить'),'Default', js_action='"cmd_model_create","submit_iframe"')
            else:
                bt_bar.add_button(_('Отмена'),'Default', redirect_url=cancel_url)
                bt_bar.add_button(_('Сохранить'),'Default', submit_name='cmd_model_create')
        control_editor.add_botton_control('bt_bar', bt_bar)
        formControl.add_control('editor', control_editor)
        self.add_control('form_new_model', formControl)
        if 'iframe_form' in request.GET:
            self.change_template('wrappers/clear.html')
            return self.render(request)
            
        return self