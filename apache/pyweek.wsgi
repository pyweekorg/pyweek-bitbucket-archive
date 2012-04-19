import os, sys
sys.path.append('/home/richard/pyweek/')

os.environ['DJANGO_SETTINGS_MODULE'] = 'pyweek.settings'

import django.core.handlers.wsgi

application = django.core.handlers.wsgi.WSGIHandler()
