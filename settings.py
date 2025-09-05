from configurations import Configuration
from pathlib import Path
import os
import django.core.mail.backends.smtp
import django.contrib.sessions.backends.signed_cookies
import django.contrib.sessions.backends.db

class Base(Configuration):

    SECRET_KEY = '_2(b2c_j$xb0ft4w&rp!bs=om7x5$9cnr8yd#!(d+rha$g%en*'

    PROJECT_ROOT = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
    BASE_DIR = Path(__file__).resolve().parent

    DATABASE_CONNECTION_STRING = 'postgresql+psycopg2://dev:dev@localhost/mishutka_web'
    CONFIG_NAME = 'Base'
    ALLOWED_HOSTS = ['*']

    LANGUAGE_CODE = 'ru'
    TIME_ZONE = 'UTC'
    DEBUG = True
    USE_I18N = True
    USE_L10N = True
    USE_TZ = True
    STATIC_URL = '/static/'
    CORS_ORIGIN_ALLOW_ALL = True
    CORS_ALLOW_CREDENTIALS = True
    USE_X_FORWARDED_HOST = True

    EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
    
    EMAIL_PORT = 587
    EMAIL_HOST = 'smtp.gmail.com'
    EMAIL_HOST_USER = 'mishutka@gmail.com'
    EMAIL_HOST_PASSWORD = 'wejtoerhgerg'

    @property
    def FROM_EMAIL(self):
        return os.getenv('EMAIL_HOST_USER',self.EMAIL_HOST_USER)

    INSTALLED_APPS = [
        'django.contrib.admin',
        'django.contrib.auth',
        'django.contrib.contenttypes',
        'django.contrib.sessions',
        'django.contrib.messages',
        'django.contrib.staticfiles',
        'django_user_agents',
        'rest_framework',
        'django_filters',
        'channels',
        'web',
        # 'bots',
        # 'models',

    ]

    DEFAULT_MIDDLEWARE = [
        'django.middleware.common.CommonMiddleware',
        'django.contrib.sessions.middleware.SessionMiddleware',
        'django.middleware.csrf.CsrfViewMiddleware',
        'django.contrib.auth.middleware.AuthenticationMiddleware',
        'django.contrib.messages.middleware.MessageMiddleware',
        'django_user_agents.middleware.UserAgentMiddleware',
        'web.middleware.BaseSessionMiddleware',
    ]
    MIDDLEWARE = DEFAULT_MIDDLEWARE

    ROOT_URLCONF = 'urls'

    MEDIA_ROOT = os.path.join(BASE_DIR, 'uploads').replace('\\', '/')
    MEDIA_URL = '/uploads/'

    IMPORT_ROOT = os.path.join(BASE_DIR, 'imports').replace('\\', '/')
    IMPORT_URL = '/imports/'

    # STATIC_ROOT = os.path.join(BASE_DIR, 'static').replace('\\', '/')
    # STATIC_URL = '/static/'

    TEMPLATES = [
        {
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [
                str(BASE_DIR.joinpath('templates')),
                str(BASE_DIR.joinpath('emails','templates')),
            ],
            'APP_DIRS': True,
            'OPTIONS': {
                'context_processors': [
                    'django.template.context_processors.debug',
                    'django.template.context_processors.request',
                    'django.contrib.auth.context_processors.auth',
                    'django.contrib.messages.context_processors.messages',
                ],
            },
        },
    ]
    
    PASSWORD_HASHERS = [
        'backend.components.hashers.SHA256PasswordHasher.SHA256PasswordHasher',
        'django.contrib.auth.hashers.BCryptSHA256PasswordHasher',
        'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    ]

    # WSGI_APPLICATION = 'wsgi.application'
    ASGI_APPLICATION = 'asgi.application'

    DEFAULT_FILE_STORAGE = 'django.core.files.storage.FileSystemStorage'

    # STORAGES = {
    #     "default": {
    #         "BACKEND": "django.core.files.storage.FileSystemStorage",
    #     },
    #     "staticfiles": {
    #         "BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage",
    #     },
    # }

    MESSAGE_STORAGE = 'django.contrib.messages.storage.cookie.CookieStorage'

    AUTH_PASSWORD_VALIDATORS = [
        {
            'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
        },
        {
            'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
        },
    ]
    REST_FRAMEWORK = {
        #'DEFAULT_AUTHENTICATION_CLASSES': (
        #    'rest_framework.authentication.SessionAuthentication',
        #),
        'DEFAULT_AUTHENTICATION_CLASSES': [],
        'DEFAULT_PERMISSION_CLASSES': [
            'rest_framework.permissions.AllowAny',
            #'rest_framework.permissions.IsAuthenticated',    
            #'rest_framework.permissions.DjangoModelPermissions',
            #'rest_framework.permissions.DjangoModelPermissionsOrAnonReadOnly',
        ],
        'DEFAULT_FILTER_BACKENDS': [
            'rest_witchcraft.filters.SearchFilter',
            'django_filters.rest_framework.DjangoFilterBackend'
        ]
    }

    STATICFILES_DIRS = [
        os.path.join(BASE_DIR, 'static'),
    ]

    SESSION_ENGINE = 'django.contrib.sessions.backends.signed_cookies'



class Web(Base):
    CONFIG_NAME = 'Web'
    DEBUG = False
    DATABASE_CONNECTION_STRING = property(lambda self: os.getenv('DATABASE_CONNECTION_STRING', 'postgresql+psycopg2://postgres:postgres@localhost/mishutka_web'))

class Test(Base):
    CONFIG_NAME = 'Test'
    DEBUG = True
    # DATABASE_CONNECTION_STRING = property(lambda self: os.getenv('DATABASE_CONNECTION_STRING', 'postgresql+psycopg2://postgres:postgres@localhost/starkonet_web_develop'))
    DATABASE_CONNECTION_STRING = property(lambda self: 'postgresql+psycopg2://postgres:postgres@localhost/mishutka_web')
