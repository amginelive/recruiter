"""
WSGI config for recruiter project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
import site

# Add the site-packages of the chosen virtualenv to work with
site.addsitedir('/var/www/vhosts/recruiter/envi/lib/python3.5/site-packages')

# Add the app's directory to the PYTHONPATH
sys.path.append('/var/www/vhosts/recruiter')
sys.path.append('/var/www/vhosts/recruiter/recruiter')

os.environ['DJANGO_SETTINGS_MODULE'] = 'recruiter.settings.common'

# Activate your virtual env
# activate_env = os.path.expanduser("/var/www/vhosts/recruiter/envi/bin/activate_this.py")
# exec(open(activate_env).read())

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
