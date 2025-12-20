# parentify/__init__.py
from __future__ import absolute_import, unicode_literals

# Просто определяем имя для импорта, но не импортируем celery_app здесь
# Это предотвратит рекурсию при импорте из tasks.py
__all__ = ()
# # parentify/__init__.py
# from __future__ import absolute_import, unicode_literals

# # Это гарантирует, что Celery app будет загружена при запуске Django
# from celery_app import app as celery_app

# __all__ = ('celery_app',)

# # Явно импортируем задачи
