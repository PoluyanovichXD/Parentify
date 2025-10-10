
import json
import random
import string
from django.forms            import Widget
from django.http import QueryDict
from django.utils.safestring import mark_safe
from django.template.loader  import render_to_string
from django   import forms
import datetime
from django.urls import reverse
import os
from django.core.files.storage import default_storage

def id_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))
def toQueryDict(data):
    query_data = QueryDict('', mutable=True)
    query_data.update(data)
    return query_data

class WidgetBase(Widget):
    class Media:
        css = {
            'all': (
                
            )
        }
        js = (
            
        )
    
    
    def render(self, name, value, attrs=None, renderer=None,**kwargs):
        if value == None:
            value = ""
        context = {
            'name': name,
            'value': value,
            'attrs': attrs,
            'w': self,
        }
        if kwargs:
            for key, val in kwargs.items():
                if not context.get(key):
                    context[key] = val
        return mark_safe(render_to_string(self.template_name, context))

class TextInputWidget(WidgetBase):
    template_name = 'widgets/TextInput.html'
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = ['']
        else:
            if type(value) != list:
                value = [value]
        return super().render(name, value, attrs)
    
class PhoneInputWidget(WidgetBase):
    template_name = 'widgets/PhoneInput.html'
    class Media:
        js = (
            '/static/intl-tel-input/intlTelInput.min.js',
        )
        css = {
            'screen': (
                '/static/intl-tel-input/intlTelInput.css',
            )
        }
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = ['']
        else:
            if type(value) != list:
                value = [value]
        return super().render(name, value, attrs)

class NumberInputWidget(WidgetBase):
    template_name = 'widgets/NumberInput.html'
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = ['']
        else:
            if type(value) != list:
                value = [str(value)]
            else:
                value = [str(val) for val in value]
        return super().render(name, value, attrs)
class RangeInputWidget(WidgetBase):
    template_name = 'widgets/RangeInput.html'
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = ['']
        else:
            if type(value) != list:
                value = [value]
        return super().render(name, value, attrs)

class DateInputWidget(WidgetBase):
    template_name = 'widgets/DateInput.html'
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []
        

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = ['']
        else:
            if type(value) != list and type(value) != tuple:
                value = [value]
            for index, val in enumerate(value):
                if type(val) == datetime.datetime:
                    value[index] = val.strftime("%d-%m-%Y %H:%M:%S")
                elif type(val) == datetime.date:
                    value[index] = datetime.datetime.combine(val, datetime.datetime.min.time()).strftime("%d-%m-%Y")
                else:
                    value[index] = val
        return super().render(name, value, attrs)
class DatetimeInputWidget(WidgetBase):
    template_name = 'widgets/DatetimeInput.html'
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []
        
    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = ['']
        else:
            if type(value) != list and type(value) != tuple:
                value = [value]
            for index, val in enumerate(value):
                if type(val) == datetime.datetime:
                    value[index] = val.strftime("%d-%m-%Y %H:%M:%S")
                elif type(val) == datetime.date:
                    value[index] = datetime.datetime.combine(val, datetime.datetime.min.time()).strftime("%d-%m-%Y")
                else:
                    value[index] = val
        return super().render(name, value, attrs)
class SelectWidget(WidgetBase):
    template_name = 'widgets/SelectInput.html'
    def value_from_datadict(self, data, files, name):
        data = toQueryDict(data)
        if data.getlist(name):
            return data.getlist(name)
        else:
            return []
        
    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if value or value==False:
            if type(value) != list:
                value = [value]
            else:
                # Кастылёчек для фильтра:3
                try:
                    if len(value)==1 and type(value[0]) == list:
                        value = value[0]
                except:
                    pass
        else:
            value = ['']
        
        attrs['choices'] = self.choices if hasattr(self,'choices') else []
        return super().render(name, value, attrs)
class CheckboxWidget(WidgetBase):
    template_name = 'widgets/CheckboxInput.html'

    def format_value(self, value):
        if value is True or value is False or value is None or value == "":
            return
        return str(value)

    def value_from_datadict(self, data, files, name):
        if name not in data:
            return False
        value = data.get(name)
        values = {"True": True, "False": False}
        if isinstance(value, str):
            value = values.get(value.lower(), value)
        return bool(value)

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = False
        else:
            value = value
        return super().render(name, value, attrs)
    
    def get_context(self, name, value, attrs):
        if self.check_test(value):
            attrs = {**(attrs or {}), "checked": True}
        return super().get_context(name, value, attrs)

class SwitchWidget(WidgetBase):
    template_name = 'widgets/SwitchInput.html'

    def format_value(self, value):
        if value is True or value is False or value is None or value == "":
            return
        return str(value)

    def value_from_datadict(self, data, files, name):
        if name not in data:
            return False
        value = data.get(name)
        values = {"True": True, "False": False}
        if isinstance(value, str):
            value = values.get(value.lower(), value)
        return bool(value)

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = False
        else:
            value = value
        return super().render(name, value, attrs)
    
    def get_context(self, name, value, attrs):
        if self.check_test(value):
            attrs = {**(attrs or {}), "checked": True}
        return super().get_context(name, value, attrs)
class DateRangeWidget(WidgetBase):
    template_name = 'widgets/DateRangeInput.html'
    
    def value_from_datadict(self, data, files, name):
        return (data.get(name + '_start'), data.get(name + '_finish'))

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = zip([''],[''])
        elif not any(value):
            value = zip([''],[''])
        else:
            valList = lambda l, i: (l[i] if l and len(l)>i and (type(l[i])==list or type(l[i])==tuple) else [l[i]] 
            if l and len(l)>i and (type(l[i])!=list and type(l[i])!=tuple) else [None])
            for index, val in enumerate(value):
                if type(val) == datetime.datetime:
                    value[index] = val.strftime("%d-%m-%Y %H:%M:%S")
                elif type(val) == datetime.date:
                    value[index] = datetime.datetime.combine(val, datetime.datetime.min.time()).strftime("%d-%m-%Y")
                else:
                    value[index] = val
            value = zip(
                valList(value,0),
                valList(value,1)
            )
        return super().render(name, value, attrs,self)
class DatetimeRangeWidget(WidgetBase):
    template_name = 'widgets/DatetimeRangeInput.html'
    
    def value_from_datadict(self, data, files, name):
        return (data.get(name + '_start'), data.get(name + '_finish'))

    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = zip([''],[''])
        elif not any(value):
            value = zip([''],[''])
        else:
            valList = lambda l, i: (l[i] if l and len(l)>i and (type(l[i])==list or type(l[i])==tuple) else [l[i]] 
            if l and len(l)>i and (type(l[i])!=list and type(l[i])!=tuple) else [None])
            value = zip(
                valList(value,0),
                valList(value,1)
            )
        return super().render(name, value, attrs,self)
class NumberRangeWidget(WidgetBase):
    template_name = 'widgets/NumberRangeInput.html'
    def value_from_datadict(self, data, files, name):
        return (data.get(name + '_min'), data.get(name + '_max'))
    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if not value:
            value = zip([''],[''])
        elif not any(value):
            value = zip([''],[''])
        else:
            valList = lambda l, i: (l[i] if l and len(l)>i and (type(l[i])==list or type(l[i])==tuple) else [l[i]] 
            if l and len(l)>i and (type(l[i])!=list and type(l[i])!=tuple) else [None])
            value = zip(
                valList(value,0),
                valList(value,1)
            )
        return super().render(name, value, attrs,self)
class HtmlEditorWidget(WidgetBase):
    template_name = "widgets/HtmlEditor.html"

    # class Media:
    #     css = {
    #         'screen': (
    #             "katex/katex.min.css",
    #             "suneditor/suneditor.min.css",
    #         )
    #     }
    #     js = [
    #         "katex/katex.min.js",
    #         "suneditor/suneditor.min.js",
    #         "suneditor/lang_ru.js",
    #     ]
    #     js += ["/static/js/widgets/html_editor.js"]
    def value_from_datadict(self, data, files, name):
        if data.get(name):
            return data.get(name)
        else:
            return None
    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        return super().render(name, value, attrs, self)
    
class FileInputWidget(WidgetBase):
    template_name = 'widgets/FileInput.html'
    def value_from_datadict(self, data, files, name):
        if files.getlist(name):
            return files.getlist(name)
        eldata = toQueryDict(data)
        try:
            if not hasattr(data, 'getlist'):
                data = eldata
            if data.getlist(name):
                if data.get(name)=='':
                    return []
                dataJson = json.loads(data.get(name))
                if type(dataJson) == list:
                    return data.get(name)
                else:
                    return json.dumps(data.getlist(name))
            else:
                return []
        except:
            return []
    def render(self, name, value, attrs=None, renderer=None):
        if hasattr(self,'value'):
            value = getattr(self,'value')
        if type(value)==str:
            try:
                value = json.loads(value)
            except:
                pass
        if not value:
            value = []
        else:
            if type(value) != list:
                value = [value]
        return super().render(name, value, attrs,self)