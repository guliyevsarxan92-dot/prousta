from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.authtoken.models import Token


class ExpiringTokenAuthentication(TokenAuthentication):
    def authenticate_credentials(self, key):
        user, token = super().authenticate_credentials(key)
        if token.created + timedelta(seconds=settings.API_TOKEN_MAX_AGE) <= timezone.now():
            raise AuthenticationFailed('Sessiyanın müddəti bitib. Yenidən daxil olun.')
        return user, token


def issue_token(user):
    token, _ = Token.objects.get_or_create(user=user)
    if token.created + timedelta(seconds=settings.API_TOKEN_MAX_AGE) <= timezone.now():
        token.delete()
        token = Token.objects.create(user=user)
    return token
