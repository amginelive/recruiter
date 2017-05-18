"""
Django development server settings for squareballoon project.
"""

from .common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = (
    '*',
)

WSGI_APPLICATION = 'conf.wsgi.devt.application'

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

# google reCAPTCHA 2 settings
RECAPTCHA_PUBLIC_KEY = ''
RECAPTCHA_PRIVATE_KEY = ''
# NOCAPTCHA = False   nouse
# RECAPTCHA_USE_SSL = True  nouse
# CAPTCHA_AJAX = False  nouse
#RECAPTCHA_PROXY = 'http://192.168.0.102:9000'

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


# Debug Toolbar

INSTALLED_APPS += ('debug_toolbar',)
MIDDLEWARE_CLASSES += ('debug_toolbar.middleware.DebugToolbarMiddleware',)
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
    # 'debug_toolbar.panels.redirects.RedirectsPanel',
]


try:
    from .local import *
except ImportError:
    pass
