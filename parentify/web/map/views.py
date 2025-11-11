from django.http import Http404, HttpResponse, HttpResponseRedirect
from django.shortcuts import render

from parentify.models.models import Place, PlaceCategory
from parentify.ui.controls import ControlInputs
from parentify.ui.decorators import common_page, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.map.forms import FormFilterPlace, FormPlace, FormFilterCategory, FormCategory
from parentify.web.map.pages import PagePlaceEditor, PageCategoryEditor

def home(request):
    return render(request, 'pages/map/home.html')


class place:
    @common_page()
    @with_form('form_filter', FormFilterPlace, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        if request.GET.get('delete') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(Place).get(request.GET.get('delete')))
            request.orm_session.commit()
            return HttpResponseRedirect('/map/')
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
        
class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, p, form_filter):
        modelInfo = PageModelInfo(request.session, '/map/categories/', request.orm_session.query(PlaceCategory), PlaceCategory.id)
        return PageCategoryEditor(modelInfo).items(request, p, form_filter, PageCategoryEditor.toolbar, no_zip=False)

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_create')
    def create(request, form_model):
        modelInfo = PageModelInfo(request.session, '/map/categories/', request.orm_session.query(PlaceCategory), PlaceCategory.id)
        page = PageCategoryEditor(modelInfo).new(request, ControlInputs(form_model, classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_update')
    def edit(request, model_id, form_model):
        modelInfo = PageModelInfo(request.session, '/map/categories/', request.orm_session.query(PlaceCategory), PlaceCategory.id)
        page = PageCategoryEditor(modelInfo)
        return page.edit(request,model_id, ControlInputs(form_model))