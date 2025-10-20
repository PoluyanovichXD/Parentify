from enum import Enum


class EventTypes(Enum):
    login = 'login'
    register = 'register'
    edit_profile = 'edit_profile'
    edit_password = 'edit_password'

    child_create = 'child_create'
    child_edit = 'child_edit'
    child_delete = 'child_delete'

    
    article_create = 'article_create'
    article_edit = 'article_edit'
    article_delete = 'article_delete'

    article_category_create = 'article_category_create'
    article_category_edit = 'article_category_edit'
    article_category_delete = 'article_category_delete'

    
    forum_topic_create = 'forum_topic_create'
    forum_topic_edit = 'forum_topic_edit'
    forum_topic_delete = 'forum_topic_delete'

    forum_topic_category_create = 'forum_topic_category_create'
    forum_topic_category_edit = 'forum_topic_category_edit'
    forum_topic_category_delete = 'forum_topic_category_delete'

    forum_topic_comment_create = 'forum_topic_comment_create'
    forum_topic_comment_edit = 'forum_topic_comment_edit'
    forum_topic_comment_delete = 'forum_topic_comment_delete'

    
    map_place_create = 'map_place_create'
    map_place_edit = 'map_place_edit'
    map_place_delete = 'map_place_delete'