import collections
import datetime
from django import http, template
from sqlalchemy.sql.expression      import false,desc
import json
import re
import math
import os
import string
import pathlib
from sqlalchemy                     import Integer, String, Boolean, DateTime, Text, Float, Date, ARRAY, not_, func, case
from dateutil import parser

from parentify.methods import FileInformation, getattrkey
register = template.Library()

@register.filter
def is_favorite(goods, user_id):
    """
    Template filter для проверки, находится ли товар в избранном у пользователя
    """
    if not goods or not user_id:
        return False
    
    return goods.is_favorite(user_id)









@register.filter
def plus(value, arg):
    return value + arg

@register.filter
def minus(value, arg):
    return value - arg

@register.filter
def multiply(value, arg):
    return value * arg

@register.filter
def division(value, arg):
    if arg == 0:
        return 0
    return value / arg

def parse_date(s,**kwargs):
    try:
        return parser.parse(s,**kwargs)
    except:
        return s

@register.filter
def startswith(text, starts):
    return str(text).startswith(starts)

@register.filter
def endswith(text, ends):
    return str(text).endswith(ends)

@register.filter
def get_user(request):
    return request.current_user

@register.filter
def is_user_admin(request):
    user = request.current_user
    if user:
        return user.is_admin
    else:
        return False

@register.filter
def to_dict(instance):
    return instance.__dict__

@register.filter
def to_list(instance):
    if type(instance)==list or type(instance)==tuple:
        return instance
    else:
        return [instance]

@register.filter
def index(instance, i):
    return instance[i]

@register.simple_tag()
def index_key(instance, i,s):
    el = instance[i]
    if type(el)==dict:
        return el[s]
    else:
        return getattr(el,s)

@register.filter
def is_list(instance):
    if type(instance)==list or type(instance)==tuple:
        return True
    else:
        return False

@register.filter
def first_item_dict(instance):
    if type(instance)==dict:
        return [instance]
    elif type(instance)==list:
        return [instance[0]]
    else:
        return instance

@register.filter
def to_str(instance):
    return str(instance)

@register.filter
def calc(instance,math_str):
    instance = str(instance)
    
    return str(eval(math_str.replace('$',instance)))

@register.filter
def log(instance):
    print(instance)
    print(instance.__dict__)
    return instance

@register.filter
def attr(obj,key):
    try:
        key = str(key)
        el_attr = getattrkey(obj,key)
        if el_attr==None:
            el_attr = obj
            for k in key.split('.'):
                el_attr = getattrkey(el_attr,k)
        return el_attr
    except:
        return None

@register.filter
def attr_str(obj,key):
    try:
        key = str(key)
        el_attr = getattrkey(obj,key)
        if el_attr==None:
            el_attr = obj
            for k in key.split('.'):
                el_attr = getattrkey(el_attr,k)
        return str(el_attr)
    except:
        return None

@register.filter
def split(s, delim):
    return str(s).split(delim)

    
@register.filter
def to_json(object):
    try:
        data = json.dumps(object)
        return data
    except:
        return object

@register.filter
def from_json(object):
    try:
        data = json.loads(object)
        return data
    except:
        return object

@register.filter
def str_to_dict_and_get(object, key):
    try:
        data = json.loads(object) if not isinstance(object,dict) else object
        return data.get(key)
    except Exception as ex:
        return None

@register.filter
def is_str_dict(object):
    try:
        if isinstance(object,(dict, list)):
            return True
        data = json.loads(object)
        return True
    except Exception as ex:
        return False

@register.filter
def lookup(d, key):
    return d[key]

@register.filter
def get_type(d):
    return type(d)

@register.filter
def get_type_str(d):
    return str(type(d))

@register.filter
def get_classname(d):
    return str(type(d).__name__)

@register.filter
def find_in_arr(array, key):
    key = str(key)
    for item in array:
        if type(item)==list or type(item)==tuple:
            if item[0]==key:
                return item
        else:
            if item==key:
                return item
    return None

@register.filter
def find_in_str(d, s):
    return d.find(s) >= 0

@register.filter
def has_in_arr(array, value):
    return value in array


@register.filter
def countarr(d, key):
    full_text = ''
    count = 0
    for item in d[key]:
        full_text+=item
    count = full_text.count('}')
    return count

@register.filter 
def converterstrtolist(d,key):
    lister = []
    if d[key] != None:
        s = str(d[key])
        reg = re.findall("'(.+?)'", s)
        if reg:
            for i in range(0,len(reg),1):
                if i%2 != 0:
                    lister.append(reg[i].encode('utf8'))
    return lister

@register.filter
def count(d):
    res = list(d)
    return len(res)

@register.filter 
def is_absolute_url(d):
    start = d[:4]
    is_absolute = False
    if start == 'http': 
        is_absolute = True
    else: 
        is_absolute = False
    return is_absolute

@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False

@register.filter('startswith')
def endswith(text, starts):
    if isinstance(text, str):
        return text.endswith(starts)
    return False

@register.filter 
def get_month(d):
    return d.month

@register.filter
def get_year(d):
    return d.year

@register.filter
def str_to_num(str):
    if type(str)==int or type(str)==float or str==None:
        return str
    if "." in str and not str.endswith('.0'):
        try:
            res = float(str)
        except:
            res = str
    elif str.isdigit() or str.endswith('.0'):
        try:
            res = int(float(str))
        except:
            res = str
    else:
        res = str
    return res

@register.filter
def strfloatformat(n):
    if not n:
        return n
    n = str(n).replace(',','.')
    return n

@register.filter
def date_parse(date_time):
    try:
        if type(date_time) == str:
            date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S.%f') 
            date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
    except:
        try:
            date_time = datetime.datetime.strptime(date_time, '%Y-%m-%d %H:%M:%S') 
            date_time = date_time.strftime('%Y-%m-%d %H:%M:%S')
        except:
            pass
    return date_time

@register.filter
def date_parse_to_datetime(date_str):
    if date_str:
        return parse_date(date_str, dayfirst=True)
    else:
        return None
    


@register.filter
def rem_of_div(num1,num2):
    num1 = int(num1)
    num2 = int(num2)
    if num1 == 0 or num2 == 0:
        return 0
    s = num1%num2
    return s

@register.filter
def formatBytes(bytes):
    decimals = 2
    if bytes == 0:
        return '0 байт'
    k = 1024
    dm = 0 if decimals < 0 else decimals
    sizes = ['байт', 'КБ', 'МБ', 'ГБ', 'ТБ', 'ПТ', 'ЕБ', 'ЗБ', 'ЮБ']
    i = math.floor(math.log(bytes) / math.log(k))
    return f"{float(bytes / math.pow(k, i)):.{dm}f}" + ' ' + sizes[i]


@register.filter
def startswith(text, starts):
    return text.startswith(starts)


@register.filter
def get_file_category(path):
    file_t = pathlib.Path(path).suffix
    if file_t in FileInformation.pdf_extensions:
        return 'pdf'
    elif file_t in FileInformation.image_extensions:
        return 'image'
    elif file_t in FileInformation.video_extensions:
        return 'video'
    elif file_t in FileInformation.audio_extensions:
        return 'audio'
    return 'default'

@register.filter
def get_filename(url_or_path):
    return os.path.basename(url_or_path)
