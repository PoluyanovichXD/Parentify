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
    Получает статистику трекеров по указанному периоду с группировкой по детям и категориям
    period: 'year', 'month', 'week'
    """
    # Создаем копию базового запроса
    query = base_query
    
    # Получаем все записи трекеров
    treckers = query.all()
    if not treckers:
        # Возвращаем пустую структуру если нет данных
        return {
            'period': period,
            'categories': [],
            'series': [],
            'children': [],
            'categories_list': []
        }
    
    # Получаем всех детей из запроса
    children_ids = set([t.children_id for t in treckers])
    children = session.query(UserChild).filter(UserChild.id.in_(children_ids)).all() if children_ids else []
    
    # Получаем все категории трекеров
    category_ids = set([t.category_id for t in treckers])
    categories = session.query(TreckerCategory).filter(TreckerCategory.id.in_(category_ids)).all() if category_ids else []
    
    # Если нет детей или категорий, возвращаем пустую структуру
    if not children or not categories:
        return {
            'period': period,
            'categories': [],
            'series': [],
            'children': [{'id': c.id, 'name': c.first_name} for c in children] if children else [],
            'categories_list': [{'id': cat.id, 'name': cat.name} for cat in categories] if categories else []
        }
    if period == 'year':
        # Группировка по годам
        stats = session.query(
            extract('year', Trecker.date_trecker).label('year'),
            UserChild.id.label('child_id'),
            UserChild.first_name.label('child_name'),
            TreckerCategory.id.label('category_id'),
            TreckerCategory.name.label('category_name'),
            func.sum(Trecker.value).label('total'),
            func.count().label('count')
        ).join(
            UserChild, UserChild.id == Trecker.children_id
        ).join(
            TreckerCategory, TreckerCategory.id == Trecker.category_id
        ).filter(
            Trecker.id.in_([t.id for t in query.all()])
        ).group_by(
            extract('year', Trecker.date_trecker),
            UserChild.id,
            UserChild.first_name,
            TreckerCategory.id,
            TreckerCategory.name
        ).order_by(
            extract('year', Trecker.date_trecker),
            UserChild.first_name,
            TreckerCategory.name
        ).all()
        
        # Формируем уникальные годы
        years = sorted(set([s.year for s in stats]))
        
        # Формируем данные для графиков
        series_data = []
        
        # Для каждого ребенка и категории создаем серию
        for child in children:
            for category in categories:
                # Создаем данные для этой комбинации ребенок-категория
                series_name = f"{child.first_name} - {category.name}"
                data_for_series = []
                
                for year in years:
                    # Ищем статистику для этого года, ребенка и категории
                    stat = next((s for s in stats if s.year == year and 
                                s.child_id == child.id and s.category_id == category.id), None)
                    
                    if stat:
                        data_for_series.append(float(stat.total))
                    else:
                        data_for_series.append(0)
                
                # Добавляем серию только если есть хоть какие-то данные
                if any(data_for_series):
                    series_data.append({
                        'name': series_name,
                        'data': data_for_series,
                        'color': get_color_for_child_category(child.id, category.id)
                    })
        
        result = {
            'period': 'year',
            'categories': years,
            'series': series_data,
            'children': [{'id': c.id, 'name': c.first_name} for c in children],
            'categories_list': [{'id': cat.id, 'name': cat.name} for cat in categories]
        }
        
    elif period == 'month':
        # Группировка по месяцам (последние 12 месяцев)
        end_date = datetime.now()
        start_date = end_date - timedelta(days=365)
        
        stats = session.query(
            extract('year', Trecker.date_trecker).label('year'),
            extract('month', Trecker.date_trecker).label('month'),
            UserChild.id.label('child_id'),
            UserChild.first_name.label('child_name'),
            TreckerCategory.id.label('category_id'),
            TreckerCategory.name.label('category_name'),
            func.sum(Trecker.value).label('total'),
            func.count().label('count')
        ).join(
            UserChild, UserChild.id == Trecker.children_id
        ).join(
            TreckerCategory, TreckerCategory.id == Trecker.category_id
        ).filter(
            Trecker.id.in_([t.id for t in query.all()]),
            Trecker.date_trecker >= start_date
        ).group_by(
            extract('year', Trecker.date_trecker),
            extract('month', Trecker.date_trecker),
            UserChild.id,
            UserChild.first_name,
            TreckerCategory.id,
            TreckerCategory.name
        ).order_by(
            extract('year', Trecker.date_trecker),
            extract('month', Trecker.date_trecker),
            UserChild.first_name,
            TreckerCategory.name
        ).all()
        
        # Формируем последние 12 месяцев
        months = []
        month_data = {}
        
        for i in range(12):
            month_date = end_date - timedelta(days=30*i)
            year = month_date.year
            month = month_date.month
            month_label = f"{calendar.month_name[month][:3]} {year}"
            months.insert(0, month_label)
            month_data[(year, month)] = len(months) - 1  # Индекс в массиве
        
        # Формируем данные для графиков
        series_data = []
        
        # Для каждого ребенка и категории создаем серию
        for child in children:
            for category in categories:
                # Создаем данные для этой комбинации ребенок-категория
                series_name = f"{child.first_name} - {category.name}"
                data_for_series = [0] * len(months)
                
                # Заполняем данные
                for stat in stats:
                    if stat.child_id == child.id and stat.category_id == category.id:
                        month_index = month_data.get((stat.year, stat.month))
                        if month_index is not None:
                            data_for_series[month_index] = float(stat.total)
                
                # Добавляем серию только если есть хоть какие-то данные
                if any(data_for_series):
                    series_data.append({
                        'name': series_name,
                        'data': data_for_series,
                        'color': get_color_for_child_category(child.id, category.id)
                    })
        
        result = {
            'period': 'month',
            'categories': months,
            'series': series_data,
            'children': [{'id': c.id, 'name': c.first_name} for c in children],
            'categories_list': [{'id': cat.id, 'name': cat.name} for cat in categories]
        }
        
    elif period == 'week':
        # Группировка по неделям (последние 12 недель)
        end_date = datetime.now()
        start_date = end_date - timedelta(weeks=11)
        
        stats = session.query(
            extract('isoyear', Trecker.date_trecker).label('year'),
            extract('week', Trecker.date_trecker).label('week'),
            UserChild.id.label('child_id'),
            UserChild.first_name.label('child_name'),
            TreckerCategory.id.label('category_id'),
            TreckerCategory.name.label('category_name'),
            func.sum(Trecker.value).label('total'),
            func.count().label('count')
        ).join(
            UserChild, UserChild.id == Trecker.children_id
        ).join(
            TreckerCategory, TreckerCategory.id == Trecker.category_id
        ).filter(
            Trecker.id.in_([t.id for t in query.all()]),
            Trecker.date_trecker >= start_date
        ).group_by(
            extract('isoyear', Trecker.date_trecker),
            extract('week', Trecker.date_trecker),
            UserChild.id,
            UserChild.first_name,
            TreckerCategory.id,
            TreckerCategory.name
        ).order_by(
            extract('isoyear', Trecker.date_trecker),
            extract('week', Trecker.date_trecker),
            UserChild.first_name,
            TreckerCategory.name
        ).all()
        
        # Формируем последние 12 недель
        weeks = []
        week_data = {}
        
        for i in range(12):
            week_date = end_date - timedelta(weeks=i)
            year = week_date.isocalendar()[0]
            week_num = week_date.isocalendar()[1]
            
            # Форматируем отображение недели
            week_start = week_date - timedelta(days=week_date.weekday())
            week_end = week_start + timedelta(days=6)
            week_label = f"{week_start.strftime('%d.%m')}-{week_end.strftime('%d.%m')}"
            weeks.insert(0, week_label)
            week_data[(year, week_num)] = len(weeks) - 1
        
        # Формируем данные для графиков
        series_data = []
        
        # Для каждого ребенка и категории создаем серию
        for child in children:
            for category in categories:
                # Создаем данные для этой комбинации ребенок-категория
                series_name = f"{child.first_name} - {category.name}"
                data_for_series = [0] * len(weeks)
                
                # Заполняем данные
                for stat in stats:
                    if stat.child_id == child.id and stat.category_id == category.id:
                        week_index = week_data.get((stat.year, stat.week))
                        if week_index is not None:
                            data_for_series[week_index] = float(stat.total)
                
                # Добавляем серию только если есть хоть какие-то данные
                if any(data_for_series):
                    series_data.append({
                        'name': series_name,
                        'data': data_for_series,
                        'color': get_color_for_child_category(child.id, category.id)
                    })
        
        result = {
            'period': 'week',
            'categories': weeks,
            'series': series_data,
            'children': [{'id': c.id, 'name': c.first_name} for c in children],
            'categories_list': [{'id': cat.id, 'name': cat.name} for cat in categories]
        }
    
    return result


def get_color_for_child_category(child_id, category_id):
    """
    Генерирует цвет для комбинации ребенок-категория
    """
    # Базовые цвета для детей
    child_colors = {
        1: '#2196F3',  # Синий
        2: '#FF9800',  # Оранжевый
        3: '#4CAF50',  # Зеленый
        4: '#E91E63',  # Розовый
        5: '#9C27B0',  # Фиолетовый
        6: '#00BCD4',  # Бирюзовый
        7: '#FF5722',  # Темно-оранжевый
        8: '#795548',  # Коричневый
    }
    
    # Оттенки для категорий
    category_shades = {
        1: 'darken',   # Темнее
        2: 'normal',   # Нормальный
        3: 'lighten',  # Светлее
        4: 'lighter',  # Еще светлее
        5: 'lightest', # Самый светлый
    }
    
    # Базовый цвет для ребенка
    base_color = child_colors.get(child_id % len(child_colors) + 1, '#2196F3')
    
    # Получаем оттенок для категории
    shade_type = category_shades.get(category_id % len(category_shades) + 1, 'normal')
    
    # Генерируем цвет (упрощенная версия)
    if shade_type == 'darken':
        return base_color
    elif shade_type == 'normal':
        return base_color
    elif shade_type == 'lighten':
        # Упрощенное осветление цвета
        return lighten_color(base_color, 0.2)
    elif shade_type == 'lighter':
        return lighten_color(base_color, 0.4)
    elif shade_type == 'lightest':
        return lighten_color(base_color, 0.6)
    
    return base_color


def lighten_color(color, amount):
    """
    Упрощенная функция для осветления цвета
    """
    # Это упрощенная версия - в реальном приложении используйте библиотеку для работы с цветами
    colors = {
        '#2196F3': ['#1976D2', '#64B5F6', '#90CAF9', '#BBDEFB'],  # Синий
        '#FF9800': ['#F57C00', '#FFB74D', '#FFCC80', '#FFE0B2'],  # Оранжевый
        '#4CAF50': ['#388E3C', '#81C784', '#A5D6A7', '#C8E6C9'],  # Зеленый
        '#E91E63': ['#C2185B', '#F06292', '#F48FB1', '#F8BBD0'],  # Розовый
        '#9C27B0': ['#7B1FA2', '#BA68C8', '#CE93D8', '#E1BEE7'],  # Фиолетовый
        '#00BCD4': ['#0097A7', '#4DD0E1', '#80DEEA', '#B2EBF2'],  # Бирюзовый
    }
    
    # Если цвет найден, возвращаем соответствующий оттенок
    if color in colors:
        shades = colors[color]
        if amount <= 0.2:
            return shades[0] if len(shades) > 0 else color
        elif amount <= 0.4:
            return shades[1] if len(shades) > 1 else color
        elif amount <= 0.6:
            return shades[2] if len(shades) > 2 else color
        else:
            return shades[3] if len(shades) > 3 else color
    
    return color


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
            try:
                statistics = get_trecker_statistics(request.orm_session, query, period)
                return JsonResponse(statistics)
            except Exception as e:
                return JsonResponse({
                    'error': str(e),
                    'period': period,
                    'categories': [],
                    'series': [],
                    'children': [],
                    'categories_list': []
                }, status=500)
        
        if request.GET.get('delete') and request.current_user:
            request.orm_session.delete(query.get(request.GET.get('delete')))
            request.orm_session.commit()
            return HttpResponseRedirect('/trecker/')
        
        # Получаем статистику для графика
        try:
            period = request.GET.get('period', 'month')
            statistics = get_trecker_statistics(request.orm_session, query, period)
        except Exception as e:
            # В случае ошибки возвращаем пустую статистику
            statistics = {
                'period': 'month',
                'categories': [],
                'series': [],
                'children': [],
                'categories_list': []
            }
        
        request.statistics = statistics
        
        modelInfo = PageModelInfo(request.session, '/trecker/', query.order_by(Trecker.created_at.desc()), Trecker.id)
        page = PageTreckerEditor(modelInfo).items(request, p, form_filter, type_list='dict', btn_controls=ControlHtml({},'widgets/chart_trecker.html'))
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