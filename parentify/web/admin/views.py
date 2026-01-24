from django.http                    import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts               import render
from parentify.models.models        import *
from django.contrib.auth.hashers    import *

from sqlalchemy import inspect, func

from parentify.ui.controls import ControlBase, ControlHtml, ControlInputs, ControlPagerFull, ControlRecord, ControlRecordlist
from parentify.ui.decorators import HttpRedirectException, common_page, page_has_user, with_form, with_get_int
from parentify.ui.mvc import PageModelInfo
from parentify.ui.pages import PageSimple
from parentify.web.admin.pages import PageAdminEditor
from parentify.web.childs.forms import FormChild
from parentify.web.forms import FormRegister
from parentify.web.forum.forms import FormForum, FormCategory as FormForumCategory, FormForumComment
from parentify.web.goods.forms import FormGoods, FormCategory as FormGoodsCategory
from parentify.web.map.forms import FormPlace, FormCategory as FormPlaceCategory
from parentify.web.article.forms import FormArticle, FormCategory as FormArticleCategory
from parentify.web.calendar.forms import FormDevelopmentCalendar, ChildDevelopmentWeek
from datetime import datetime, timedelta


dictAdminModels = {
    "": [None, "Дашборд", "fas fa-tachometer-alt",[],None],
    "user": [User, "Пользователи", "fas fa-users",
        [['ФИО', 'full_name'],['Почта', "email"]], FormRegister,
    ],
    "user_child": [UserChild, "Дети", "fas fa-child",
        [['ФИО', 'full_name'],['Родитель', "user.full_name"]], FormChild,
    ],
    "article": [Article, "Статьи", "fas fa-newspaper",
        [['Название','title']], FormArticle,
    ],
    "article_category": [ArticleCategory, "Категории статей", "fas fa-folder",
        [['Название','name']], FormArticleCategory,
    ],
    "forum_topic": [ForumTopic, "Вопросы форума", "fas fa-comments",
        [['Название','title']], FormForum,
    ],
    "forum_comment": [ForumComment, "Коментарии форума", "fas fa-message",
        [['Название','topic.title'], ['Пользователь','user.full_name'], ['Сообщение','content']], FormForumComment,
    ],
    "forum_topic_category": [ForumTopicCategory, "Категории форума", "fas fa-tags",
        [['Название','name']], FormForumCategory,
    ],
    "place": [Place, "Места", "fas fa-map-marker-alt",
        [['Название','title']], FormPlace,
    ],
    "place_category": [PlaceCategory, "Категории мест", "fas fa-map-signs",
        [['Название','name']], FormPlaceCategory,
    ],
    "goods": [Goods, "Товары", "fas fa-store",
        [['Название','title']], FormGoods,
    ],
    "goods_category": [GoodsCategory, "Категории товаров", "fas fa-box-open",
        [['Название','name']], FormGoodsCategory,
    ],
    "calendar": [ChildDevelopmentWeek, "Календарь развития", "fas fa-calendar",
        [['Заголовок','title'], ['Номер недели','week_number']], FormDevelopmentCalendar,
    ],
}

def adminMenu(orm): 
    return {
    key: {
        "name": val[1],
        "icon": val[2],
        "url": f'/admin/{key}/',
        "count": orm.query(val[0]).count() if val[0] else 0,
        "model": val[0],
        "fields": val[3],
        "form": val[4]
    }
    for key, val in dictAdminModels.items()
}

def page_admin():
    def page_decorator(func):
        @page_has_user(True)
        @common_page()
        def func_wrapper(request, *args, **kwargs):
            try:
                user = request.current_user
                
                if not user or not getattr(user, 'is_admin', False):
                    raise Http404()
                
                request.admin_menu = adminMenu(request.orm_session)
                
                page = func(request, *args, **kwargs)
                
                is_response = isinstance(page, (HttpResponse, HttpResponseRedirect, JsonResponse))
                if not is_response:
                    page.change_template('wrappers/admin.html')
                    return page
                else:
                    return page
                    
            except HttpRedirectException as e:
                return HttpResponseRedirect(e.redirect_url)
        return func_wrapper
    return page_decorator




class admin:
    @page_admin()
    @with_get_int('p', 0, 255)
    def dashboard(request, p):
        page_number = p
        page_size = 25
        page = PageSimple('Администрирование')
        dashboard = ControlBase('controls/ControlDashboard.html')
        now = datetime.now()
        week_ago = now - timedelta(days=7)
        
        # Получаем данные для графика за текущий месяц
        current_month_start = datetime(now.year, now.month, 1)
        next_month = now.month + 1 if now.month < 12 else 1
        next_month_year = now.year if now.month < 12 else now.year + 1
        current_month_end = datetime(next_month_year, next_month, 1) - timedelta(days=1)
        
        # Группируем события по дням за текущий месяц (для PostgreSQL)
        from sqlalchemy import func, cast, Date
        
        # Вариант для PostgreSQL
        event_stats = request.orm_session.query(
            cast(SiteEvent.created_at, Date).label('date'),
            func.count(SiteEvent.id).label('count')
        ).filter(
            SiteEvent.created_at >= current_month_start,
            SiteEvent.created_at <= current_month_end
        ).group_by(
            cast(SiteEvent.created_at, Date)
        ).order_by('date').all()
        
        # Преобразуем данные для Highcharts
        chart_dates = []  # Список дат для категорий
        chart_counts = []  # Список количеств для данных
        total_events = 0
        
        # Создаем полный диапазон дат за месяц
        date_range = []
        current_date = current_month_start
        while current_date <= current_month_end:
            date_range.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        # Заполняем данные для графика
        event_dict = {}
        for date_obj, count in event_stats:
            # date_obj может быть datetime или date, преобразуем в строку
            if hasattr(date_obj, 'strftime'):
                date_str = date_obj.strftime('%Y-%m-%d')
            else:
                date_str = str(date_obj)
            event_dict[date_str] = count
            total_events += count
            
        for date_str in date_range:
            chart_dates.append(date_str)
            chart_counts.append(event_dict.get(date_str, 0))
        
        # Группируем события по типу для круговой диаграммы
        event_by_type = request.orm_session.query(
            SiteEvent.type,
            func.count(SiteEvent.id).label('count')
        ).filter(
            SiteEvent.created_at >= current_month_start,
            SiteEvent.created_at <= current_month_end
        ).group_by(SiteEvent.type).all()
        
        # Словарь для перевода типов событий на русский
        event_type_translations = {
            'login': 'Авторизация',
            'register': 'Регистрация',
            'edit_profile': 'Редактирование профиля',
            'edit_password': 'Изменение пароля',
            'child_create': 'Создание профиля ребенка',
            'child_edit': 'Редактирование профиля ребенка',
            'child_delete': 'Удаление профиля ребенка',
            'article_create': 'Создание статьи',
            'article_edit': 'Редактирование статьи',
            'article_delete': 'Удаление статьи',
            'article_category_create': 'Создание категории статей',
            'article_category_edit': 'Редактирование категории статей',
            'article_category_delete': 'Удаление категории статей',
            'forum_topic_create': 'Создание вопроса форума',
            'forum_topic_edit': 'Редактирование вопроса форума',
            'forum_topic_delete': 'Удаление вопроса форума',
            'forum_topic_category_create': 'Создание категории форума',
            'forum_topic_category_edit': 'Редактирование категории форума',
            'forum_topic_category_delete': 'Удаление категории форума',
            'forum_topic_comment_create': 'Добавление комментария',
            'forum_topic_comment_edit': 'Редактирование комментария',
            'forum_topic_comment_delete': 'Удаление комментария',
            'map_place_create': 'Добавление места на карте',
            'map_place_edit': 'Редактирование места на карте',
            'map_place_delete': 'Удаление места на карте',
        }
        
        # Преобразуем данные для круговой диаграммы
        pie_chart_data = []
        for event_type, count in event_by_type:
            # Получаем русское название или оставляем оригинальное, если перевода нет
            russian_name = event_type_translations.get(event_type, event_type)
            pie_chart_data.append({
                'name': russian_name,
                'y': count
            })
        
        dashboard.add_context({
            'user_count': request.orm_session.query(User).count(),
            'user_child_count': request.orm_session.query(UserChild).count(),
            'article_count': request.orm_session.query(Article).count(),
            'forum_topic_count': request.orm_session.query(ForumTopic).count(),
            'new_users': request.orm_session.query(User).filter(User.created_at >= week_ago),
            'new_users_count': request.orm_session.query(User).filter(User.created_at >= week_ago).count(),
            'event_stats': event_stats,
            'chart_dates': chart_dates,  # Отдельный список дат
            'chart_counts': chart_counts,  # Отдельный список количеств
            'pie_chart_data': pie_chart_data,
            'current_month': now.strftime('%B %Y'),
            'total_events': total_events,
        })
        
        query = request.orm_session.query(SiteEvent)
        recordList = ControlRecordlist(query[page_number * page_size: (page_number + 1) * page_size],
        [
            ['Пользователь', 'user.full_name'],
            ['Действие', 'text'],
            ['Время', 'created_at'],
        ])
        recordList.add_pager('bottom_pager', ControlPagerFull(query, page_number, page_size, query.count(), query.count()))
        page.add_control('dashboard', dashboard)
        page.add_control('html', recordList)
        request.stat = request.orm_session.query(SiteEvent)
        return page
    
    @page_admin()
    @with_get_int('p', 0, 255)
    def model_list(request, model, p):
        dataModel = adminMenu(request.orm_session).get(model)
        if not dataModel:
            raise Http404()
        if request.GET.get('delete'):
            request.orm_session.delete(request.orm_session.query(dataModel['model']).get(request.GET.get('delete')))
            request.orm_session.commit()
            return HttpResponseRedirect(dataModel['url'])
        modelInfo = PageModelInfo(request.session, dataModel['url'], request.orm_session.query(dataModel['model']), dataModel['model'].id)
        PageAdminEditor._fields = dataModel['fields']
        return PageAdminEditor(modelInfo).items(request, p, None, PageAdminEditor.toolbar)
    @page_admin()
    def model_create(request,model):
        dataModel = adminMenu(request.orm_session).get(model)
        if not dataModel:
            raise Http404()
        form_model=dataModel['form'](request)
        if 'cmd_model_create' in request.POST and form_model.is_valid():
            form_model.cmd_model_create(request)
            return HttpResponseRedirect(dataModel['url'])
        modelInfo = PageModelInfo(request.session, dataModel['url'], request.orm_session.query(dataModel['model']), dataModel['model'].id)
        page = PageAdminEditor(modelInfo).new(request, ControlInputs(form_model))
        return page 
    @page_admin()
    def model_edit(request, model, model_id):
        dataModel = adminMenu(request.orm_session).get(model)
        if not dataModel:
            raise Http404()
        form_model=dataModel['form'](request, model_id)
        if 'cmd_model_update' in request.POST and form_model.is_valid():
            form_model.cmd_model_create(request)
            return HttpResponseRedirect(dataModel['url'])
        modelInfo = PageModelInfo(request.session, dataModel['url'], request.orm_session.query(dataModel['model']), dataModel['model'].id)
        page = PageAdminEditor(modelInfo)
        return page.edit(request,model_id, ControlInputs(form_model))


# @with_form('form_filter', FormFilterCategory, 'cmd_filter', 'cmd_discard', 'cmd_store')
# @with_form('form_model', FormCategory, 'cmd_model_create')
# @with_form('form_model', FormCategory, 'cmd_model_update')