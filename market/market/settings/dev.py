from .base import *  # pylint: disable=W0401, W0614

DEBUG = True

INTERNAL_IPS = [
    "127.0.0.1",
]


DJANGO_APPS = []
DEV_APPS = []
INSTALLED_APPS += \
    [
        'debug_toolbar'
    ] + PROJECT_APPS

MIDDLEWARE += [
    'debug_toolbar.middleware.DebugToolbarMiddleware',
]

AUTH_PASSWORD_VALIDATORS = []
