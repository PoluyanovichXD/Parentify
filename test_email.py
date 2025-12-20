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