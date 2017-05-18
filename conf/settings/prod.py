from .common import *


DEBUG = False

ALLOWED_HOSTS = ['www.squareballoon.com', 'squareballoon.com']

ADMINS = (
    ('Lorence Lim', 'jlorencelim@gmail.com'),
)
MANAGERS = ADMINS + ('Matt Codina', 'mattcodina.work@gmail.com')

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
