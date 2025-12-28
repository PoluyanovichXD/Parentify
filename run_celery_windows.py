# run_celery_windows.py
import os
import sys

if __name__ == '__main__':
    # Устанавливаем переменные окружения
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'parentify.settings')
    os.environ.setdefault('DJANGO_CONFIGURATION', 'Test')
    
    # Устанавливаем configurations
    from configurations import importer
    importer.install()
    
    # Импортируем приложение Celery
    from celery_app import app
    
    # Запускаем worker с параметрами для Windows
    argv = [
        'worker',
        '--loglevel=info',
        '--pool=solo',  # Используем solo pool для Windows
        '--concurrency=1',
        '--without-mingle',
        '--without-gossip',
    ]
    
    app.worker_main(argv)