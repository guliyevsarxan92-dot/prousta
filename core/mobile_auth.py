import json
import secrets
import hashlib
from datetime import timedelta
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from .identity import google_user
from .throttles import mobile_auth_limit
from .models import MobileLoginTicket

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.models import User
from django.core.cache import cache
from django.http import HttpResponseBadRequest, JsonResponse
from django.shortcuts import redirect
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET, require_POST

from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token

from .models import Profil

TOKEN_TTL_SECONDS = 60
CACHE_PREFIX = "mobile_login_token:"


@csrf_exempt
@require_POST
@mobile_auth_limit
def mobile_google_login(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return HttpResponseBadRequest("invalid json")

    if not isinstance(data, dict) or not isinstance(data.get("id_token"), str):
        return JsonResponse({"error": "id_token required"}, status=400)
    token = data["id_token"].strip()
    if not token or len(token) > 16384:
        return JsonResponse({"error": "id_token required"}, status=400)

    client_id = getattr(settings, "GOOGLE_WEB_CLIENT_ID", "") or settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    if not client_id:
        return JsonResponse({"error": "server not configured"}, status=500)

    try:
        info = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id
        )
    except (ValueError, TypeError):
        return JsonResponse({"error": "invalid token"}, status=401)

    try:
        user = google_user(info)
    except ValidationError as exc:
        return JsonResponse({'error': ' '.join(exc.messages)}, status=400)

    login_token = secrets.token_urlsafe(32)
    MobileLoginTicket.objects.create(digest=hashlib.sha256(login_token.encode()).hexdigest(),
                                      user=user, expires=timezone.now() + timedelta(seconds=TOKEN_TTL_SECONDS))
    return JsonResponse({"login_token": login_token})


@require_GET
def mobile_session(request):
    token = (request.GET.get("t") or "").strip()
    if not token:
        return redirect("giris")
    with transaction.atomic():
        ticket = MobileLoginTicket.objects.select_for_update().select_related('user').filter(
            digest=hashlib.sha256(token.encode()).hexdigest(), expires__gt=timezone.now()).first()
        if not ticket:
            return redirect('giris')
        user = ticket.user
        ticket.delete()
    if not user.is_active:
        return redirect('giris')
    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
    response = redirect('/')
    response['Cache-Control'] = 'no-store'
    response['Referrer-Policy'] = 'no-referrer'
    return response
