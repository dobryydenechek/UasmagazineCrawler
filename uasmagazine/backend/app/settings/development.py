from .defaults import *

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql_psycopg2',
        'NAME': 'crawlers',
        'USER': 'crawlers',
        'PASSWORD': 'qwerty123',
        'HOST': '127.0.0.1',
        'PORT': '5432',
    }
}

SCRAPYD_URL = 'http://localhost:6800'
CELERY_BROKER_URL = 'redis://localhost:6379/0'
FILES_STORE = '/tmp/storage'

STATIC_URL = '/static/'
STATIC_ROOT = ''
STATICFILES_DIRS = (os.path.join(BASE_DIR, 'static'), )
