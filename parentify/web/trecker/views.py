import datetime
from django.http import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from sqlalchemy import extract, func, case
from datetime import datetime, timedelta
import calendar, json

from parentify.models.models import Goods, GoodsCategory, UserFavorite, Trecker, TreckerCategory, UserChild
from parentify.ui.controls import ControlInputs, ControlHtml
from parentify.ui.decorators import common_page, page_has_user, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.web.trecker.forms import FormFilterTrecker, FormTrecker, FormFilterCategory, FormCategory
from parentify.web.trecker.pages import PageTreckerEditor, PageCategoryEditor

def get_trecker_statistics(session, base_query, period='month'):
    """
    Получает статистику трекеров по указанному периоду
    period: 'year', 'month', 'week'
    """
    # Создаем копию базового запроса без сортировки
    query = base_query
    
    if period == 'year':
        # Группировка по годам
        stats = session.query(
            extract('year', Trecker.date_trecker).label('period'),
            func.sum(Trecker.value).label('total'),
            func.count().label('count')
        ).filter(
            Trecker.id.in_([t.id for t in query.all()])
        ).group_by(
            extract('year', Trecker.date_trecker)
        ).order_by(
            extract('year', Trecker.date_trecker)
        ).all()
        
        # Форматируем данные для Highcharts
        result = {
            'period': 'year',
            'categories': [int(s.period) for s in stats],
            'data': [float(s.total) for s in stats],
            'count': [int(s.count) for s in stats],
            'data_avg': [float(s.total / s.count) if s.count > 0 else 0 for s in stats]
        }
        
    elif period == 'month':
        # Группировка по месяцам года
        current_year = datetime.now().year
        last_year = current_year - 1
        
        # Получаем данные за последние 2 года
        stats = session.query(
            extract('year', Trecker.date_trecker).label('year'),
            extract('month', Trecker.date_trecker).label('month'),
            func.sum(Trecker.value).label('total'),
            func.count().label('count')
        ).filter(
            Trecker.id.in_([t.id for t in query.all()]),
            extract('year', Trecker.date_trecker).in_([current_year, last_year])
        ).group_by(
            extract('year', Trecker.date_trecker),
            extract('month', Trecker.date_trecker)
        ).order_by(
            extract('year', Trecker.date_trecker),
            extract('month', Trecker.date_trecker)
        ).all()
        
        # Формируем данные для всех месяцев
        months = []
        data = []
        count = []
        data_avg = []
        
        for year in [last_year, current_year]:
            for month in range(1, 13):
                month_name = f"{calendar.month_name[month][:3]} {year}"
                months.append(month_name)
                
                # Ищем данные для этого месяца
                stat = next((s for s in stats if s.year == year and s.month == month), None)
                if stat:
                    data.append(float(stat.total))
                    count.append(int(stat.count))
                    data_avg.append(float(stat.total / stat.count) if stat.count > 0 else 0)
                else:
                    data.append(0)
                    count.append(0)
                    data_avg.append(0)
        
        result = {
            'period': 'month',
            'categories': months,
            'data': data,
            'count': count,
            'data_avg': data_avg
        }
        
    elif period == 'week':
        # Группировка по неделям (последние 12 недель)
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=11)  # 12 недель включая текущую
        
        # Используем ISO недели (год и номер недели)
        stats = session.query(
            extract('isoyear', Trecker.date_trecker).label('year'),
            extract('week', Trecker.date_trecker).label('week'),
            func.sum(Trecker.value).label('total'),
            func.count().label('count')
        ).filter(
            Trecker.id.in_([t.id for t in query.all()]),
            Trecker.date_trecker >= start_date
        ).group_by(
            extract('isoyear', Trecker.date_trecker),
            extract('week', Trecker.date_trecker)
        ).order_by(
            extract('isoyear', Trecker.date_trecker),
            extract('week', Trecker.date_trecker)
        ).all()
        
        # Формируем список последних 12 недель
        weeks = []
        data = []
        count = []
        data_avg = []
        
        # Создаем словарь для быстрого поиска
        stats_dict = {(int(s.year), int(s.week)): s for s in stats}
        
        for i in range(12):
            week_date = end_date - timedelta(weeks=i)
            year = week_date.isocalendar()[0]
            week_num = week_date.isocalendar()[1]
            
            # Форматируем отображение недели
            week_start = week_date - timedelta(days=week_date.weekday())
            week_end = week_start + timedelta(days=6)
            week_label = f"{week_start.strftime('%d.%m')}-{week_end.strftime('%d.%m')}"
            weeks.insert(0, week_label)
            
            # Ищем данные для этой недели
            stat = stats_dict.get((year, week_num))
            if stat:
                data.insert(0, float(stat.total))
                count.insert(0, int(stat.count))
                data_avg.insert(0, float(stat.total / stat.count) if stat.count > 0 else 0)
            else:
                data.insert(0, 0)
                count.insert(0, 0)
                data_avg.insert(0, 0)
        
        result = {
            'period': 'week',
            'categories': weeks,
            'data': data,
            'count': count,
            'data_avg': data_avg
        }
    
    return result

class trecker:
    @common_page()
    @with_form('form_filter', FormFilterTrecker, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, *args, **kwargs):
        p = kwargs.get('p')
        form_filter = kwargs.get('form_filter')
        query = request.orm_session.query(Trecker)
        
        if args:
            query = query.filter(Trecker.children_id==args[0])
        elif request.current_user and not request.current_user.is_admin:
            childrens = request.orm_session.query(UserChild).filter(UserChild.user_id==request.current_user.id)
            query = query.filter(Trecker.children_id.in_([item.id for item in childrens]))
        
        # Проверяем, если это JSON запрос
        if request.GET.get('json') == '1':
            from django.http import JsonResponse
            period = request.GET.get('period', 'month')
            statistics = get_trecker_statistics(request.orm_session, query, period)
            return JsonResponse(statistics)
        
        if request.GET.get('delete') and request.current_user:
            request.orm_session.delete(query.get(request.GET.get('delete')))
            request.orm_session.commit()
            return HttpResponseRedirect('/trecker/')
        
        # Получаем статистику для графика
        period = request.GET.get('period', 'month')
        statistics = get_trecker_statistics(request.orm_session, query, period)
        request.statistics = statistics
        
        modelInfo = PageModelInfo(request.session, '/trecker/', query.order_by(Trecker.created_at.desc()), Trecker.id)
        page = PageTreckerEditor(modelInfo).items(request, p, form_filter, type_list='dict', controls=ControlHtml({},'widgets/chart_trecker.html'))
        return page

    @common_page()
    @with_form('form_model', FormTrecker, 'cmd_model_create')
    def create(request, *args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/', request.orm_session.query(Trecker), Trecker.id)
        page = PageTreckerEditor(modelInfo).new(request, ControlInputs(kwargs.get('form_model')))
        return page 

    @common_page()
    @with_form('form_model', FormTrecker, 'cmd_model_update')
    def edit(request, *args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/', request.orm_session.query(Trecker), Trecker.id)
        page = PageTreckerEditor(modelInfo)
        return page.edit(request, args[0] if len(args)==1 else args[1], ControlInputs(kwargs.get('form_model')))

    @common_page()
    def view(request, *args):
        model_id = args[0] if len(args)==1 else args[1]
        if request.GET.get('delete') and request.current_user and request.current_user.is_admin:
            request.orm_session.delete(request.orm_session.query(Trecker).get(model_id))
            request.orm_session.commit()
            return HttpResponseRedirect('../')
        modelInfo = PageModelInfo(request.session, '/trecker/', request.orm_session.query(Trecker), Trecker.id)
        page = PageTreckerEditor(modelInfo)
        return page.view(request, args[0] if len(args)==1 else args[1])
    

class categories:
    @common_page()
    @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
    @with_get_int('p', 0, 255)
    def all(request, *args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/categories/', request.orm_session.query(TreckerCategory).order_by(TreckerCategory.created_at.desc()), TreckerCategory.id)
        return PageCategoryEditor(modelInfo).items(request, kwargs.get('p'), kwargs.get('form_filter'), PageCategoryEditor.toolbar, no_zip=False)

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_create')
    def create(request,*args, **kwargs):
        modelInfo = PageModelInfo(request.session, '/trecker/categories/', request.orm_session.query(TreckerCategory), TreckerCategory.id)
        page = PageCategoryEditor(modelInfo).new(request, ControlInputs(kwargs.get('form_model'), classname='[&]:md:grid-cols-1'))
        return page 

    @common_page()
    @with_form('form_model', FormCategory, 'cmd_model_update')
    def edit(request, *args, **kwargs):
        model_id = args[0] if len(args)==1 else args[1]
        modelInfo = PageModelInfo(request.session, '/trecker/categories/', request.orm_session.query(TreckerCategory), TreckerCategory.id)
        page = PageCategoryEditor(modelInfo)
        return page.edit(request,model_id, ControlInputs(kwargs.get('form_model')))