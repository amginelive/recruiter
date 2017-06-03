"""
Django development server settings for squareballoon project.
"""

from .common import *


# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = (
    '*',
)

# Webpack development server
STATIC_URL = 'http://localhost:3000/static/'

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
# RECAPTCHA_PROXY = 'http://192.168.0.102:9000'


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
