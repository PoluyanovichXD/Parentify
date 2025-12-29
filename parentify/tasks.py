# parentify/tasks.py
import os
import sys
import json

# Добавьте эту проверку в самое начало файла
if os.environ.get('CELERY_LOADING', False):
    # Если Celery уже загружает задачи, не импортируем ничего
    pass
else:
    # Устанавливаем флаг, чтобы предотвратить рекурсию
    os.environ['CELERY_LOADING'] = 'True'
    
    # Остальной код импортов и функций...
    import logging
    from datetime import datetime
    from celery import shared_task
    from django.utils import timezone
    from django.core.mail import send_mail
    from django.conf import settings
    from django.core.mail import EmailMessage, EmailMultiAlternatives

    logger = logging.getLogger(__name__)

@shared_task
def check_and_send_reminders():
    """
    Проверяет и отправляет напоминания, которые подошли по времени.
    """
    logger.info("Запуск проверки напоминаний...")
    
    # Инициализируем переменную reminders на случай ошибки
    reminders = []
    
    try:
        # Импортируем здесь, чтобы избежать проблем с загрузкой Django
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        from parentify.models.models import Reminder, User, UserChild
        
        # Настройка подключения к базе данных
        database_url = getattr(settings, 'DATABASE_CONNECTION_STRING', 
                             'postgresql+psycopg2://postgres:postgres@localhost/parentify_db')
        
        # Заменяем хост 'database' на 'localhost' если нужно
        if 'database' in database_url:
            database_url = database_url.replace('database', 'localhost')
        
        engine = create_engine(database_url)
        SessionLocal = sessionmaker(bind=engine)
        
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
                # Получаем пользователя
                user = db.query(User).filter(User.id == reminder.user_id).first()
                
                if user and user.email:
                    # Получаем ребенка, если есть
                    child = None
                    if reminder.children_id:
                        child = db.query(UserChild).filter_by(id=reminder.children_id).first()
                    
                    # Создаем словари с данными для передачи в задачу
                    reminder_data = {
                        'id': reminder.id,
                        'name': reminder.name,
                        'message': reminder.message,
                        'scheduled_datetime': reminder.scheduled_datetime.isoformat(),
                        'children_id': reminder.children_id
                    }
                    
                    user_data = {
                        'id': user.id,
                        'email': user.email,
                        'first_name': user.first_name,
                        'last_name': user.last_name,
                        'zodiac_sign': user.zodiac_sign
                    }
                    
                    child_data = None
                    if child:
                        child_data = {
                            'id': child.id,
                            'first_name': child.first_name,
                            'last_name': child.last_name,
                            'birth_year': child.birth_year,
                            'gender_name': child.gender_name,
                            'zodiac_sign': child.zodiac_sign
                        }
                    
                    # Отправляем email через отдельную задачу с данными
                    send_reminder_email.apply_async(
                        args=[reminder_data, user_data, child_data],
                        countdown=1  # Небольшая задержка
                    )
                    
                    # Помечаем как отправленное
                    reminder.is_sent = True
                    db.commit()
                    
                    logger.info(f"Задача отправки напоминания {reminder.id} поставлена в очередь")
                    logger.info(f"Тип: {'детское' if child else 'личное'}")
                    
                else:
                    logger.warning(f"У пользователя {reminder.user_id} нет email")
                    reminder.is_sent = True  # Помечаем, чтобы не проверять снова
                    db.commit()
                
            except Exception as e:
                logger.error(f"Ошибка при обработке напоминания {reminder.id}: {str(e)}")
                db.rollback()
        
        db.close()
        
    except Exception as e:
        logger.error(f"Ошибка в check_and_send_reminders: {str(e)}")
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
    
    return f"Обработано {len(reminders)} напоминаний"

@shared_task(bind=True, max_retries=3)
def send_reminder_email(self, reminder_data, user_data, child_data=None):
    """
    Отправляет конкретное напоминание по email с учетом связи с ребенком.
    Принимает данные в виде словарей, а не объекты SQLAlchemy.
    """
    logger.info("=" * 50)
    logger.info(f"НАЧАЛО ОТПРАВКИ EMAIL НАПОМИНАНИЯ")
    logger.info(f"Reminder ID: {reminder_data.get('id')}")
    logger.info(f"User email: {user_data.get('email')}")
    logger.info(f"Child data: {'присутствует' if child_data else 'отсутствует'}")
    logger.info("=" * 50)
    
    try:
        # Извлекаем данные из словарей
        reminder_id = reminder_data.get('id')
        reminder_name = reminder_data.get('name', 'Напоминание')
        message = reminder_data.get('message', '')
        
        user_email = user_data.get('email')
        user_first_name = user_data.get('first_name', 'уважаемый пользователь')
        user_last_name = user_data.get('last_name', '')
        user_zodiac_sign = user_data.get('zodiac_sign')
        
        # Получаем текущую дату и время для использования в шаблоне
        current_datetime = datetime.now()
        current_year = current_datetime.year
        send_date_str = current_datetime.strftime('%d.%m.%Y %H:%M')
        log_timestamp = current_datetime.strftime('%Y-%m-%d %H:%M:%S')
        
        # Проверяем настройки email
        email_host_user = getattr(settings, 'EMAIL_HOST_USER', None)
        email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
        if not email_host_user:
            logger.error("EMAIL_HOST_USER не настроен")
            return False
        
        # Формируем тему и сообщение в зависимости от типа напоминания
        if child_data:
            # Напоминание связано с ребенком
            child_first_name = child_data.get('first_name', '')
            child_last_name = child_data.get('last_name', '')
            child_birth_year = child_data.get('birth_year')
            child_gender_name = child_data.get('gender_name', 'не указан')
            child_zodiac_sign = child_data.get('zodiac_sign', 'не указан')
            
            # Рассчитываем возраст ребенка
            child_age = current_year - child_birth_year if child_birth_year else "не указан"
            
            subject = f"👶 {reminder_name} - напоминание для {child_first_name}"
            
            email_message = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #4CAF50;
                        color: white;
                        padding: 20px;
                        border-radius: 5px;
                        text-align: center;
                    }}
                    .reminder-title {{
                        color: #2c3e50;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 15px 0;
                        text-align: center;
                    }}
                    .child-info {{
                        background-color: #f0f8ff;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        border-left: 4px solid #4CAF50;
                    }}
                    .reminder-message {{
                        background-color: #fff8e1;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                        border: 1px solid #ffd54f;
                        font-size: 16px;
                        line-height: 1.8;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        color: #666;
                        font-size: 12px;
                    }}
                    .child-name {{
                        color: #4CAF50;
                        font-weight: bold;
                    }}
                    .reminder-name {{
                        color: #e74c3c;
                        font-weight: bold;
                        font-size: 18px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>👶 Parentify уведомление</h2>
                </div>
                
                <div class="reminder-title">
                    Напоминание: <span class="reminder-name">"{reminder_name}"</span>
                </div>
                
                <p>Здравствуйте, <strong>{user_first_name}</strong>!</p>
                
                <div class="child-info">
                    <h3>💝 Для вашего ребенка:</h3>
                    <p><strong>Имя:</strong> <span class="child-name">{child_first_name} {child_last_name}</span></p>
                    <p><strong>Возраст:</strong> {child_age} лет</p>
                    <p><strong>Пол:</strong> {child_gender_name}</p>
                    <p><strong>Знак зодиака:</strong> {child_zodiac_sign}</p>
                </div>
                
                <div class="reminder-message">
                    <h3>📝 Сообщение:</h3>
                    <p>{message}</p>
                </div>
                
                <p>Берегите себя и своих близких! ❤️</p>
                
                <div class="footer">
                    <p>Это автоматическое сообщение от Parentify.</p>
                    <p>Название напоминания: {reminder_name}</p>
                    <p>ID напоминания: {reminder_id}</p>
                    <p>Дата отправки: {send_date_str}</p>
                    <p>Пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </body>
            </html>
            """
        else:
            # Личное напоминание пользователя
            subject = f"🔔 {reminder_name} - ваше напоминание"
            
            zodiac_html = f'<p><strong>Знак зодиака:</strong> {user_zodiac_sign}</p>' if user_zodiac_sign else ''
            
            email_message = f"""
            <html>
            <head>
                <style>
                    body {{
                        font-family: Arial, sans-serif;
                        line-height: 1.6;
                        color: #333;
                        max-width: 600px;
                        margin: 0 auto;
                        padding: 20px;
                    }}
                    .header {{
                        background-color: #2196F3;
                        color: white;
                        padding: 20px;
                        border-radius: 5px;
                        text-align: center;
                    }}
                    .reminder-title {{
                        color: #2c3e50;
                        font-size: 20px;
                        font-weight: bold;
                        margin: 15px 0;
                        text-align: center;
                    }}
                    .user-info {{
                        background-color: #e3f2fd;
                        padding: 15px;
                        border-radius: 5px;
                        margin: 20px 0;
                        border-left: 4px solid #2196F3;
                    }}
                    .reminder-message {{
                        background-color: #fff8e1;
                        padding: 20px;
                        border-radius: 5px;
                        margin: 20px 0;
                        border: 1px solid #ffd54f;
                        font-size: 16px;
                        line-height: 1.8;
                    }}
                    .footer {{
                        margin-top: 30px;
                        padding-top: 20px;
                        border-top: 1px solid #eee;
                        color: #666;
                        font-size: 12px;
                    }}
                    .user-name {{
                        color: #2196F3;
                        font-weight: bold;
                    }}
                    .reminder-name {{
                        color: #e74c3c;
                        font-weight: bold;
                        font-size: 18px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🔔 Parentify уведомление</h2>
                </div>
                
                <div class="reminder-title">
                    Напоминание: <span class="reminder-name">"{reminder_name}"</span>
                </div>
                
                <div class="user-info">
                    <h3>👤 Для вас:</h3>
                    <p><strong>Получатель:</strong> <span class="user-name">{user_first_name} {user_last_name}</span></p>
                    <p><strong>Email:</strong> {user_email}</p>
                    {zodiac_html}
                </div>
                
                <div class="reminder-message">
                    <h3>📝 Сообщение:</h3>
                    <p>{message}</p>
                </div>
                
                <p>Помните о важных моментах в своей жизни! 💪</p>
                
                <div class="footer">
                    <p>Это автоматическое сообщение от Parentify.</p>
                    <p>Название напоминания: {reminder_name}</p>
                    <p>ID напоминания: {reminder_id}</p>
                    <p>Дата отправки: {send_date_str}</p>
                    <p>Пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </body>
            </html>
            """
        
        # Определяем from_email
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', email_host_user)
        
        try:
            # Создаем email сообщение с HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"Напоминание \"{reminder_name}\": {message}\n\nЭто автоматическое сообщение от Parentify. ID: {reminder_id}",
                from_email=from_email,
                to=[user_email]
            )
            
            # Прикрепляем HTML версию
            email.attach_alternative(email_message, "text/html")
            
            # Отправляем
            email.send(fail_silently=False)
            
            logger.info(f"✓ Email напоминания \"{reminder_name}\" (ID: {reminder_id}) успешно отправлен на {user_email}")
            
            # Логируем тип напоминания
            reminder_type = "детское" if child_data else "личное"
            logger.info(f"Тип напоминания: {reminder_type}")
            
        except Exception as send_error:
            logger.error(f"✗ Ошибка при отправке email: {str(send_error)}")
            import traceback
            logger.error(f"Трассировка send_mail: {traceback.format_exc()}")
            raise
        
        # Логируем в файл с указанием типа
        try:
            log_file = os.path.join(settings.BASE_DIR, 'email_reminders.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                reminder_type = "детское" if child_data else "личное"
                child_name = f" ({child_data.get('first_name', '')})" if child_data else ""
                f.write(f"[{log_timestamp}] {reminder_type.capitalize()} напоминание \"{reminder_name}\"{child_name} (#{reminder_id}) отправлено на {user_email}\n")
        except Exception as log_error:
            logger.warning(f"Не удалось записать в лог-файл: {str(log_error)}")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Ошибка отправки email напоминания: {str(e)}")
        import traceback
        logger.error(f"Полная трассировка ошибки:\n{traceback.format_exc()}")
        
        # Пытаемся повторить через 60 секунд
        try:
            logger.info(f"Повторная попытка отправки через 60 секунд...")
            raise self.retry(exc=e, countdown=60)
        except Exception:
            logger.error(f"Превышено максимальное количество попыток отправки")
            return False

@shared_task(bind=True)
def send_test_email(self, user_email, message="Тестовое напоминание"):
    """
    Тестовая задача для проверки отправки email.
    """
    logger.info("=" * 50)
    logger.info(f"НАЧАЛО ОТПРАВКИ ТЕСТОВОГО EMAIL НА {user_email}")
    logger.info("=" * 50)
    
    print("\n" + "="*50)
    print("НАСТРОЙКИ EMAIL В CELERY:")
    print("="*50)
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_HOST_PASSWORD ДЛИНА: {len(settings.EMAIL_HOST_PASSWORD) if settings.EMAIL_HOST_PASSWORD else 0}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', 'Не настроено')}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', 'Не настроено')}")
    print(f"DEFAULT_FROM_EMAIL: {getattr(settings, 'DEFAULT_FROM_EMAIL', 'Не настроено')}")
    
    try:
        # ПРОСТОЕ ПИСЬМО БЕЗ HTML
        subject = "Тест от Parentify"
        email_message = f"Тестовое сообщение: {message}"
        
        print(f"\nОтправка письма:")
        print(f"  От: {settings.EMAIL_HOST_USER}")
        print(f"  Кому: {user_email}")
        print(f"  Тема: {subject}")
        print(f"  Сообщение: {email_message}")
        
        # ВАЖНО: Добавляем таймаут для email
        import socket
        socket.setdefaulttimeout(10)  # 10 секунд таймаут
        
        # ОТПРАВЛЯЕМ ПИСЬМО С БОЛЬШЕЙ ОТЛАДКОЙ
        print(f"\nПопытка отправки...")
        
        from django.core.mail import get_connection
        
        try:
            # Создаем соединение вручную для лучшей отладки
            connection = get_connection(
                backend='django.core.mail.backends.smtp.EmailBackend',
                fail_silently=False,
                timeout=10
            )
            
            # Открываем соединение
            connection.open()
            print("✓ SMTP соединение открыто")
            
            email = EmailMessage(
                subject=subject,
                body=email_message,
                from_email=settings.EMAIL_HOST_USER,
                to=[user_email],
                connection=connection,
            )
            
            result = email.send()
            print(f"✓ Результат отправки: {result}")
            
            # Закрываем соединение
            connection.close()
            print("✓ Соединение закрыто")
            
        except Exception as send_error:
            print(f"✗ Ошибка при отправке: {send_error}")
            import traceback
            traceback.print_exc()
            raise
        
        print(f"\n✓ Письмо отправлено! Результат: {result}")
        
        logger.info(f"✓ Email отправлен успешно! Результат: {result}")
        return f"Успешно отправлено! Результат: {result}"
        
    except Exception as e:
        print(f"\n✗ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()  # Вывод в консоль
        
        logger.error(f"✗ Ошибка: {e}")
        logger.error(f"Трассировка:\n{traceback.format_exc()}")
        
        return f"Ошибка: {e}"