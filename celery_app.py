# celery_app.py
import os
import sys

# Устанавливаем переменные окружения ДО любого импорта Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parentify.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')

# Добавляем родительскую директорию в путь Python
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# Устанавливаем django-configurations импортер
try:
    from configurations import importer
    importer.install()
except ImportError:
    pass

# Теперь импортируем Django
import django
django.setup()

# Теперь импортируем Celery
from celery import Celery

# Создаем экземпляр Celery с именем проекта
app = Celery('parentify')

# Загружаем настройки из Django settings
from django.conf import settings

# Используем настройки из Django
app.config_from_object('django.conf:settings', namespace='CELERY')

# УБРАТЬ этот блок - он вызывает рекурсию:
# try:
#     # Импортируем задачи
#     from parentify import tasks
#     print(f"✓ Импортированы задачи из parentify.tasks")
#     
#     # Регистрируем задачи вручную
#     app.tasks.register(tasks.check_and_send_reminders)
#     app.tasks.register(tasks.send_reminder_email)
#     app.tasks.register(tasks.send_test_email)
#     print(f"✓ Задачи зарегистрированы вручную")
#     
# except ImportError as e:
#     print(f"✗ Ошибка импорта задач: {e}")
#     import traceback
#     traceback.print_exc()

# Вместо этого просто используйте автообнаружение
app.autodiscover_tasks(['parentify'])

@app.task(bind=True, name='debug_task')
def debug_task(self):
    print(f'Request: {self.request!r}')
    return "Debug task executed"

# Экспортируем app
__all__ = ['app']