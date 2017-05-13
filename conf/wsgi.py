"""
WSGI config for recruiter project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.11/howto/deployment/wsgi/
"""

import os
import sys
import site

# previously hardcoded to: /var/www/vhosts/recruiter/envi
venv_path = os.environ.setdefault('ENVPATH', '/var/www/vhosts/recruiter/envi')
vact_path = os.path.expanduser(os.path.join(venv_path, 'bin', 'activate_this.py'))

# Activate the virtualenv
# 
# previous implementation:
#     site.addsitedir('/var/www/vhosts/recruiter/envi/lib/python3.5/site-packages')
with open(vact_path) as file:
    exec(file.read(), {'__file__': vact_path})

# Additional paths to PYTHONPATH
for path in (
    '/var/www/vhosts/recruiter'
    '/var/www/vhosts/recruiter/recruiter'
):
    sys.path.append(path)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')

from django.core import wsgi
application = wsgi.get_wsgi_application()
