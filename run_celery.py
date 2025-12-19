# celery_app.py (упрощенный)
import os
import sys

# Устанавливаем переменные окружения
os.environ['DJANGO_SETTINGS_MODULE'] = 'parentify.settings'
os.environ['DJANGO_CONFIGURATION'] = 'Base'

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем django-configurations импортер
from configurations import importer
importer.install()

# Импортируем Django
import django
django.setup()

# Теперь импортируем Celery
from celery import Celery

# Создаем экземпляр Celery
app = Celery('parentify')

# Загружаем настройки из Django settings
from django.conf import settings

# Настройки Celery
app.conf.update(
    broker_url='redis://localhost:6379/0',
    result_backend='redis://localhost:6379/0',
    broker_connection_retry_on_startup=True,
    timezone='Europe/Moscow',
    enable_utc=False,
)

# Загружаем расписание из настроек Django если есть
if hasattr(settings, 'CELERY_BEAT_SCHEDULE'):
    app.conf.beat_schedule = settings.CELERY_BEAT_SCHEDULE
else:
    # Дефолтное расписание
    app.conf.beat_schedule = {
        'check-reminders': {
            'task': 'parentify.tasks.check_and_send_reminders',
            'schedule': 30.0,
        },
    }

# ВАЖНО: Убираем явную регистрацию задач - пусть Celery сам находит их
# Не вызываем app.tasks.register() вручную
# Celery сам найдет задачи через @shared_task декоратор

# Автообнаружение задач
app.autodiscover_tasks(['parentify'])

print("Celery app configured successfully")