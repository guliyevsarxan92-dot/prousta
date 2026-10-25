from django.core.cache import cache
from django.db import connection
from django.http import JsonResponse
from django.views.decorators.http import require_GET


@require_GET
def readiness(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
        cache.get('__readiness__')
    except Exception:
        return JsonResponse({'status': 'unavailable'}, status=503)
    response = JsonResponse({'status': 'ok'})
    response['Cache-Control'] = 'no-store'
    return response
