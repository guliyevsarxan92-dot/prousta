from django.db.models.signals import post_save, pre_save, post_delete
from django.db.models import F
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Odenis, Profil, Mesaj, VipPaket

@receiver(post_save, sender=User)
def profil_yarat(sender, instance, created, **kwargs):
    if created:
        Profil.objects.get_or_create(istifadeci=instance)


def _sistem_istifadecisi():
    """Sistem bildirişləri üçün göndərici istifadəçi (yaradılır əgər yoxdursa)."""
    user, _ = User.objects.get_or_create(
        username='prousta_sistem',
        defaults={
            'email': 'sistem@prousta.az',
            'first_name': 'Prousta',
            'last_name': 'Sistem',
            'is_active': False,
        },
    )
    return user


@receiver(post_save, sender=Odenis)
def odenis_tesdiq_mesaj(sender, instance, created, **kwargs):
    """Ödəniş təsdiq edildikdə istifadəçiyə avtomatik bildiriş mesajı göndərir."""
    if created or not getattr(instance, '_tesdiq_transition', False):
        return

    def _gonder():
        try:
            sistem = _sistem_istifadecisi()
            if instance.nov == 'balans':
                metn = (
                    f"Hörmətli istifadəçi,\n\n"
                    f"Balans artırma sorğunuz təsdiq edildi. Balansınıza "
                    f"{instance.mebleg} ₼ əlavə olundu.\n\n"
                    f"İndi elanlarınızı VIP edə və ya digər ödənişli xidmətlərdən "
                    f"istifadə edə bilərsiniz.\n\n"
                    f"Prousta.az komandası"
                )
            elif instance.nov in ('vip', 'super_vip'):
                nov_ad = 'Super VIP' if instance.nov == 'super_vip' else 'VIP'
                metn = (
                    f"Hörmətli istifadəçi,\n\n"
                    f"{nov_ad} elan ödənişiniz ({instance.mebleg} ₼) təsdiq edildi. "
                    f"Elanınız artıq {nov_ad} statusda siyahının yuxarısında göstərilir.\n\n"
                    f"Təşəkkür edirik!\n\n"
                    f"Prousta.az komandası"
                )
            else:
                metn = (
                    f"Hörmətli istifadəçi,\n\n"
                    f"Ödənişiniz ({instance.mebleg} ₼) təsdiq edildi.\n\n"
                    f"Prousta.az komandası"
                )

            Mesaj.objects.create(
                gonderici=sistem,
                alici=instance.istifadeci,
                elan=instance.elan,
                metn=metn,
                oxundu=False,
            )
        except Exception:
            pass

    try:
        if transaction.get_connection().in_atomic_block:
            transaction.on_commit(_gonder)
        else:
            _gonder()
    except Exception:
        _gonder()


@receiver(pre_save, sender=User)
def revoke_tokens_on_password_change(sender, instance, **kwargs):
    if instance.pk:
        old = User.objects.filter(pk=instance.pk).values_list('password', flat=True).first()
        if old is not None and old != instance.password:
            from rest_framework.authtoken.models import Token
            Token.objects.filter(user_id=instance.pk).delete()


def _delete_after_commit(model, field, name, storage):
    from .media_cleanup import enqueue
    enqueue(name, 'receipts' if field == 'qebz' else 'default')


from .models import Elan, ElanShekil, ReklamBanner, Kategori, Problem


@receiver(post_delete)
def cleanup_deleted_media(sender, instance, **kwargs):
    fields = {ElanShekil: 'shekil', Profil: 'avatar', Odenis: 'qebz'}
    field = fields.get(sender)
    if field:
        file = getattr(instance, field)
        if file and file.name:
            _delete_after_commit(sender, field, file.name, file.storage)


@receiver(pre_save)
def cleanup_replaced_media(sender, instance, **kwargs):
    fields = {ElanShekil: 'shekil', Profil: 'avatar', Odenis: 'qebz'}
    field = fields.get(sender)
    if field and instance.pk:
        old = sender.objects.filter(pk=instance.pk).first()
        if old:
            previous = getattr(old, field)
            current = getattr(instance, field)
            if previous and previous.name != getattr(current, 'name', None):
                instance._obsolete_media = (sender, field, previous.name, previous.storage)


@receiver(post_save)
@receiver(post_delete)
def invalidate_public_caches(sender, **kwargs):
    from django.core.cache import cache
    if sender == ReklamBanner:
        transaction.on_commit(lambda: cache.delete('reklam_bannerleri'))
    if sender == Kategori:
        transaction.on_commit(lambda: cache.delete_many(['nav_kateqoriyalar', 'seo_indexable_kat_ids', 'prousta_llms_txt_v3']))
    if sender in (Kategori, Problem, Elan):
        transaction.on_commit(lambda: cache.delete_many(['seo_indexable_kat_ids', 'prousta_llms_txt_v4']))


@receiver(post_save)
def cleanup_replaced_media_after_save(sender, instance, **kwargs):
    old = getattr(instance, '_obsolete_media', None)
    if old:
        del instance._obsolete_media
        _delete_after_commit(*old)
