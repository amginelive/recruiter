"""
Django settings for recruiter project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
APP_DIR = os.path.join(BASE_DIR, 'apps')
LOG_DIR = os.path.join(BASE_DIR, 'logs')

# App/Library Paths
sys.path.append(APP_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')no_g$60popv3=ki4$omo2kx0++kx)a2*lot@41+2xyup*-&p%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ['192.168.1.104', '192.168.1.100', '192.168.1.102', '192.168.1.105', '192.168.0.108', '192.168.0.100']
ADMINS = (
    ('Illya Konovalov', 'horbor@gmail.com'),
)


MANAGERS = ADMINS
LANGUAGE_CODE = 'en'

SEO_MODELS = True
# Application definition

INSTALLED_APPS = (
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.sites',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'authme',
    'easy_thumbnails',
    'phonenumber_field',
#    'djangoseo',
    'recruit',
    'profileme',
    'bootstrapform',  # for allauth templates
    # allauth
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'allauth.socialaccount.providers.facebook',
#    'allauth.socialaccount.providers.google',
    # end allauth
#    'snowpenguin.django.recaptcha2',
    'debug_toolbar',
)

MIDDLEWARE_CLASSES = (
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.locale.LocaleMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django.middleware.security.SecurityMiddleware',
)

ROOT_URLCONF = 'recruiter.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),
            os.path.join(BASE_DIR, 'apps/allauth/templates')
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                "django.contrib.auth.context_processors.auth",
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.static",
                #"django.template.context_processors.tz",
                "django.contrib.messages.context_processors.messages",
            ],
            #'loaders':[
            #    'django.template.loaders.filesystem.Loader',
            #    'django.template.loaders.app_directories.Loader'
            #],
            'debug': DEBUG,
        },
    },
]

ROOT_URLCONF = 'recruiter.urls'
WSGI_APPLICATION = 'recruiter.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',   # Add 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
        'NAME': 'recruiter',                      # Or path to database file if using sqlite3.
        # The following settings are not used with sqlite3:
        'USER': 'dev',
        'PASSWORD': 'dev',
        'HOST': 'localhost',                    # Empty for localhost through domain sockets or '127.0.0.1' for localhost through TCP.
        'PORT': '5432',
    }
}

# google reCAPTCHA 2 settings
RECAPTCHA_PUBLIC_KEY = 'pub_key'
RECAPTCHA_PRIVATE_KEY = 'priv_key'
# NOCAPTCHA = False   nouse
# RECAPTCHA_USE_SSL = True  nouse
# CAPTCHA_AJAX = False  nouse
#RECAPTCHA_PROXY = 'http://192.168.0.102:9000'

if TESTING:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3', # Add 'postgresql_psycopg2', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': 'recruiter',                      # Or path to database file if using sqlite3.
        }
    }


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

# TRANSMETA language configuration
LANGUAGE_CODE = 'en'

#ugettext = lambda s: s # dummy ugettext function, as django's docs say
from django.utils.translation import ugettext_lazy as _

LANGUAGES = (
    ('en', _('English')),
)

# localization, name of language cookie used by locale middleware
LANGUAGE_COOKIE_NAME = 'lang'
# session language key
LANGUAGE_SESSION_KEY = 'lang'

TIME_ZONE = 'Europe/Kiev'

USE_I18N = True

USE_L10N = True

USE_TZ = True

SITE_ID = 1

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/var/www/example.com/media/"
MEDIA_ROOT = '/var/www/vhosts/upwork/recruiter/http/media/'

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://example.com/media/", "http://media.example.com/"
MEDIA_URL = '/media/'

# Absolute path to the directory static files should be collected to.
# Don't put anything in this directory yourself; store your static files
# in apps' "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/var/www/example.com/static/"
STATIC_ROOT = '/var/www/vhosts/upwork/recruiter/assets/'

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.8/howto/static-files/

STATIC_URL = '/static/'
# Additional locations of static files

STATICFILES_DIRS = (
    # Put strings here, like "/home/html/static" or "C:/www/django/static".
    # Always use forward slashes, even on Windows.
    # Don't forget to use absolute paths, not relative paths.
    '/var/www/vhosts/upwork/recruiter/static/',
)

# AUTHENTICATION_BACKENDS list has been added later
AUTHENTICATION_BACKENDS = (
        'authme.auth.CustomAuth',
        # Needed to login by username in Django admin, regardless of `allauth`
        "django.contrib.auth.backends.ModelBackend",
        # `allauth` specific authentication methods, such as login by e-mail
        "allauth.account.auth_backends.AuthenticationBackend",
)


# user model (optional)
AUTH_USER_MODEL = 'authme.User'

# sessions (optional)
SESSION_ENGINE = "django.contrib.sessions.backends.cached_db" # it's not a default

# cache (optional)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        'TIMEOUT': 60,
        'KEY_PREFIX': 'recruiter',
    }
}

#CACHES = {
#    'default': {
#        'BACKEND': 'django.core.cache.backends.memcached.MemcachedCache',
#        'LOCATION': '127.0.0.1:11211',
#    }
#}


# Start allauth settings
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_AUTHENTICATION_METHOD = "email"
ACCOUNT_EMAIL_REQUIRED = True
LOGIN_REDIRECT_URL = '/dashboard/'
#ACCOUNT_ADAPTER = 'authme.account_adapter.NoNewUsersAccountAdapter'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_SIGNUP_FORM_CLASS = 'authme.forms.CustomSignupForm'
ACCOUNT_LOGOUT_ON_GET = True  # don't ask on sign out
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_EMAIL_REQUIRED = False
#SOCIALACCOUNT_ADAPTER = 'authme.account_adapter.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'authme.account_adapter.CustomAccountAdapter'
ACCOUNT_USERNAME_BLACKLIST = ['admin', 'squareballoon', 'root']
ACCOUNT_USERNAME_VALIDATORS = None
#ACCOUNT_USER_MODEL_EMAIL_FIELD= 'email'

# social providers

# SOCIALACCOUNT_PROVIDERS = \
#     {'facebook':
#         {'METHOD': 'oauth2',
#          'SCOPE': ['email', 'public_profile', 'user_friends'],
#          'AUTH_PARAMS': {'auth_type': 'https'},
#          'FIELDS': [
#              'id',
#              'email',
#              'name',
#              'first_name',
#              'last_name',
#              'verified',
#              'locale',
#              'timezone',
#              'link',
#              'gender',
#              'updated_time'],
#          'EXCHANGE_TOKEN': True,
#          'VERIFIED_EMAIL': True,
#          'VERSION': 'v2.4'}}

# end allauth settings

# Email addresses, default phone, etc.
NOREPLY_EMAIL = 'noreply@squareballoon.com'
DEFAULT_SUPPORT_EMAIL = 'support@squareballoon.com'

EMAIL_BACKEND = 'django.core.mail.backends.filebased.EmailBackend'
EMAIL_FILE_PATH = '/var/www/vhosts/upwork/recruiter/tmp_mail'  # for testing

# used to generate different image sizes, but the format is for
# and can be used by easy-thumbnails app
THUMBNAIL_ALIASES = {
    # based on models
    'profileme_candidate': {
        'photo': {'size': (200, 200), 'crop': 'smart'},
    },
    'profileme_agent': {
        'photo': {'size': (200, 200), 'crop': 'smart'},
    },
    'recruit_company': {
        'logo': {'size': (600, 200), 'crop': 'smart'},
    },
}

# for recruiter (not Django original parameter)
TEMP_UPLOAD_DIR = MEDIA_ROOT + 'upload/'
# imagine: use temporary images or upload directly
IMAGINE_USE_TEMP = False

# phone_number_field settings
PHONENUMBER_DB_FORMAT = 'E164'


# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
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
    },
    'loggers': {
        'django.security.DisallowedHost': {
            'handlers': ['null'],
            'propagate': False,
        },
        'django.request': {
            'handlers': ['mail_admins'],
            'level': 'INFO',
            'propagate': False
        },
        'debug_log': {
            'handlers': ['debug_log_file'],
            'level': 'DEBUG',
            'propagate': False
        },
    }
}


if DEBUG:
    MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
    #INSTALLED_APPS += ('debug_toolbar',)
    INTERNAL_IPS = ('127.0.0.1', '192.168.0.101','192.168.1.103','192.168.1.102','192.168.1.106','192.168.1.100','192.168.1.105','192.168.1.108','192.168.56.102')
    DEBUG_TOOLBAR_CONFIG = {
        'EXCLUDE_URLS': ('/baladmin',),
        'INTERCEPT_REDIRECTS': True,
    }
    DEBUG_TOOLBAR_PANELS = [
        'debug_toolbar.panels.versions.VersionsPanel',
        'debug_toolbar.panels.timer.TimerPanel',
        'debug_toolbar.panels.settings.SettingsPanel',
        'debug_toolbar.panels.headers.HeadersPanel',
        'debug_toolbar.panels.request.RequestPanel',
        'debug_toolbar.panels.sql.SQLPanel',
        'debug_toolbar.panels.staticfiles.StaticFilesPanel',
        'debug_toolbar.panels.templates.TemplatesPanel',
        'debug_toolbar.panels.cache.CachePanel',
        'debug_toolbar.panels.signals.SignalsPanel',
        'debug_toolbar.panels.logging.LoggingPanel',
        'debug_toolbar.panels.redirects.RedirectsPanel',
    ]


# Settings override
try:
    from .local_settings import *
except ImportError as e:
    pass

try:
    from .local_settings import modify
    modify(globals())
except ImportError:
    pass
