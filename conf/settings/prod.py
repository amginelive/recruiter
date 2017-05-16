"""
Django development server settings for squareballoon project.
"""

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
