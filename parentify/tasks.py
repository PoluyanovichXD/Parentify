from celery import shared_task  # ИСПОЛЬЗУЙТЕ ЭТОТ ИМПОРТ
from django.utils import timezone
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import logging
from datetime import datetime
import os
import sys

# Устанавливаем переменные окружения для django-configurations
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parentify.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Base')

# Добавляем текущую директорию в путь
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Устанавливаем django-configurations импортер
from configurations import importer
importer.install()

# Теперь импортируем Django
import django
django.setup()

# Теперь импортируем остальное
from parentify.models.models import Reminder, User
from django.core.mail import send_mail
from django.conf import settings

logger = logging.getLogger(__name__)

# Настройка подключения к базе данных
DATABASE_URL = settings.DATABASE_CONNECTION_STRING
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)

@shared_task
def check_and_send_reminders():
    """
    Проверяет и отправляет напоминания, которые подошли по времени.
    Эта задача выполняется каждую минуту по расписанию Celery Beat.
    """
    logger.info("Запуск проверки напоминаний...")
    
    try:
        db = SessionLocal()
        now = timezone.now()
        
        # Находим напоминания для отправки
        reminders = db.query(Reminder).filter(
            Reminder.scheduled_datetime <= now,
            Reminder.is_sent == False
        ).all()
        
        logger.info(f"Найдено {len(reminders)} напоминаний для отправки")
        
        for reminder in reminders:
            try:
                # Получаем пользователя для этого напоминания
                user = db.query(User).filter(User.id == reminder.user_id).first()
                
                if user and user.email:
                    # Отправляем email пользователю
                    send_reminder_email.delay(
                        reminder_id=reminder.id,
                        user_email=user.email,
                        message=reminder.message
                    )
                    
                    # Помечаем как отправленное
                    reminder.is_sent = True
                    db.commit()
                    
                    logger.info(f"Напоминание {reminder.id} отправлено пользователю {user.email}")
                else:
                    logger.warning(f"У пользователя {reminder.user_id} нет email или пользователь не найден")
                    reminder.is_sent = True  # Все равно помечаем, чтобы не проверять снова
                    db.commit()
                
            except Exception as e:
                logger.error(f"Ошибка при обработке напоминания {reminder.id}: {str(e)}")
                db.rollback()
        
        db.close()
        
    except Exception as e:
        logger.error(f"Ошибка в check_and_send_reminders: {str(e)}")
    
    return f"Обработано {len(reminders)} напоминаний"

@shared_task
def send_reminder_email(reminder_id, user_email, message):
    """
    Задача для отправки конкретного напоминания по email.
    """
    logger.info(f"Отправка email напоминания {reminder_id} на адрес {user_email}")
    
    try:
        # Проверяем, что email настройки есть
        if not all([
            hasattr(settings, 'EMAIL_HOST_USER'),
            hasattr(settings, 'DEFAULT_FROM_EMAIL') or hasattr(settings, 'EMAIL_HOST_USER')
        ]):
            logger.error("Email настройки не сконфигурированы")
            return False
        
        # Формируем тему и сообщение
        subject = f"🔔 Напоминание #{reminder_id}"
        
        # Форматируем сообщение
        email_message = f"""
        Здравствуйте!
        
        Это напоминание от Parentify:
        
        {message}
        
        ---
        Это автоматическое сообщение, пожалуйста, не отвечайте на него.
        """
        
        # Отправляем email
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', settings.EMAIL_HOST_USER)
        
        send_mail(
            subject=subject,
            message=email_message.strip(),
            from_email=from_email,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        # Логируем успешную отправку
        logger.info(f"Email напоминания {reminder_id} успешно отправлен на {user_email}")
        
        # Записываем в лог-файл (опционально)
        try:
            with open('email_reminders.log', 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                f.write(f"[{timestamp}] Напоминание #{reminder_id} отправлено на {user_email}: {message[:100]}...\n")
        except Exception as log_error:
            logger.warning(f"Не удалось записать в лог-файл: {str(log_error)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки email напоминания {reminder_id}: {str(e)}")
        
        # Можно добавить повторную попытку с задержкой
        # send_reminder_email.retry(exc=e, countdown=60)  # Повторить через 60 секунд
        
        return False

@shared_task
def send_test_email(user_email, message="Тестовое напоминание"):
    """
    Тестовая задача для проверки отправки email.
    """
    logger.info(f"Отправка тестового email на {user_email}")
    
    try:
        subject = "📧 Тестовое письмо от Parentify"
        
        email_message = f"""
        Это тестовое сообщение для проверки работы системы напоминаний:
        
        {message}
        
        Если вы получили это письмо, значит email уведомления работают корректно.
        """
        
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', getattr(settings, 'EMAIL_HOST_USER', 'noreply@parentify.com'))
        
        send_mail(
            subject=subject,
            message=email_message.strip(),
            from_email=from_email,
            recipient_list=[user_email],
            fail_silently=False,
        )
        
        logger.info(f"Тестовый email успешно отправлен на {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки тестового email: {str(e)}")
        return False