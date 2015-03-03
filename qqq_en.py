import os
import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE'] = 'settings'
os.environ['QQQ_LANGUAGE'] = 'en'

application = django.core.handlers.wsgi.WSGIHandler()
