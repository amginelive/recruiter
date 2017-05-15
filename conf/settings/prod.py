"""
Django development server settings for squareballoon project.
"""

import os

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
LOG_DIR = os.path.join(BASE_DIR, 'logs')


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')no_g$60popv3=ki4$omo2kx0++kx)a2*lot@41+2xyup*-&p%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['www.squareballoon.com', 'squareballoon.com']
ADMINS = (
    ('Illya Konovalov', 'horbor@horbor.de'),
)
MANAGERS = ADMINS + ('Matt Codina', 'mattcodina.work@gmail.com')

LANGUAGE_CODE = 'en'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',   # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'squareballoon',                      # Or path to database file if using sqlite3.
        'USER': 'recruiter',
        'PASSWORD': 'TeKra0ka567!',
        'HOST': 'localhost',                    # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
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
MEDIA_ROOT = '/var/www/vhosts/recruiter/http/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/var/www/vhosts/recruiter/http/static/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
# Additional locations of static files

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/vhosts/recruiter/static/',
)

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
SERVER_EMAIL = "noreply@squareballoon.com"
EMAIL_PORT = 587

DEFAULT_FROM_EMAIL = SERVER_EMAIL
# can be used in email body and titles
#EMAIL_HOST = 'localhost'
EMAIL_PROJECT_NAME = 'squareballoon'

# Email addresses, default phone, etc.
NOREPLY_EMAIL = 'noreply@squareballoon.com'
DEFAULT_SUPPORT_EMAIL = 'support@squareballoon.com'


# for squareballoon (not Django original parameter)
TEMP_UPLOAD_DIR = MEDIA_ROOT+'upload/'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,

    'formatters': {
        'verbose': {
            'format': '[%(levelname)s %(asctime)s %(module)s %(process)d %(thread)d] %(message)s'
        },
        'normal': {
            'format': '[%(levelname)s %(asctime)s %(module)s] %(message)s'
        },
        'simple': {
            'format': '[%(levelname)s %(asctime)s] %(message)s'
        },
    },

    'handlers': {
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        },
        'debug_log_file': {
            'formatter': 'normal',
            'level': 'DEBUG',
            'filename': os.path.join(LOG_DIR, 'debug.log'),
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'when': 'W0',
            'encoding': 'utf-8'
        },
        'null': {
            'level': 'DEBUG',
            'class': 'logging.NullHandler',
        },
        'action_log': {
            'formatter': 'normal',
            'level': 'INFO',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOG_DIR, 'console.log'),
            'when': 'W0',
            'encoding': 'utf-8'
        }
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins', 'debug_log_file'],
            'level': 'INFO',
            'propagate': True
        },
        'debug_log': {
            'handlers': ['debug_log_file'],
            'level': 'DEBUG',
            'propagate': False
        },
        'console_log': {
            'handlers': ['action_log'],
            'level': 'INFO',
            'propagate': False
        },
    }
}
