"""
WSGI config for market project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/3.2/howto/deployment/wsgi/
"""
import os
from threading import Thread

from django.core.wsgi import get_wsgi_application

from browsing_history.clear_history import history_deletion

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'market.settings')

application = get_wsgi_application()

Thread(target=history_deletion).start()
