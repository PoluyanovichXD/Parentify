from datetime import timedelta
from io import BytesIO
import json
import re
import sys
import phonenumbers
from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import gettext as _
from django.core.files.uploadedfile import InMemoryUploadedFile

from parentify.methods import parse_date
from parentify.ui.widgets import *

def kwargs_init(**kwargs):
    attrs_init = ['max_length','min_length','strip','empty_value','required','widget','label','initial','help_text','error_messages','show_hidden_initial','validators','localize','disabled','label_suffix']
    return {key:value for key, value in kwargs.items() if key in attrs_init}

class TextInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.widget = TextInputWidget(attrs={'type': 'text','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply}|kwargs)
        
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = value if value and not str(value).isspace() else None
            else:
                value = [item for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
class EmailInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,validation=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.validation = validation
        self.widget = TextInputWidget(attrs={'type': 'text','label':self.label})
        self.widget.template_name='widgets/EmailInput.html'

    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.email_validation(value) if value and not str(value).isspace() else None
            else:
                value = [self.email_validation(item) for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
    def email_validation(self, value):
        if not self.validation:
            return value
        if not value:
            return value
        regex = re.compile(r"^[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[A-Za-z0-9!#$%&'*+/=?^_`{|}~-]+)*@(?:[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?\.)+[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$")
        if re.fullmatch(regex,value):
            return value
        else:
            raise ValidationError(_('Не верно указан Email'))
class PhoneInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.widget = PhoneInputWidget(attrs={'type': 'phone','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply}|kwargs)
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.phone_validation(value) if value and not str(value).isspace() else None
            else:
                value = [self.phone_validation(item) for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
    def phone_validation(self, value):
        if not value or value == '':
            return value
        number = value
        try:
            number = phonenumbers.parse(value)
        except phonenumbers.NumberParseException as ex:
            if ex.error_type == ex.INVALID_COUNTRY_CODE:
                raise ValidationError(_('Не верно указан код страны'))
            elif ex.error_type == ex.NOT_A_NUMBER:
                raise ValidationError(_('В поле "Номер телефона" введены некорректные символы'))
            elif ex.error_type == ex.TOO_LONG:
                raise ValidationError(_('Данный номер превышает значимую длину'))
            elif ex.error_type == ex.TOO_SHORT_AFTER_IDD:
                raise ValidationError(_('Данный номер некорректный для IDD'))
        try:
            if phonenumbers.is_valid_number(number):
                return value
            else:
                raise ValidationError(_('Не верно указан номер телефона'))
        except:
            raise ValidationError(_('Не верно указан номер телефона'))
class PasswordInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,password_len=None,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.password_len = password_len
        self.widget = TextInputWidget(attrs={'type': 'text','label':self.label})
        self.widget.template_name='widgets/PasswordInput.html'


    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.password_validation(value) if value and not str(value).isspace() else None
            else:
                value = [self.password_validation(item) for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
    def password_validation(self, value):
        if not value or value == '':
            return value
        if self.password_len==None or len(value)>=self.password_len:
            return value
        else:
            raise ValidationError(_(f'Количество символов в поле {self.label} должно быть не меньше {self.password_len}'))
class CoordinatesInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.widget = TextInputWidget(attrs={'type': 'text','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply}|kwargs)
        self.widget.template_name='widgets/CoordinatesInput.html'
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def coord_validation(self,value):
        has_validate = re.match('^(\-?\d+\.\d+),(\-?\d+\.\d+)$', value)
        if has_validate:
            return value
        else:
            raise ValidationError(_('Не верно указаны координаты!'))
    
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.coord_validation(value) if value and not str(value).isspace() else None
            else:
                value = [self.coord_validation(item) for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
class TextAreaInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.widget = TextInputWidget(attrs={'type': 'text','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply}|kwargs)
        self.widget.template_name='widgets/TextareaInput.html'
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = value if value and not str(value).isspace() else None
            else:
                value = [item for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
class NumberInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,min=None,max=None,step="1",*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self.step = step
        self._multiply = multiply
        self.widget = NumberInputWidget(attrs={'type': 'number','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply,'min':min,'max':max,'step':step}|kwargs)
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
    
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.res_number(value) if value and not str(value).isspace() else None
            else:
                value = [self.res_number(item) for item in list(filter(lambda x:x and not str(x).isspace(),value))]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
    def res_number(self,data_el):
        if type(data_el) == str:
            data_el = data_el.replace(',','.')
            if data_el.isnumeric():
                return int(data_el)
            elif data_el.replace(".", "").isnumeric():
                return float(data_el)
            else:
                return None
        else:
            return data_el
class DateInputField(forms.DateField):
    def __init__(self,multiply=False,validator=False,visible_text=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.widget = DateInputWidget(attrs={'type': 'text','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply}|kwargs)
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.set_date(value) if  value and not str(value).isspace() else None
            else:
                value = [self.set_date(item) for item in list(filter(lambda x:x and not str(x).isspace(),value)) if self.set_date(item) != None]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Неверный формат даты. Требуется:dd-mm-yyyy'))
    def set_date(self,value):
        date = parse_date(value, dayfirst=True) if value else None
        if date:
            date = date + timedelta(hours=23,minutes=59,seconds=59)
        return date
    
class DateTimeInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.widget = DatetimeInputWidget(attrs={'type': 'text','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply}|kwargs)
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            if not self.multiply:
                value = value[0]
                value = self.set_date(value) if value and not str(value).isspace() else None
            else:
                value = [self.set_date(item) for item in list(filter(lambda x:x and not str(x).isspace(),value)) if self.set_date(item) != None]
                value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Неверный формат даты. Требуется:dd-mm-yyyy HH:MM'))
    def set_date(self, value):
        date = parse_date(value, dayfirst=True) if value else None
        return date
class CheckboxField(forms.BooleanField):
    def __init__(self,required=False,label=None,str_bool=False,**kwargs):
        super().__init__(required=required, label=label,**kwargs_init(**kwargs))
        self.widget = CheckboxWidget(attrs={'type': 'checkbox','label':self.label}|kwargs)
    def to_python(self, value):
        try:
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None

class SwitchField(forms.BooleanField):
    def __init__(self,required=False,label=None,true_title=None,false_title=None,visible_text=True,initial=None,switch_select=False,onchange=None,**kwargs):
        super().__init__(required=required, label=label,**kwargs_init(**kwargs))
        self.widget = SwitchWidget(attrs={'type': 'checkbox','label':self.label,'true_title':true_title,'false_title':false_title,'visible_text':visible_text,'switch_select':switch_select,'onchange':onchange}|kwargs)
    def to_python(self, value):
        try:
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
class SelectInputField(forms.CharField):
    def __init__(self,multiply=False,validator=False,visible_text=True,choices = [], disabled=False,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self._multiply = multiply
        self.choices = choices
        self.widget = SelectWidget(attrs={'type': 'select','label':self.label,'visible_text':visible_text,'validator':validator,'multiply':multiply,'choices':choices, 'disabled':disabled}|kwargs)
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    @property
    def choices(self):
        return self._choices
    
    @choices.setter
    def choices(self, value):
        self.widget.choices = value
        self._choices = value
    
    def to_python(self, value):
        try:
            if not value or str(value).isspace(): return None
            value = value if type(value) == list or type(value) == tuple else [value]
            if not self.multiply:
                value = value[0]
                for ch in self.choices:
                    if str(value) == str(ch[0]):
                        return ch[0]
                    elif type(ch[1])==list or type(ch[1])==tuple:
                        for cp in ch[1]:
                            if str(value) == str(cp[0]):
                                return cp[0]
            else:
                # value_list = []
                # value = [item for item in list(filter(lambda x:x!='',value))]
                # for val in value:
                #     for ch in self.choices:
                #         if str(val) == str(ch[0]):
                #             value_list.append(val)
                #             break
                value_list = [item for item in list(filter(lambda x:bool(x),value))]
                return value_list if value_list else None
            return None
        except Exception as e:
            print(e)
            raise ValidationError(_('Некорректный выбор'))
        

class FileField(forms.FileField):
    def __init__(self,label=None,accept=[],multiply=False,max_files=None,max_file_size=None,upload_to=None,images_type=False,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        if type(accept)==str:
            accept = [accept]
        if images_type:
            accept = accept+['.tiff','.jfif','.bmp','.gif','.svg','.png','.jpeg','.svgz','.jpg','.webp','.ico','.xbm','.dib','.pip','.apng','.tif','.pjpeg','.avif']
        self.accept = accept
        self._multiply = multiply
        upload_url = None
        self.label = label
        if upload_to:
            upload_url=f'/images/upload/{upload_to}/'
        self.filepond_id = id_generator(size=32)
        self.widget = FileInputWidget(attrs={'type': 'file','label':self.label,'accept':accept,'max_files':max_files,'max_file_size':max_file_size,'upload_to':upload_to,'upload_url':upload_url,'filepond_id': self.filepond_id,'multiply':multiply}|kwargs)
        self.widget
    @property
    def multiply(self):
        return self._multiply
    @multiply.setter
    def multiply(self, value):
        self.widget.attrs['multiply']= value
        self._multiply = value
    @property
    def label(self):
        return self._label
    
    @label.setter
    def label(self, value):
        self.widget.label = value
        self._label = value
    def to_python(self,value):
        try:
            if value:
                if type(value) == str:
                    jsonFiles = json.loads(value)
                    value = []
                    for item in jsonFiles:
                        item = json.loads(item) if type(item) == str else item
                        with open(item['path'], "rb") as f:
                            item['file'] = BytesIO(f.read())
                        file = InMemoryUploadedFile(
                            file=item['file'],
                            field_name=item['field_name'],
                            name=item['name'],
                            content_type=item['content_type'],
                            size=item['size'],
                            charset=item['charset'],
                            content_type_extra=item['content_type_extra']
                        )
                        setattr(file,'path',item['path'])
                        setattr(file,'upload_path',item['upload_path'])
                        setattr(file,'url',item['url'])
                        value.append(file)
                if self.accept:
                    for file in value:
                        file_valid = False
                        for accep in self.accept:
                            file_format = file.name[-len(accep):]
                            if file_format.lower() == accep.lower():
                                file_valid = True
                                break
                        if not file_valid:
                            raise ValidationError(_('Неверный формат файла'))
                
                if not self.multiply and type(value) == list:
                    if not hasattr(value[0],'read'):
                        raise ValidationError(_('Файл не был загружен'))
                    return value[0]
                if [v for v in value if not hasattr(v,'read')]:
                    raise ValidationError(_('Файлы не были загружены'))
                return value
            else:
                return None
        except Exception as ex:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            print(ex)
            print(exc_type, fname, exc_tb.tb_lineno)
            print('###'*5)
            raise ValidationError(_('Выберите файл'))

class HtmlEditorField(forms.CharField):
    def __init__(self,label=None,*args, **kwargs):
        super().__init__(*args,**kwargs)
        self.widget = HtmlEditorWidget(attrs={'type':'text','label':label}|kwargs)
    
    def to_python(self,value):
        try:
            if value and not value == "<p><br></p>" :
                return value
            else:
                return ''
        except ValueError:
            raise ValidationError(_('Заполните форму'))




class RangeInputField(forms.IntegerField):
    def __init__(self,min=None,max=None,step="1",*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self.step = step
        self.widget = RangeInputWidget(attrs={'type': 'number','label':self.label,'step':step,'min':min,'max':max}|kwargs)

    def to_python(self, value):
        try:
            value = [self.res_number(item) for item in list(filter(lambda x:x and not str(x).isspace(),value))]
            value = value if value else None
            return value
        except ValueError:
            raise ValidationError(_('Некорректный ввод'))
        return None
    
    def res_number(self,data_el):
        if type(data_el) == str:
            data_el = data_el.replace(',','.')
            if data_el.isnumeric():
                return int(data_el)
            elif data_el.replace(".", "").isnumeric():
                return float(data_el)
            else:
                return None
        else:
            return data_el
        


class DateRangeField(forms.DateField):
    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self.widget = DateRangeWidget(attrs={'type': 'date','label':self.label}|kwargs)

    def to_python(self, value):
        try:
            # if isinstance(value[0], (int, float)):
            #     start = datetime.datetime.fromtimestamp(float(value[0]))
            # else:
            #     start = parse_date(value[0], dayfirst=True) if value[0] else None
            # if isinstance(value[1], (int, float)):
            #     finish = datetime.datetime.fromtimestamp(float(value[1]))
            # else:
            #     finish = parse_date(value[1], dayfirst=True) if value[1] else None
            start = parse_date(value[0], dayfirst=True) if value[0] else None
            finish = parse_date(value[1], dayfirst=True) if value[1] else None
            if start and finish and start > finish:
                raise ValidationError(_('Неверный временной промежуток'))
            if finish:
                finish = finish + timedelta(hours=23,minutes=59,seconds=59)
            return (start, finish)
        except ValueError:
            raise ValidationError(_('Неверный формат даты. Требуется:dd-mm-yyyy'))
        return (None, None)

class DatetimeRangeField(forms.DateField):
    def __init__(self,*args, **kwargs):
        super().__init__(*args,**kwargs_init(**kwargs))
        self.widget = DatetimeRangeWidget(attrs={'type': 'date','label':self.label}|kwargs)

    def to_python(self, value):
        try:
            start = parse_date(value[0], dayfirst=True) if value[0] else None
            finish = parse_date(value[1], dayfirst=True) if value[1] else None
            if start and finish and start > finish:
                raise ValidationError(_('Неверный временной промежуток'))
            if finish:
                finish = finish + timedelta(hours=23,minutes=59,seconds=59)
            return (start, finish)
        except ValueError:
            raise ValidationError(_('Неверный формат даты. Требуется:dd-mm-yyyy HH:MM'))
        return (None, None)
