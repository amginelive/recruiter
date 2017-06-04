from django.core.cache import cache
from django.conf import settings
from django.utils import timezone


class ActiveUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        current_user = request.user
        if request.user.is_authenticated():
            now = timezone.now()
            cache.set(f'seen_{current_user.email}', now,
                           settings.USER_LASTSEEN_TIMEOUT)

        response = self.get_response(request)
        return response
