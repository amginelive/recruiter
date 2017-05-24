"""
Django settings for recruiter project.
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
import sys
from django.utils.translation import ugettext_lazy as _

TESTING = len(sys.argv) > 1 and sys.argv[1] == 'test'

PROJECT_DIR = os.path.dirname(os.path.dirname(__file__))
BASE_DIR = os.path.dirname(PROJECT_DIR)
APP_DIR = os.path.join(BASE_DIR, 'apps')
LOG_DIR = os.path.join(BASE_DIR, 'var', 'logs')

# App/Library Paths
sys.path.append(APP_DIR)

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ')no_g$60popv3=ki4$omo2kx0++kx)a2*lot@41+2xyup*-&p%'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = [
    '192.168.1.104',
    '192.168.1.100',
    '192.168.1.102',
    '192.168.1.105',
    '192.168.0.108',
    '192.168.0.100',
]

SITE_ID = 1

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
    'django.contrib.postgres',

    'allauth',
    'allauth.account',
    'allauth.socialaccount',
#    'allauth.socialaccount.providers.facebook',
#    'allauth.socialaccount.providers.google',
#    'snowpenguin.django.recaptcha2',
    'bootstrapform',
    'django_extensions',
    'django_js_reverse',
#    'djangoseo',
    'easy_thumbnails',
    'phonenumber_field',

    'companies',
    'recruit',
    'users',
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

ROOT_URLCONF = 'conf.urls'
WSGI_APPLICATION = 'conf.wsgi.prod.application'


# Database
# https://docs.djangoproject.com/en/1.11/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'recruiter',
        'USER': 'recruiter',
        'PASSWORD': 'recruiter!',
        'HOST': '',
        'PORT': '',
    }
}


# Internationalization
# https://docs.djangoproject.com/en/1.8/topics/i18n/

# TRANSMETA language configuration
LANGUAGE_CODE = 'en'

LANGUAGES = (
    ('en', _('English')),
)

LANGUAGE_COOKIE_NAME = 'lang'

LANGUAGE_SESSION_KEY = 'lang'

TIME_ZONE = 'Europe/London'

USE_I18N = True

USE_L10N = True

USE_TZ = True


####################################################################################################
# Frontend-related configuration
####################################################################################################

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'frontend', 'templates'),
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

# Static files (CSS, JavaScript, Images)

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'frontend', 'static.prod')
STATICFILES_DIRS = (
    os.path.join(BASE_DIR, 'frontend', 'static'),
)

# Media files

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'frontend', 'media')

THUMBNAIL_ALIASES = {
}

# imagine: use temporary images or upload directly
IMAGINE_USE_TEMP = False
TEMP_UPLOAD_DIR = MEDIA_ROOT + 'upload/'


####################################################################################################
# Authentication
####################################################################################################

AUTH_USER_MODEL = 'users.User'

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTHENTICATION_BACKENDS = (
        'users.auth.CustomAuth',
        # Needed to login by username in Django admin, regardless of `allauth`
        "django.contrib.auth.backends.ModelBackend",
        # `allauth` specific authentication methods, such as login by e-mail
        "allauth.account.auth_backends.AuthenticationBackend",
)

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
#ACCOUNT_ADAPTER = 'users.account_adapter.NoNewUsersAccountAdapter'
ACCOUNT_USER_MODEL_USERNAME_FIELD = None
ACCOUNT_USERNAME_REQUIRED = False
SIGNUP_PASSWORD_ENTER_TWICE = True
ACCOUNT_SIGNUP_PASSWORD_VERIFICATION = True
ACCOUNT_SIGNUP_FORM_CLASS = 'users.forms.CustomSignupForm'
ACCOUNT_LOGOUT_ON_GET = True  # don't ask on sign out
SOCIALACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_EMAIL_VERIFICATION = 'mandatory'
SOCIALACCOUNT_EMAIL_REQUIRED = False
#SOCIALACCOUNT_ADAPTER = 'users.account_adapter.CustomSocialAccountAdapter'
ACCOUNT_ADAPTER = 'users.account_adapter.CustomAccountAdapter'
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


####################################################################################################
# Email Configurations
####################################################################################################

EMAIL_PROJECT_NAME = 'squareballoon'
NOREPLY_EMAIL = 'noreply@squareballoon.com'
DEFAULT_SUPPORT_EMAIL = 'support@squareballoon.com'

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_USE_TLS = True
EMAIL_HOST = 'smtp.mailgun.org'
EMAIL_HOST_USER = 'postmaster@mail.squareballoon.com'
EMAIL_HOST_PASSWORD = '7c4effb8443db2a9f70cf4e9ea3e243f'
SERVER_EMAIL = "noreply@squareballoon.com"
EMAIL_PORT = 587
DEFAULT_FROM_EMAIL = SERVER_EMAIL


####################################################################################################
# Integrations Behaviour Configurations
####################################################################################################

# google reCAPTCHA 2 settings
RECAPTCHA_PUBLIC_KEY = 'pub_key'
RECAPTCHA_PRIVATE_KEY = 'priv_key'
# NOCAPTCHA = False   nouse
# RECAPTCHA_USE_SSL = True  nouse
# CAPTCHA_AJAX = False  nouse
#RECAPTCHA_PROXY = 'http://192.168.0.102:9000'

PHONENUMBER_DB_FORMAT = 'E164'
SEO_MODELS = True

# Django JS Reverse Configurations
JS_REVERSE_JS_MINIFY = False


####################################################################################################
# Logging Configurations
####################################################################################################

# ADMINS = (
#     ('Lorence', 'jlorencelim@gmail.com'),
# )

# MANAGERS = ADMINS

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
