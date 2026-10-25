from rest_framework.throttling import SimpleRateThrottle
from functools import wraps
from django.core.cache import cache
from django.http import JsonResponse


def mobile_auth_limit(view):
    """Bound Google verification requests before contacting the provider."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        key = 'mobile-google-auth:' + request.META.get('REMOTE_ADDR', 'unknown')
        if cache.add(key, 1, timeout=60):
            count = 1
        else:
            try:
                count = cache.incr(key)
            except ValueError:
                # The counter may expire between add and incr.
                cache.add(key, 1, timeout=60)
                count = 1
        if count > 5:
            response = JsonResponse({'error': 'Çoxsaylı cəhd. Bir dəqiqə sonra yoxlayın.'}, status=429)
            response['Retry-After'] = '60'
            return response
        return view(request, *args, **kwargs)
    return wrapped


class AuthThrottle(SimpleRateThrottle):
    scope = 'auth'

    def get_cache_key(self, request, view):
        return self.cache_format % {'scope': self.scope, 'ident': self.get_ident(request)}


class WriteThrottle(AuthThrottle):
    scope = 'write'

    def get_cache_key(self, request, view):
        if request.method in ('GET', 'HEAD', 'OPTIONS'):
            return None
        ident = request.user.pk if request.user.is_authenticated else self.get_ident(request)
        return self.cache_format % {'scope': self.scope, 'ident': ident}
