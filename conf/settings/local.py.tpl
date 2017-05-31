DEBUG = True

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

AUTH_PASSWORD_VALIDATORS = []

ACCOUNT_EMAIL_VERIFICATION = 'none'

# Webpack dev server url
STATIC_URL = 'http://localhost:3000/static/'
