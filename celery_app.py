# celery_app.py (полностью замените содержимое)
import os
import sys

# Устанавливаем переменные окружения ДО любого импорта Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parentify.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')  # ВАЖНО!

# Добавляем текущую директорию в путь Python
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем django-configurations импортер
from configurations import importer
importer.install()

# Теперь импортируем Django
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
    app.conf.beat_schedule = {
        'check-reminders': {
            'task': 'parentify.tasks.check_and_send_reminders',
            'schedule': 30.0,
        },
    }

# Явно импортируем и регистрируем задачи
try:
    from parentify.tasks import check_and_send_reminders, send_reminder_email, send_test_email
    app.tasks.register(check_and_send_reminders)
    app.tasks.register(send_reminder_email)
    app.tasks.register(send_test_email)
    print("Tasks registered successfully")
except ImportError as e:
    print(f"Warning: Could not import tasks: {e}")

# Также пробуем автообнаружение
app.autodiscover_tasks()