from threading                   import Lock

from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse

form_csrf_lock = Lock()
csrf = {}
class HttpRedirectException(Exception):
    def __init__(self, redirect_url):
        self.redirect_url = redirect_url

class form_process_locker:

    def __init__(self, request):
        self.request = request

    def __enter__(self):
        with form_csrf_lock:
            if 'csrfmiddlewaretoken' in self.request.POST:
                if self.request.POST['csrfmiddlewaretoken'] in csrf:
                    raise HttpRedirectException(self.request.get_full_path())
                csrf[self.request.POST['csrfmiddlewaretoken']] = True
                return self.request.POST['csrfmiddlewaretoken']
        return '0'

    def __exit__(self, type, value, traceback):
        with form_csrf_lock:
            if 'csrfmiddlewaretoken' in self.request.POST and csrf:
                csrf.pop(self.request.POST['csrfmiddlewaretoken'], None)
        return False


def common_page(page_template='pages/PageAutorizedSimple.html'):
    def page_decorator(func):
        def func_wrapper(request, *args, **kwargs):
            worker = getattr(request, 'current_worker', None)
            try:
                page = func(request, *args, **kwargs)
                # closed_not_user_url = []
                # if not worker:
                #     for url in closed_not_user_url:
                #         if request.path.startswith(url):
                #             return login(request)
                if type(page) == HttpResponse or type(page) == HttpResponseRedirect  or type(page) == JsonResponse or type(page) == Response:
                    return page
                page.change_template(page_template)
                return page.render(request)
            except HttpRedirectException as e:
                return HttpResponseRedirect(e.redirect_url)
        return func_wrapper
    return page_decorator



def with_form(form_var, form_class, *actions):
    def contains_form_decorator(func):
        def func_wrapper(request, *args, **kwargs):
            form_dict = {}
            form = form_class(request, *args, **form_dict)
            kwargs = {**form_dict, **kwargs}
            if request.method == 'POST':
                with form_process_locker(request):
                    for action in actions:
                        if action in request.POST:
                            if 'cmd_discard' in form.__dict__['data']:
                                form.cmd_discard(request)
                                form.cmd_store(request)
                            elif form.is_valid():
                                r = getattr(form, action)(request)
                                if type(r) == HttpResponse:
                                    return r
                                if hasattr(form, 'discard_on_execute') and form.discard_on_execute:
                                    form.cmd_discard(request)
                                elif hasattr(form, 'cmd_store'):
                                    form.cmd_store(request)
                                try:
                                    if 'iframe_form' in request.GET:
                                        raise HttpRedirectException('?iframe_form&iframe_close')
                                    else:
                                        try:
                                            raise HttpRedirectException(r if r else request.get_full_path()) 
                                        except:
                                            raise HttpRedirectException(request.get_full_path()) 
                                except:
                                    if 'iframe_form' in request.GET:
                                        return HttpResponseRedirect('?iframe_form&iframe_close')
                                    else:
                                        try:
                                            return HttpResponseRedirect(r if r else request.get_full_path())
                                        except:
                                            return HttpResponseRedirect(request.get_full_path())
                            elif hasattr(form, 'cmd_store'):
                                form.cmd_store(request)
                            if hasattr(form,'errors') and form.errors:
                                print(form.errors)
            if form_var:
                kwargs[form_var] = form
            return func(request, *args, **kwargs)
        return func_wrapper
    return contains_form_decorator

def page_has_user(has_admin=False):
    def page_decorator(func):
        def func_wrapper(request,*args,**kwargs):
            try:
                worker = request.current_worker
                page = func(request, *args, **kwargs)
                is_response = type(page) == HttpResponse or type(page) == HttpResponseRedirect  or type(page) == JsonResponse
                if not worker:
                    raise Http404()
                else:
                    if has_admin and not worker.is_admin:
                        raise Http404()
                    else:
                        return page
            except HttpRedirectException as e:
                return HttpResponseRedirect(e.redirect_url)
        return func_wrapper
    return page_decorator


def with_get_int(par_name, min_value = None, max_value = None):
    def contains_form_decorator(func):
        def func_wrapper(request, *args, **kwargs):
            try:
                val = int('0' if 'cmd_filter' in request.POST else request.GET.get(par_name, '0') )
                if (min_value and val < min_value) or (max_value and val > max_value):
                    raise ValueError
            except ValueError:
                raise Http404()
            kwargs[par_name] = val
            return func(request, *args, **kwargs)
        return func_wrapper
    return contains_form_decorator