"""Google identities are keyed by provider subject, never by an unverified email."""
import secrets

from django.contrib.auth.models import User
from django.db import transaction
from django.core.exceptions import ValidationError
from social_core.exceptions import AuthException
from social_django.models import UserSocialAuth


def require_explicit_google_link(backend, details, user=None, *args, **kwargs):
    if user is None and User.objects.filter(email__iexact=details.get('email', '')).exists():
        raise AuthException(backend, 'Əvvəl mövcud hesabınıza daxil olun, sonra Google hesabını əlaqələndirin.')


@transaction.atomic
def google_user(info):
    if not isinstance(info, dict):
        raise ValidationError('Google hesabı təsdiqlənməyib.')
    email = (info.get('email') or '').strip().lower()
    subject = info.get('sub')
    if not email or info.get('email_verified') is not True or not isinstance(subject, str) or not subject:
        raise ValidationError('Google hesabı təsdiqlənməyib.')
    identity = UserSocialAuth.objects.select_related('user').filter(provider='google-oauth2', uid=subject).first()
    if identity:
        if not identity.user.is_active:
            raise ValidationError('Hesab deaktiv edilib.')
        return identity.user
    existing = list(User.objects.select_for_update().filter(email__iexact=email)[:2])
    if (len(existing) == 1 and existing[0].is_active and not existing[0].has_usable_password()
            and not existing[0].is_staff and not existing[0].is_superuser
            and not existing[0].social_auth.exists()):
        # Older mobile Google accounts had no provider row. They cannot be
        # password-created by registration. Invalidate old sessions/tokens when claimed.
        user = existing[0]
        user.set_unusable_password()
        user.save(update_fields=['password'])
        UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid=subject)
        return user
    if existing:
        raise ValidationError('Bu email ilə hesab mövcuddur. Əvvəl həmin hesaba daxil olaraq Google hesabını əlaqələndirin.')
    # A random username avoids races and reserves system identities.
    user = User.objects.create_user(username='google_' + secrets.token_hex(12), email=email,
                                    first_name=(info.get('given_name') or '')[:50],
                                    last_name=(info.get('family_name') or '')[:50])
    UserSocialAuth.objects.create(user=user, provider='google-oauth2', uid=subject)
    user.profil.ad = user.first_name
    user.profil.soyad = user.last_name
    user.profil.save(update_fields=['ad', 'soyad'])
    return user
