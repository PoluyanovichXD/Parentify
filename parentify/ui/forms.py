from django import forms

class FormCore(forms.Form):
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