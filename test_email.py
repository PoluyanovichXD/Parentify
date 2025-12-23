# # test_mailru.py
# import smtplib
# import ssl

# print("="*60)
# print("ТЕСТ ПОДКЛЮЧЕНИЯ К MAIL.RU")
# print("="*60)

# # Настройки
# smtp_server = "smtp.mail.ru"
# port = 465  # Пробуем порт 465 с SSL
# username = "svetomir_send_2023@mail.ru"  # ЗАМЕНИТЕ НА ВАШ
# password = "cdtnjvbh,fq"  # ЗАМЕНИТЕ НА ВАШ

# print(f"Сервер: {smtp_server}")
# print(f"Порт: {port}")
# print(f"Логин: {username}")

# # Тестируем разные порты
# ports_to_test = [
#     (465, True, False),   # SSL
#     (587, False, True),   # TLS
#     (25, False, False),   # Обычный SMTP
# ]

# for port_num, use_ssl, use_tls in ports_to_test:
#     print(f"\n{'='*40}")
#     print(f"Тест порта {port_num} (SSL: {use_ssl}, TLS: {use_tls})")
#     print(f"{'='*40}")
    
#     try:
#         if use_ssl:
#             # SSL соединение
#             context = ssl.create_default_context()
#             with smtplib.SMTP_SSL(smtp_server, port_num, context=context, timeout=10) as server:
#                 print(f"✓ Подключено к {smtp_server}:{port_num} через SSL")
#                 server.login(username, password)
#                 print("✓ Аутентификация успешна")
                
#                 # Тест отправки
#                 test_msg = f"""From: {username}
# To: {username}
# Subject: Тест Mail.ru SMTP

# Это тестовое письмо от Mail.ru SMTP."""
                
#                 server.sendmail(username, username, test_msg)
#                 print("✓ Письмо отправлено!")
#                 print(f"\n✅ ПОРТ {port_num} РАБОТАЕТ!")
#                 break
                
#         else:
#             # Обычное или TLS соединение
#             with smtplib.SMTP(smtp_server, port_num, timeout=10) as server:
#                 print(f"✓ Подключено к {smtp_server}:{port_num}")
                
#                 if use_tls:
#                     server.starttls()
#                     print("✓ TLS включен")
                
#                 server.login(username, password)
#                 print("✓ Аутентификация успешна")
                
#                 # Тест отправки
#                 test_msg = f"""From: {username}
# To: {username}
# Subject: Тест Mail.ru SMTP

# Это тестовое письмо от Mail.ru SMTP."""
                
#                 server.sendmail(username, username, test_msg)
#                 print("✓ Письмо отправлено!")
#                 print(f"\n✅ ПОРТ {port_num} РАБОТАЕТ!")
#                 break
                
#     except Exception as e:
#         print(f"✗ Ошибка порта {port_num}: {type(e).__name__}: {e}")
#         continue

# print("\n" + "="*60)
# print("ТЕСТ ЗАВЕРШЕН")
# print("="*60)



# test_gmail_ssl.py
import smtplib
import ssl

smtp_server = "smtp.gmail.com"
port = 465  # Используем порт 465 вместо 587
sender_email = "parentify.official@gmail.com"
password = "jthuekzdqzdgjxls"

print("="*60)
print("ТЕСТ GMAIL С SSL (ПОРТ 465)")
print("="*60)

try:
    # Создаем SSL контекст
    context = ssl.create_default_context()
    
    print(f"Подключение к {smtp_server}:{port} через SSL...")
    
    # Используем SMTP_SSL для порта 465
    with smtplib.SMTP_SSL(smtp_server, port, context=context, timeout=10) as server:
        print("✓ Подключение установлено")
        
        print("Аутентификация...")
        server.login(sender_email, password)
        print("✓ Аутентификация успешна!")
        
        print("Тест отправки...")
        test_msg = """From: parentify.official@gmail.com
To: d.polyunovich@gmail.com
Subject: Тест через порт 465

Это тестовое письмо через порт 465."""
        
        server.sendmail(sender_email, "d.polyunovich@gmail.com", test_msg)
        print("✓ Письмо отправлено!")
        
    print("✓ Все тесты пройдены!")
    
except Exception as e:
    print(f"\n✗ ОШИБКА: {type(e).__name__}: {e}")
    
    # Пробуем другие порты
    print("\n" + "="*60)
    print("ПРОБУЕМ ДРУГИЕ ПОРТЫ:")
    print("="*60)
    
    for test_port in [25, 2525, 587, 465]:
        try:
            print(f"\nПорт {test_port}: ", end="")
            if test_port == 465:
                with smtplib.SMTP_SSL(smtp_server, test_port, timeout=5) as s:
                    print("Доступен (SSL)")
            else:
                with smtplib.SMTP(smtp_server, test_port, timeout=5) as s:
                    print("Доступен")
        except:
            print("Недоступен")
    
    import traceback
    traceback.print_exc()