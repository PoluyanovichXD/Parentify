# parentify/tasks.py
import os
import sys

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
        from parentify.models.models import Reminder, User
        
        # Настройка подключения к базе данных
        # Используем настройки из Django или локальные настройки
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
                    # Отправляем email через отдельную задачу
                    send_reminder_email.apply_async(
                        args=[reminder.id, user.email, reminder.message],
                        countdown=1  # Небольшая задержка
                    )
                    
                    # Помечаем как отправленное
                    reminder.is_sent = True
                    db.commit()
                    
                    logger.info(f"Задача отправки напоминания {reminder.id} поставлена в очередь")
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
        # Можно добавить детальную информацию об ошибке
        import traceback
        logger.error(f"Трассировка: {traceback.format_exc()}")
    
    return f"Обработано {len(reminders)} напоминаний"
@shared_task(bind=True, max_retries=3)
def send_reminder_email(self, reminder_id, user_email, message, children_id=None):
    """
    Отправляет конкретное напоминание по email с учетом связи с ребенком.
    """
    logger.info(f"Отправка email напоминания {reminder_id} на {user_email}, children_id: {children_id}")
    
    try:
        # Получаем информацию о пользователе и ребенке из базы данных
        from sqlalchemy import create_engine
        from sqlalchemy.orm import sessionmaker
        
        # Импортируем модели здесь, чтобы избежать циклических импортов
        from parentify.models import db, User, UserChild
        
        # Создаем сессию для работы с базой данных
        engine = create_engine(settings.DATABASE_CONNECTION_STRING)
        Session = sessionmaker(bind=engine)
        session = Session()
        
        user = None
        child = None
        
        try:
            # Находим пользователя по email
            user = session.query(User).filter_by(email=user_email).first()
            
            # Если напоминание связано с ребенком, находим информацию о ребенке
            if children_id:
                child = session.query(UserChild).filter_by(id=children_id).first()
                
                # Проверяем, принадлежит ли ребенок этому пользователю
                if child and child.user_id != user.id:
                    child = None  # Ребенок не принадлежит пользователю
                    logger.warning(f"Ребенок с ID {children_id} не принадлежит пользователю {user_email}")
                    
        except Exception as db_error:
            logger.error(f"Ошибка при получении данных из БД: {str(db_error)}")
        finally:
            session.close()
        
        # Проверяем настройки email
        email_host_user = getattr(settings, 'EMAIL_HOST_USER', None)
        email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
        logger.debug(f"EMAIL_HOST_USER: {email_host_user}")
        logger.debug(f"EMAIL_HOST_PASSWORD: {'*' * len(email_host_password) if email_host_password else 'None'}")
        
        if not email_host_user:
            logger.error("EMAIL_HOST_USER не настроен")
            return False
        
        # Формируем тему и сообщение в зависимости от типа напоминания
        if child:
            # Напоминание связано с ребенком
            subject = f"👶 Напоминание для {child.first_name} от Parentify"
            
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
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>👶 Parentify Reminder</h2>
                </div>
                
                <p>Здравствуйте, <strong>{user.first_name if user else 'уважаемый пользователь'}</strong>!</p>
                
                <div class="child-info">
                    <h3>💝 Напоминание для вашего ребенка:</h3>
                    <p><strong>Имя:</strong> <span class="child-name">{child.first_name} {child.last_name}</span></p>
                    <p><strong>Возраст:</strong> {child.birth_year} лет</p>
                    <p><strong>Пол:</strong> {child.gender_name}</p>
                    <p><strong>Знак зодиака:</strong> {child.zodiac_sign}</p>
                </div>
                
                <div class="reminder-message">
                    <h3>📝 Сообщение напоминания:</h3>
                    <p>{message}</p>
                </div>
                
                <p>Берегите себя и своих близких! ❤️</p>
                
                <div class="footer">
                    <p>Это автоматическое сообщение от Parentify.</p>
                    <p>ID напоминания: {reminder_id}</p>
                    <p>Дата отправки: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                    <p>Пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </body>
            </html>
            """
        else:
            # Личное напоминание пользователя
            subject = f"🔔 Личное напоминание от Parentify"
            
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
                </style>
            </head>
            <body>
                <div class="header">
                    <h2>🔔 Parentify Reminder</h2>
                </div>
                
                <div class="user-info">
                    <h3>👤 Ваше личное напоминание</h3>
                    <p><strong>Получатель:</strong> <span class="user-name">{user.first_name if user else 'уважаемый пользователь'} {user.last_name if user else ''}</span></p>
                    {f'<p><strong>Email:</strong> {user_email}</p>' if user else ''}
                    {f'<p><strong>Знак зодиака:</strong> {user.zodiac_sign}</p>' if user and user.zodiac_sign else ''}
                </div>
                
                <div class="reminder-message">
                    <h3>📝 Сообщение напоминания:</h3>
                    <p>{message}</p>
                </div>
                
                <p>Помните о важных моментах в своей жизни! 💪</p>
                
                <div class="footer">
                    <p>Это автоматическое сообщение от Parentify.</p>
                    <p>ID напоминания: {reminder_id}</p>
                    <p>Дата отправки: {datetime.now().strftime('%d.%m.%Y %H:%M')}</p>
                    <p>Пожалуйста, не отвечайте на это письмо.</p>
                </div>
            </body>
            </html>
            """
        
        # Определяем from_email
        from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', email_host_user)
        logger.debug(f"FROM_EMAIL: {from_email}")
        
        # Отправляем email с HTML оформлением
        logger.debug(f"Отправка письма: subject={subject}, to={user_email}")
        
        try:
            # Создаем email сообщение с HTML
            email = EmailMultiAlternatives(
                subject=subject,
                body=f"Напоминание: {message}\n\nЭто автоматическое сообщение от Parentify. ID: {reminder_id}",
                from_email=from_email,
                to=[user_email]
            )
            
            # Прикрепляем HTML версию
            email.attach_alternative(email_message, "text/html")
            
            # Отправляем
            email.send(fail_silently=False)
            
            logger.info(f"Email напоминания {reminder_id} успешно отправлен на {user_email}")
            
            # Логируем тип напоминания
            reminder_type = "детское" if child else "личное"
            logger.info(f"Тип напоминания: {reminder_type}")
            
        except Exception as send_error:
            logger.error(f"Ошибка при отправке email: {str(send_error)}")
            import traceback
            logger.error(f"Трассировка send_mail: {traceback.format_exc()}")
            raise  # Повторно поднимаем исключение для обработки в основном блоке
        
        # Логируем в файл с указанием типа
        try:
            log_file = os.path.join(settings.BASE_DIR, 'email_reminders.log')
            with open(log_file, 'a', encoding='utf-8') as f:
                timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                reminder_type = "детское" if child else "личное"
                f.write(f"[{timestamp}] {reminder_type.capitalize()} напоминание #{reminder_id} отправлено на {user_email}\n")
        except Exception as log_error:
            logger.warning(f"Не удалось записать в лог-файл: {str(log_error)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Ошибка отправки email напоминания {reminder_id}: {str(e)}")
        import traceback
        logger.error(f"Полная трассировка ошибки:\n{traceback.format_exc()}")
        
        # Пытаемся повторить через 60 секунд
        try:
            logger.info(f"Повторная попытка отправки через 60 секунд...")
            raise self.retry(exc=e, countdown=60)
        except Exception:
            # Если превышено количество попыток, возвращаем False
            logger.error(f"Превышено максимальное количество попыток отправки")
            return False
# @shared_task(bind=True, max_retries=3)
# def send_reminder_email(self, reminder_id, user_email, message):
#     """
#     Отправляет конкретное напоминание по email.
#     """
#     logger.info(f"Отправка email напоминания {reminder_id} на {user_email}")
    
#     try:
#         # Проверяем настройки email
#         email_host_user = getattr(settings, 'EMAIL_HOST_USER', None)
#         email_host_password = getattr(settings, 'EMAIL_HOST_PASSWORD', None)
        
#         logger.debug(f"EMAIL_HOST_USER: {email_host_user}")
#         logger.debug(f"EMAIL_HOST_PASSWORD: {'*' * len(email_host_password) if email_host_password else 'None'}")
#         logger.debug(f"EMAIL_HOST: {getattr(settings, 'EMAIL_HOST', None)}")
#         logger.debug(f"EMAIL_PORT: {getattr(settings, 'EMAIL_PORT', None)}")
        
#         if not email_host_user:
#             logger.error("EMAIL_HOST_USER не настроен")
#             return False
        
#         # Формируем тему и сообщение
#         subject = f"🔔 Напоминание #{reminder_id}"
        
#         email_message = f"""
#         Здравствуйте!
        
#         Это напоминание от Parentify:
        
#         {message}
        
#         ---
#         Это автоматическое сообщение, пожалуйста, не отвечайте на него.
#         """
        
#         # Определяем from_email
#         from_email = getattr(settings, 'DEFAULT_FROM_EMAIL', email_host_user)
#         logger.debug(f"FROM_EMAIL: {from_email}")
        
#         # Отправляем email с детальной отладкой
#         logger.debug(f"Отправка письма: subject={subject}, to={user_email}")
        
#         try:
#             send_mail(
#                 subject=subject,
#                 message=email_message.strip(),
#                 from_email=from_email,
#                 recipient_list=[user_email],
#                 fail_silently=False,
#             )
#             logger.info(f"Email напоминания {reminder_id} успешно отправлен на {user_email}")
            
#         except Exception as send_error:
#             logger.error(f"Ошибка при вызове send_mail: {str(send_error)}")
#             import traceback
#             logger.error(f"Трассировка send_mail: {traceback.format_exc()}")
#             raise  # Повторно поднимаем исключение для обработки в основном блоке
        
#         # Логируем в файл
#         try:
#             log_file = os.path.join(settings.BASE_DIR, 'email_reminders.log')
#             with open(log_file, 'a', encoding='utf-8') as f:
#                 timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
#                 f.write(f"[{timestamp}] Напоминание #{reminder_id} отправлено на {user_email}\n")
#         except Exception as log_error:
#             logger.warning(f"Не удалось записать в лог-файл: {str(log_error)}")
        
#         return True
        
#     except Exception as e:
#         logger.error(f"Ошибка отправки email напоминания {reminder_id}: {str(e)}")
#         import traceback
#         logger.error(f"Полная трассировка ошибки:\n{traceback.format_exc()}")
        
#         # Пытаемся повторить через 60 секунд
#         try:
#             logger.info(f"Повторная попытка отправки через 60 секунд...")
#             raise self.retry(exc=e, countdown=60)
#         except Exception:
#             # Если превышено количество попыток, возвращаем False
#             logger.error(f"Превышено максимальное количество попыток отправки")
#             return False
    
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