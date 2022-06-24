import os
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent


env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_htmx',
]

PROJECT_APPS = [
    'user_app',
    'categories',
    'configuration_service',
    'roles',
    'utils',
    'banners',
    'products',
    'products_compare',
    'sellers',
    'review',
    'payment',
    'browsing_history.apps.BrowsingHistory',
    'reviews',
    'discounts',
    'cart',
]

PRODCOMP_SESSION_ID = 'product_compare'
CART_SESSION_ID = 'cart'

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'utils.middlewares.CartTotalPriceMiddleware',
]


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

ROOT_URLCONF = 'market.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'products_compare.context_processors.product_compare_list',
            ],
        },
    },
]

WSGI_APPLICATION = 'market.wsgi.application'


ALLOWED_HOSTS = []
DEBUG = env.bool('DEBUG', default=False)
SECRET_KEY = env.str('SECRET_KEY')

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_L10N = True
USE_TZ = True

DATABASES = {'default': env.db('DATABASE_URL')}
public_root = BASE_DIR / 'public'
MEDIA_ROOT = public_root / 'media'
MEDIA_URL = env.str('MEDIA_URL', default='/media/')

STATIC_ROOT = public_root / 'static'
STATICFILES_DIRS = [
    BASE_DIR / "static"
]
STATIC_URL = env.str('STATIC_URL', default='/static/')

LOGIN_URL = '/account/login/'
LOGIN_REDIRECT_URL = '/account/profile/'
LOGOUT_REDIRECT_URL = '/'

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'roles': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}

CACHES = {'default': env.cache('CACHE')}
