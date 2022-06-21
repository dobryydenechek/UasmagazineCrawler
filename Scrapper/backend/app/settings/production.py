from .defaults import *

DEBUG = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': os.environ['POSTGRES_DB_NAME'],
        'USER': os.environ['POSTGRES_USERNAME'],
        'PASSWORD': os.environ['POSTGRES_PASSWORD'],
        'HOST': os.environ['POSTGRES_HOSTNAME'],
        'PORT': os.environ['POSTGRES_PORT']
    }
}

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
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

SCRAPYD_HOST = os.environ['SCRAPYD_HOST']
SCRAPYD_URL = 'http://%s:6800' % SCRAPYD_HOST
REDIS_HOST = os.environ['REDIS_HOST']
CELERY_BROKER_URL = 'redis://%s:6379/0' % REDIS_HOST
FILES_STORE = os.environ['FILES_STORE']

STATIC_URL = '/static/'
STATIC_ROOT = ''
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'),)

ALLOWED_HOSTS = ['*']
