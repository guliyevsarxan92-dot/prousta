from django.db.models.signals import post_save, pre_save, post_delete
from django.db.models import F
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import Odenis, Profil, Mesaj, VipPaket, Elan

@receiver(post_save, sender=User)
def profil_yarat(sender, instance, created, **kwargs):
    if created:
        Profil.objects.get_or_create(istifadeci=instance)


def _sistem_istifadecisi():
    """Sistem bildirişləri üçün göndərici istifadəçi (yaradılır əgər yoxdursa)."""
    user, created = User.objects.get_or_create(
        username='prousta_sistem',
        defaults={
            'email': 'sistem@prousta.az',
            'first_name': 'Prousta',
            'last_name': 'Sistem',
            'is_active': True,
        },
    )
    update_fields = []
    if not user.is_active:
        user.is_active = True
        update_fields.append('is_active')
    if user.first_name != 'Prousta':
        user.first_name = 'Prousta'
        update_fields.append('first_name')
    if user.last_name != 'Sistem':
        user.last_name = 'Sistem'
        update_fields.append('last_name')
    if user.has_usable_password():
        user.set_unusable_password()
        update_fields.append('password')
    if update_fields:
        user.save(update_fields=update_fields)

    profil, _ = Profil.objects.get_or_create(istifadeci=user)
    p_updates = []
    if profil.ad != 'Prousta':
        profil.ad = 'Prousta'
        p_updates.append('ad')
    if profil.soyad != 'Sistem':
        profil.soyad = 'Sistem'
        p_updates.append('soyad')
    if p_updates:
        profil.save(update_fields=p_updates)

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


@receiver(pre_save, sender=Elan)
def track_elan_status_pre_save(sender, instance, **kwargs):
    """Elanın aktiv statusa keçib-keçmədiyini izləyir."""
    if instance.pk:
        old_status = Elan.objects.filter(pk=instance.pk).values_list('status', flat=True).first()
        instance._status_transitioned_to_aktiv = (old_status != 'aktiv' and instance.status == 'aktiv')
    else:
        instance._status_transitioned_to_aktiv = (instance.status == 'aktiv')


@receiver(post_save, sender=Elan)
def ilk_elan_vip_mesaj(sender, instance, created, **kwargs):
    """İstifadəçinin ilk elanı aktiv olduqda avtomatik VIP məlumat mesajı göndərir."""
    if instance.status != 'aktiv':
        return
    if not getattr(instance, '_status_transitioned_to_aktiv', False):
        return

    user = instance.istifadeci
    if not user or user.username == 'prousta_sistem':
        return

    def _gonder():
        try:
            sistem = _sistem_istifadecisi()
            if Mesaj.objects.filter(
                alici=user,
                gonderici=sistem,
                metn__icontains='VIP elanlar ən üst sıralarda yer alır'
            ).exists():
                return

            if Elan.objects.filter(istifadeci=user, status='aktiv').count() != 1:
                return

            metn = (
                "Salam! İlk elanınız uğurla dərc olundu.\n\n"
                "Daha çox müştəri və sifariş qazanmaq üçün elanınızı VIP edin!\n"
                "VIP elanlar ən üst sıralarda yer alır, xüsusi nişanla fərqlənir "
                "və adi elanlardan 10 qat daha çox zəng toplayır.\n\n"
                "Elanınızın üzərindəki «VIP et» düyməsini sıxaraq dərhal aktiv edə bilərsiniz.\n\n"
                "Uğurlu işlər!\n"
                "Prousta.az"
            )
            Mesaj.objects.create(
                gonderici=sistem,
                alici=user,
                elan=instance,
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
