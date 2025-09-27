from django.conf import settings
from django.http import Http404, HttpResponse, HttpResponseRedirect


def common_page(page_template='pages/PageAutorizedSimple.html'):
    def page_decorator(func):
        def func_wrapper(request, *args, **kwargs):
            worker = getattr(request, 'current_worker', None)
            if request.path.startswith('/journal') and not settings.WEB_VERSION:
                raise Http404()
            try:
                page = func(request, *args, **kwargs)
                closed_not_user_url = []
                if not worker:
                    for url in closed_not_user_url:
                        if request.path.startswith(url):
                            return login(request)
                if type(page) == HttpResponse or type(page) == HttpResponseRedirect  or type(page) == JsonResponse or type(page) == Response:
                    return page
                page.change_template(page_template)
                return page.render(request)
            except HttpRedirectException as e:
                return HttpResponseRedirect(e.redirect_url)
        return func_wrapper
    return page_decorator