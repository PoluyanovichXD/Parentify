from django.http                    import Http404, HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts               import render
from parentify.models.models        import *
from django.contrib.auth.hashers    import *

from sqlalchemy import inspect

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
        dashboard.add_context({
            'user_count': request.orm_session.query(User).count(),
            'user_child_count': request.orm_session.query(UserChild).count(),
            'article_count': request.orm_session.query(Article).count(),
            'forum_topic_count': request.orm_session.query(ForumTopic).count(),
            'new_users': request.orm_session.query(User).filter(User.created_at >= week_ago),
            'new_users_count': request.orm_session.query(User).filter(User.created_at >= week_ago).count(),
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
        # request.stat = request.orm_session.query(SiteEvent)
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