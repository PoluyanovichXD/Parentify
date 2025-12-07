from django import forms
from django.http import HttpResponseRedirect
from sqlalchemy.sql import text, func
from sqlalchemy.sql.expression import literal_column




# def choise_name_orm(request, ClassModel, all=False, name_field=None):
#     choise = [(None, ''), ]
#     if not name_field:
#         name_field = ClassModel.name
#     if all:
#         choise.extend(request.orm_session.query(text(ClassModel.url_key_name), name_field).order_by(name_field).all())
#     else:
#         if hasattr(ClassModel, 'approved'):
#             choise.extend(request.orm_session.query(text(ClassModel.url_key_name), name_field).filter(ClassModel.approved == True).order_by(name_field).all())
#         else:
#             choise.extend(request.orm_session.query(text(ClassModel.url_key_name), name_field).order_by(name_field).all())
#     return choise

def choise_name_orm(request, ClassModel, all=False, name_field=None):
    choise = [(None, ''), ]
    
    if not name_field:
        name_field = 'name'
    
    id_field = getattr(ClassModel, 'url_key_name', 'id')
    
    if isinstance(name_field, (list, tuple)):
        if len(name_field) == 1:
            display_expr = getattr(ClassModel, name_field[0])
        else:
            concat_parts = []
            for i, field in enumerate(name_field):
                if i > 0:
                    concat_parts.append(literal_column("' '"))
                concat_parts.append(getattr(ClassModel, field))
            
            display_expr = func.concat(*concat_parts)
    elif isinstance(name_field, str):
        display_expr = getattr(ClassModel, name_field)
    else:
        display_expr = name_field
    
    query = request.orm_session.query(
        getattr(ClassModel, id_field),
        display_expr
    ).order_by(display_expr)
    
    if not all and hasattr(ClassModel, 'approved'):
        query = query.filter(ClassModel.approved == True)
    
    results = query.all()
    choise.extend(results)
    
    return choise

class FormCore(forms.Form):
    _errors = None
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # for key in self.fields.keys():
        #     try:
        #         if isinstance(self.fields[key],instance_multifields):
        #             self.fields[key].form = self
        #     except:
        #         continue

class FormBase(FormCore):
    def __init__(self, request, init_data={}, current_data=None, **kwargs):
        self.request = request
        if request.method == 'POST':
            super().__init__(request.POST, request.FILES, initial=init_data)
        elif current_data:
            super().__init__(current_data, initial=init_data)
        else:
            super().__init__(initial=init_data)

class PermanentForm(FormBase):

    def __init__(self, request, storage_name, discard_on_execute=False, init_data={}, **kwargs):
        self.discard_on_execute = discard_on_execute
        self._storage_key = 'form_storage_' + storage_name
        if self._storage_key in request.session:
            super().__init__(request, init_data, request.session[self._storage_key].get(request.path, {}), **kwargs)
        else:
            super().__init__(request, init_data, **kwargs)

    def cmd_store(self, request):
        request.session.setdefault(self._storage_key, {})[request.path] = {}
        for field_name, field in self.fields.items():
            if request.POST:
                for field_p in [f for f in request.POST if field_name in f]:
                    if field_p in self.data:
                        if (hasattr(field, 'multiply') and field.multiply):
                            request.session[self._storage_key][request.path][field_p] = self.data.getlist(field_p)
                        else:
                            request.session[self._storage_key][request.path][field_p] = self.data.get(field_p)

        request.session.modified = True

    def cmd_discard(self, request):
        if self._storage_key in request.session and request.path in request.session[self._storage_key]:
            for field_name, field in self.fields.items():
                for field_p in [f for f in request.POST if field_name in f]:
                    if field_p in request.session[self._storage_key][request.path]:
                        request.session[self._storage_key][request.path].pop(field_p)
        self.data = self.initial
        if 'p' in request.GET:
            return HttpResponseRedirect(request.path).url
        else:
            return request.build_absolute_uri()

class FormModelFilter(PermanentForm):
    
    def cmd_filter(self, request):
        if "?p=" in request.get_full_path():
            return request.get_full_path().replace(request.get_full_path().split("?")[1].split("&")[0], "")
        return request.get_full_path()

    def filter(self, model_data):
        return model_data