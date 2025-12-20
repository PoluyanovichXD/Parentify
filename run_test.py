# run_test.py
import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parentify.settings')
os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

try:
    from configurations import importer
    importer.install()
except ImportError:
    pass

django.setup()

# Импортируем задачу и запускаем
from parentify.tasks import send_test_email

print("Запускаем тестовую задачу...")
result = send_test_email.delay("d.polyunovich@gmail.com", "Тест из Python скрипта")
print(f"Задача запущена: {result.id}")
print(f"Результат (через get): {result.get(timeout=30)}")  # Ждем 30 секунд