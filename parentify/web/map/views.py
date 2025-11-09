from django.http import Http404, HttpResponse
from django.shortcuts import render

from parentify.models.models import Place
from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.map.forms import FormFilterPlace, FormPlace
from parentify.web.map.pages import PagePlaceEditor

def home(request):
    return render(request, 'pages/map/home.html')


class place:
    @common_page()
    @with_form('form_filter', FormFilterPlace, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/map/', request.orm_session.query(Place), Place.id)
        return PagePlaceEditor(modelInfo).items(request, p, form_filter, type_list='dict')

    @common_page()
    @with_form('form_model', FormPlace, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/map/', request.orm_session.query(Place), Place.id)
        page = PagePlaceEditor(modelInfo).new(request, ControlInputs(form_model))
        return page 

    @common_page()
    @with_form('form_model', FormPlace, 'cmd_model_update')
    def edit(request, place_id, form_model):
        modelInfo = PageModelInfo(request.session, '/map/', request.orm_session.query(Place), Place.id)
        page = PagePlaceEditor(modelInfo)
        return page.edit(request, place_id, ControlInputs(form_model))

    @common_page()
    def view(request, place_id):
        modelInfo = PageModelInfo(request.session, '/map/', request.orm_session.query(Place), Place.id)
        page = PagePlaceEditor(modelInfo)
        return page.view(request, place_id)
    
    def image_url(request, place_id):
        try:
            return HttpResponse(request.orm_session.query(Place).get(place_id).image,
                                content_type='image/*')
        except Exception as ex:
            print(ex)
            raise Http404()