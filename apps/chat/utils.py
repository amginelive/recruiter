from django.core.cache import cache
from django.conf import settings
from django.utils import timezone


def update_user_presence(user):
    now = timezone.now()
    cache.set(f'seen_{user.email}', now, settings.USER_ONLINE_TIMEOUT)
