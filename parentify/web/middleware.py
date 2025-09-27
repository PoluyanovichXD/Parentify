from django.http import HttpRequest
import time, requests, datetime

from django.conf                import settings
from django.http.response       import HttpResponse, HttpResponseRedirect, Http404
from django.utils.deprecation   import MiddlewareMixin
from parentify.models.models              import Orm, User


class BaseSessionMiddleware(MiddlewareMixin):
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        request.host = f"{request.scheme}://{ request.META.get('HTTP_HOST')}"
        request.settings = settings
        request.current_datetime = datetime.datetime.now()
        request.orm_session = Orm()
        request.current_user = request.orm_session.query(User).filter(User.password==request.session.get('token')).first()
        return view_func(request, *view_args, **view_kwargs)

    def process_request(self, request):
        pass
        # request.orm_session = Orm()

    def process_response(self, request, response):
        try:
            request.orm_session.close()
        except AttributeError:
            return response
        return response

    def process_exception(self, request, exception):
        try:
            request.orm_session.close()
        except AttributeError:
            pass
        print(exception)