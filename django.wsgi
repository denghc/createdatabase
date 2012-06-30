import os
import sys
import django.core.handlers.wsgi
sys.path.append('/home/devsleague/websites')
sys.path.append('/home/devsleague/websites/RegisterSystem')
os.environ['DJANGO_SETTINGS_MODULE'] = 'RegisterSystem.settings'
application = django.core.handlers.wsgi.WSGIHandler() 