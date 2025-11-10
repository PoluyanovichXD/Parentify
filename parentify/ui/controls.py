import datetime, math
from django.template.loader import render_to_string
from sqlalchemy import Integer, String, Boolean, DateTime, Text, Float, Date, ARRAY


class ControlBase(object):

    def __init__(self, control_template='controls/ControlBase.html',classname=None):
        self.__controlTemplate = control_template
        self.__subcontrols = []
        self.__btn_controls = []
        self.__need_css = []
        self.__need_js = []
        self.__context = {}
        self.__classname = classname
        super().__init__()

    def get_template(self):
        return self.__controlTemplate

    def get_subcontrols(self):
        return self.__subcontrols

    def need_css(self, name):
        assert name not in self.__need_css, "duplicate css"
        self.__need_css.append(name)

    def need_js(self, name):
        assert name not in self.__need_js, "duplicate js"
        self.__need_js.append(name)

    def add_control(self, name, control,classname=None):
        assert name not in ([c[0]] for c in self.__subcontrols), "duplicate control name"
        if classname == None:
            classname = name
        self.__subcontrols.append((name, control,classname))
    
    def add_botton_control(self,name,control):
        assert name not in ([c[0]] for c in self.__btn_controls), "duplicate control name"
        self.__btn_controls.append((name, control))
    
    def add_context(self,context):
        self.__context.update(context)

    def publish(self, context_branch, js, css):
        for v in self.__need_js:
            if v not in js:
                js.append(v)
        for v in self.__need_css:
            if v not in css:
                css.append(v)
        if len(self.__subcontrols) > 0:
            context_branch['controls'] = []
            context_branch['btn_controls'] = []
            for c in self.__subcontrols:
                subcontrol = {'name': c[0],'classname': c[2]}
                c[1].publish(subcontrol, js, css)
                context_branch['controls'].append(subcontrol)
            
            for c in self.__btn_controls:
                subbtncontrol = {'name': c[0]}
                c[1].publish(subbtncontrol, js, css)
                context_branch['btn_controls'].append(subbtncontrol)
        if self.__context:
            context_branch.update(self.__context)
        context_branch['template'] = self.__controlTemplate


class ControlHtml(ControlBase):

    def __init__(self, html_content, control_template='controls/ControlHtml.html'):
        self.__html_content = html_content
        super().__init__(control_template)

    def add_control(self, name, control):
        assert "unexpected call"

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        context_branch['content'] = self.__html_content

class ControlRecord(ControlBase):
    """"""

    def __init__(self, queryrec, control_fields=None, control_template='controls/ControlRecord.html'):
        self.__queryrec = queryrec
        self.__control_fields = control_fields
        if type(queryrec) != dict:
            assert self.__queryrec.count() <= 1, 'multiple records queried'
        super().__init__(control_template)

    def add_control(self, name, control):
        assert "unexpected call"

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        if self.__control_fields:
            context_branch['content'] = {'order': [], 'fields': {}}
            for field_title, field_name in self.__control_fields:
                if type(self.__queryrec) == dict:
                    value = self.__queryrec.get(field_name)
                else:
                    try:
                        value = getattr(self.__queryrec[0], field_name)
                    except AttributeError as ex:
                        value = None
                context_branch['content']['order'].append({'name': field_name,
                                                           'title': field_title,
                                                           'value': value})
                context_branch['content']['fields'][field_name] = {'title': field_title,
                                                                   'value': value}
        else:
            if type(self.__queryrec) == dict:
                context_branch['content'] = {'order': [], 'fields': {}}
                for k in sorted(self.__queryrec.keys()):
                    context_branch['content']['order'].append({'name': k,
                                                               'title': k,
                                                               'value': self.__queryrec.get(k)})
                    context_branch['content']['fields'][k] = {'title': k,
                                                               'value': self.__queryrec.get(k)}

            else:
                context_branch['content'] = self.__queryrec[0] if self.__queryrec.count() else {}



class ControlInputs(ControlBase):

    def __init__(self, form=None, control_template='controls/ControlInputs.html',classname="",**kwargs):
        self.__form = form
        self.__controls = []
        self.__btn_controls = []
        self.__classname = classname
        self.__kwargs = {
            "toggle":True
        }
        self.__kwargs = self.__kwargs|kwargs
        super().__init__(control_template)
        if form:
            if hasattr(form, 'media'):
                for j in form.media._js:
                    self.need_js(j if j.startswith('/static/') else '/static/' + j)
                for k, v in form.media._css.items():
                    if k != 'all':
                        for s in v:
                            self.need_css(s if s.startswith('/static/') else '/static/' + s)
            for c in self.__controls:
                super().add_control(c[1].__class__.__name__, c[1])
    @property
    def get_form(self):
        return self.__form

    def add_botton_control(self,name,control):
        assert name not in ([c[0]] for c in self.__btn_controls), "duplicate control name"
        self.__btn_controls.append((name, control))

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        context_branch['content'] = self.__form
        context_branch['classname'] = self.__classname
        context_branch['btn_controls'] = []
        for c in self.__btn_controls:
            subbtncontrol = {'name': c[0]}
            c[1].publish(subbtncontrol, js, css)
            context_branch['btn_controls'].append(subbtncontrol)
        context_branch.update(self.__kwargs)


class ControlRecordlist(ControlBase):
    """Global tabbed control with paginated records list with ability to view/edit/create new records"""

    def __init__(self, queryset, fields=[], id_field=None, url_field=None, get="{%%}", target="_self",
                 control_template='controls/ControlRecordList.html',fields_url=[],fields_sort=[],fields_event=[],*args,**kwargs):
        
        self.__records = list(queryset)
        self.__fields = fields
        self.__id_field = id_field
        self.__url_field = url_field
        self.__target = target
        self.__get = get
        self.__subcontrols = []
        self._fields_url = fields_url if fields_url else []
        self._fields_sort = fields_sort if fields_sort else []
        self._fields_event = fields_event if fields_event else []
        self._fields_url = [self._fields_url] if type(self._fields_url) == str else self._fields_url
        self._fields_sort = [self._fields_sort] if type(self._fields_sort) == str else self._fields_sort
        self._fields_event = [self._fields_event] if type(self._fields_event) == str else self._fields_event
        self._kwargs = kwargs
        self._kwargs['type_list'] = kwargs.get('type_list', 'zip')
        super().__init__(control_template)

    def add_control(self, name, control,classname=None):
        assert name not in ([c[0]] for c in self.__subcontrols), "duplicate control name"
        if classname == None:
            classname = name
        self.__subcontrols.append((name, control,classname))
    
    def add_pager(self,name,control,classname=None):
        self.add_control(name,control,classname)

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        context_branch['content'] = []
        context_branch['id_field'] = self.__id_field if self.__id_field else None
        _fields_url = {}
        for item in self._fields_url:
            if type(item)==str:
                _fields_url[item] = item
            elif type(item)==list or type(item)==tuple:
                _fields_url[item[0]] = item[1]
        context_branch['fields_url'] = _fields_url
        context_branch['fields_sort'] = self._fields_sort
        context_branch['fields_event'] = self._fields_event
        list_types = [Integer, String, Boolean, DateTime, Text, Float, Date, ARRAY]
        headers = [ ] if self.__id_field else []
        keys = [ ] if self.__id_field else []
        for f in self.__fields:
            headers.append(f[0])
        for f  in self.__fields:
            keys.append(f[1])
        context_branch['keys'] = keys
        # if 'inside' in self._kwargs:
        #     context_branch['inside'] = bool(self._kwargs.get('inside'))
        # else:
        #     context_branch['inside'] = True
        context_branch['api'] = bool(self._kwargs.get('api', True))
        context_branch['api_get'] = self._kwargs.get('api_get', None)
        if self._kwargs['type_list'] == 'zip':
            context_branch['headers'] = list(zip(headers, keys))
        else:
            context_branch['headers'] = headers
        if len(self.__subcontrols) > 0:
            context_branch['controls'] = []
            for c in self.__subcontrols:
                subcontrol = {'name': c[0],'classname': c[2]}
                c[1].publish(subcontrol, js, css)
                context_branch['controls'].append(subcontrol)
        context_branch['classname'] = str(self._kwargs['classname']) if 'classname' in self._kwargs else None
        context_branch['query'] = self.__records
        for o in self.__records:
            valRow = []
            keyRow = []
            if self.__fields:
                for f in self.__fields:
                    sv = o
                    sv_class = type(sv)
                    if type(f[0]) == str:
                        for v in f[1].split('.'):
                            sv_class = type(getattr(type(sv),v).type) if hasattr(type(sv),v) and hasattr(getattr(type(sv),v),'type') and type(getattr(type(sv),v).type) in list_types else sv_class
                            if type(sv) == dict:
                                sv = sv.get(v)
                            else:
                                sv = getattr(sv, v,None)
                    else:
                        tl = []
                        for lv in f[1]:
                            for v in lv.split('.'):
                                sv_class = type(getattr(type(sv),v).type) if hasattr(type(sv),v) and hasattr(getattr(type(sv),v),'type') and type(getattr(type(sv),v).type) in list_types else sv_class
                                if type(sv) == dict:
                                    if type(sv)!=str:
                                        sv = sv.get(v)
                                        if type(sv)==str:
                                            tl.append(sv)
                                            sv = o
                                    else:
                                        sv = o
                                        sv = sv.get(v)
                                        if type(sv)==str:
                                            tl.append(sv)
                                            sv = o
                                else:
                                    if type(sv)!=str:
                                        sv = getattr(sv, v)
                                        if type(sv)==str:
                                            tl.append(sv)
                                            sv = o
                                    else:
                                        sv = o
                                        sv = getattr(sv, v)
                                        if type(sv)==str:
                                            tl.append(sv)
                                            sv = o
                            try:
                                sv = f[2].join(map(str, tl))
                            except:
                                sv = ' '.join(map(str, tl))
                    try:
                        if sv_class==Date or type(sv) == datetime.date:
                            sv = sv.strftime('%d %b %Yг')
                        elif sv_class==DateTime or type(sv) == datetime.datetime:
                            sv = sv.strftime('%d %b %Yг %H:%M')
                        elif type(sv)==list or type(sv)==tuple:
                            # sv = ', '.join([str(svi) for svi in sv])
                            sv = [str(svi) for svi in sv]
                    except Exception as ex:
                        print(ex)
                    valRow.append(sv)
                    keyRow.append(f[1])
                    # if not self._kwargs.get('only_data'):
                    #     valRow.append(str(sv))
                    #     keyRow.append(str(f[1]))
                    # else:
                    #     valRow.append(sv)
                    #     keyRow.append(f[1])
            else:
                if type(o) == dict:
                    valRow = {}
                    for k in sorted(o.keys()):
                        valRow[k] = o.get(k)
            t = self._kwargs['type_list']
            if t == 'zip':
                zipRow = list(zip(valRow, keyRow))
            elif t == 'dict':
                zipRow = dict(zip(keyRow, valRow))
            elif t == 'list':
                zipRow = valRow
            else:
                zipRow = valRow 
            if type(o) == dict:
                id = o.get(self.__id_field, '') if self.__id_field else ''
            else:
                id = getattr(o, self.__id_field) if self.__id_field else ''

            if type(o) == dict:
                url = (str(o.get(self.__url_field, ''))+'/') if self.__url_field else ''
            else:
                url = (str(getattr(o, self.__url_field))+'/') if self.__url_field else ''
            if self.__get != None:
                flag = self.__get.find('{%%}')
                if flag == -1:
                    url = self.__get+url[:-1]
                else:
                    url = self.__get.replace('{%%}',url[:-1])
            if not self._kwargs.get('only_data'):
                context_branch['content'].append((id, url, zipRow, self.__target))
            else:
                context_branch['content'].append(dict(zip(keys,zipRow)))



class ControlPagerFull(ControlBase):
    """Navigator by pages control"""

    def __init__(self, queryset=None, page_active=0, page_size = 10, total=None,after_filter=None, control_template='controls/ControlPagerFull.html'):
        if total:
            self.__total = total
        else:
            self.__total = queryset.count() if type(queryset) != tuple and type(queryset) != list else len(queryset)
        if after_filter:
            self.__after_filter = after_filter
        else:
            self.__after_filter = 0
        self.__page_active = page_active
        self.__page_size = page_size
        super().__init__(control_template)

    def add_control(self, name, control):
        assert "unexpected call"

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        context_branch['content'] = {}
        context_branch['content']['total'] = self.__total
        context_branch['content']['after_filter'] = self.__after_filter
        if self.__after_filter in [11, 12, 13, 14] or self.__total==0:
            text = 'записей'
        else:
            for_text = int(str(self.__after_filter)[-1])
            if for_text in [5, 6, 7, 8, 9, 0]:
                text = 'записей'
            elif for_text in [2, 3, 4]:
                text = 'записи'
            else:
                text = 'запись'
        context_branch['content']['text'] = text
        p = range(0, math.ceil(self.__after_filter / self.__page_size))
        if len(p) > 1:
            if len(p) > 7:
                if self.__page_active < 4:
                    start = 0
                    finish = 6
                    context_branch['content']['last_item'] = {'url': '?p=' + str(len(p)-1),
                                                              'p':str(len(p)-1),
                                                              'active': '1' if len(p)-1 == self.__page_active else '',
                                                              'title': str(len(p))}
                elif self.__page_active > len(p) - 4:
                    start = len(p) - 6
                    finish = len(p)
                    context_branch['content']['first_item'] = {'url': '?p=' + str(0),
                                                               'p':str(0),
                                                               'active': '1' if 0 == self.__page_active else '',
                                                               'title': str(1)}
                else:
                    start = self.__page_active - 2
                    finish = self.__page_active + 3
                    context_branch['content']['last_item'] = {'url': '?p=' + str(len(p)-1),
                                                              'p':str(len(p)-1),
                                                              'active': '1' if len(p)-1 == self.__page_active else '',
                                                              'title': str(len(p)) }
                    context_branch['content']['first_item'] = {'url': '?p=' + str(0),
                                                               'p':str(0),
                                                               'active': '1' if 0 == self.__page_active else '',
                                                               'title': str(1)}

            else:
                start = 0
                finish = len(p)
            context_branch['content']['pages'] = []
            for i in range(start, finish):
                url = '?p=' + str(i)
                active = '1' if i == self.__page_active else ''
                context_branch['content']['pages'].append({'url': url,'p':str(i), 'active': active, 'title': str(i + 1)})



class ControlForm(ControlBase):
    """Default form control"""
    def __init__(self, action="", method="POST", control_template='controls/ControlForm.html',is_multipart=False):
        self.__action = action
        self.__method = method
        self.__is_multipart = is_multipart
        super().__init__(control_template)

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        context_branch['action'] = self.__action
        context_branch['method'] = self.__method

        context_branch['is_multipart'] = self.__is_multipart

class ControlButtonsBar(ControlBase):
    """line of buttons like toolbar control"""

    def __init__(self, control_template='controls/ControlButtonsBar.html'):
        self.__counter = 0
        self.__subcontrols = []
        super().__init__(control_template)

    def add_control(self, name, control, classname=None):
        super().add_control(name, control, classname)
        # assert name not in ([c[0]] for c in self.__subcontrols), "duplicate control name"
        # if classname == None:
        #     classname = name
        # self.__subcontrols.append((name, control,classname))

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        if len(self.__subcontrols) > 0:
            context_branch['controls'] = []
            for c in self.__subcontrols:
                subcontrol = {'name': c[0],'classname': c[2]}
                c[1].publish(subcontrol, js, css)
                context_branch['controls'].append(subcontrol)

    def add_button(self, title,btn_type='Default', redirect_url=None, js_action=None, submit_name=None,
                   control_template='controls/ControlButton.html', **kwargs):
        super().add_control('cmd_' + str(self.__counter), ControlButton(title,btn_type, redirect_url, js_action, submit_name,
                                                                        control_template=control_template,**kwargs))
        self.__counter += 1

class ControlButton(ControlBase):

    def __init__(self, title,btn_type=None, redirect_url=None, js_action=None, submit_name=None,
                 control_template='controls/ControlButton.html',**kwargs):
        self.__title = title
        self.__btn_type = btn_type if btn_type else 'Simple'
        self.__type = 'redirect' if redirect_url != None else ('js' if js_action != None else 'submit')
        self.__action = redirect_url if redirect_url != None else (js_action if js_action != None else (submit_name if submit_name != None else ''))
        self.__is_admin = True if kwargs.get('is_admin') else False
        super().__init__(control_template)

    def add_control(self, name, control):
        assert "unexpected call"

    def publish(self, context_branch, js, css):
        super().publish(context_branch, js, css)
        if self.__btn_type:
            if self.__btn_type[0:12] != 'Button':
                self.__btn_type='Button' + self.__btn_type
        context_branch['btn_type'] = self.__btn_type
        context_branch['title'] = self.__title
        context_branch['type'] = self.__type
        context_branch['action'] = self.__action
        context_branch['is_admin'] = self.__is_admin

class ControlExeption(ControlBase):
    def __init__(self,exception=None,control_template=f'controls/catch/Exeption.html',content={}):
        super().__init__()
        self.exception = exception
        self.is_exception = False
        self.control_template = control_template
        self.content = content
        self.catch_list= [
            'ChunkedEncodingError',
            'ConnectionError'
        ]
        self.classname = 'NullExeption'
        if exception:
            classname = type(exception).__name__
            self.classname = classname
            if classname in self.catch_list and self.control_template == f'controls/catch/Exeption.html':
                self.control_template = f'controls/catch/{classname}.html'
            self.control = ControlHtml(content, self.control_template)
            self.is_exception = True
        else:
            self.control = ControlHtml(content, self.control_template)
            self.is_exception = False
        self.template = self.control_template
        self.add_control(self.classname,self.control)
        
    def TemplateToString(self,template=None):
        return render_to_string(template if template else self.control_template, context={'control':{'content':self.content}} if type(self.content)==dict else {'control':{'content':{}}})