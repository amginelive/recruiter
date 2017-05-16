"""
Django development server settings for squareballoon project.
"""

import os

from .common import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = (
    '*',
)

WSGI_APPLICATION = 'conf.wsgi.devt.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'squareballoon',                      # Or path to database file if using sqlite3.
        'USER': 'root',
        'PASSWORD': 'root',
        'HOST': '192.168.56.1',                    # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        #'PORT': '',                             # Set to empty string for default.
    }
}

# google reCAPTCHA 2 settings
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
# NOCAPTCHA = False   nouse
# RECAPTCHA_USE_SSL = True  nouse
# CAPTCHA_AJAX = False  nouse
#RECAPTCHA_PROXY = 'http://192.168.0.102:9000'

TIME_ZONE = 'Europe/London'

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
# Additional locations of static files

# store static files by appending MD5 hash of the file's content to the filename
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.ManifestStaticFilesStorage'

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}

# Emailing
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@mail.squareballoon.com'
EMAIL_HOST_PASSWORD = '7c4effb8443db2a9f70cf4e9ea3e243f'
EMAIL_PORT = 587


# can be used in email body and titles
EMAIL_PROJECT_NAME = 'squareballoon'

# Email addresses, default phone, etc.
SERVER_EMAIL = "noreply@squareballoon.com"
DEFAULT_FROM_EMAIL = SERVER_EMAIL


try:
    from .local import *
except ImportError:
    pass
