from django.http import Http404, HttpResponse

from parentify.models.models import User
from parentify.ui.decorators import common_page

class users:
    @common_page()
    def avatar(request, model_id):
        try:
            return HttpResponse(request.orm_session.query(User).get(model_id).avatar,
                                content_type='image/*')
        except Exception as ex:
            print(ex)
            raise Http404()