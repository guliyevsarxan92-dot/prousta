import json
import secrets

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
def mobile_google_login(request):
    try:
        data = json.loads(request.body.decode("utf-8") or "{}")
    except ValueError:
        return HttpResponseBadRequest("invalid json")

    token = (data.get("id_token") or "").strip()
    if not token:
        return JsonResponse({"error": "id_token required"}, status=400)

    client_id = settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
    if not client_id:
        return JsonResponse({"error": "server not configured"}, status=500)

    try:
        info = google_id_token.verify_oauth2_token(
            token, google_requests.Request(), client_id
        )
    except ValueError as e:
        return JsonResponse({"error": "invalid token", "detail": str(e)}, status=401)

    email = (info.get("email") or "").lower().strip()
    if not email or not info.get("email_verified", False):
        return JsonResponse({"error": "email not verified"}, status=401)

    user = User.objects.filter(email__iexact=email).first()
    if user is None:
        base = (email.split("@")[0] or f"user{secrets.token_hex(3)}")[:26]
        username = base
        suffix = 0
        while User.objects.filter(username=username).exists():
            suffix += 1
            username = f"{base}{suffix}"
        user = User.objects.create_user(
            username=username,
            email=email,
            first_name=(info.get("given_name") or "")[:30],
            last_name=(info.get("family_name") or "")[:150],
        )
        user.set_unusable_password()
        user.save()
        profil, _ = Profil.objects.get_or_create(istifadeci=user)
        if not profil.ad:
            profil.ad = user.first_name or ""
        if not profil.soyad:
            profil.soyad = user.last_name or ""
        profil.save()

    login_token = secrets.token_urlsafe(32)
    cache.set(CACHE_PREFIX + login_token, user.pk, timeout=TOKEN_TTL_SECONDS)
    return JsonResponse({"login_token": login_token})


@require_GET
def mobile_session(request):
    token = (request.GET.get("t") or "").strip()
    if not token:
        return redirect("giris")
    key = CACHE_PREFIX + token
    user_id = cache.get(key)
    cache.delete(key)
    if not user_id:
        return redirect("giris")
    try:
        user = User.objects.get(pk=user_id)
    except User.DoesNotExist:
        return redirect("giris")
    user.backend = "django.contrib.auth.backends.ModelBackend"
    login(request, user)
    return redirect("/")
