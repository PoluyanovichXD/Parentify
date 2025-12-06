from enum import Enum


class EventTypes(Enum):
    login = 'Авторизация пользователя'
    register = 'Регистрация пользователя'
    edit_profile = 'Редактирование профиля'
    edit_password = 'Изменение пароля'

    child_create = 'Создание профиля ребенка'
    child_edit = 'Редактирование профиля ребенка'
    child_delete = 'Удаление профиля ребенка'

    article_create = 'Создание статьи'
    article_edit = 'Редактирование статьи'
    article_delete = 'Удаление статьи'

    article_category_create = 'Создание категории статей'
    article_category_edit = 'Редактирование категории статей'
    article_category_delete = 'Удаление категории статей'

    forum_topic_create = 'Создание темы форума'
    forum_topic_edit = 'Редактирование темы форума'
    forum_topic_delete = 'Удаление темы форума'

    forum_topic_category_create = 'Создание категории форума'
    forum_topic_category_edit = 'Редактирование категории форума'
    forum_topic_category_delete = 'Удаление категории форума'

    forum_topic_comment_create = 'Добавление комментария'
    forum_topic_comment_edit = 'Редактирование комментария'
    forum_topic_comment_delete = 'Удаление комментария'

    map_place_create = 'Добавление места на карте'
    map_place_edit = 'Редактирование места на карте'
    map_place_delete = 'Удаление места на карте'