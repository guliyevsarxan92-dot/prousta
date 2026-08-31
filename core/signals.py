from django.db.models.signals import pre_save, post_save
from django.db.models import F
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Odenis, Profil, Mesaj

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
            'is_active': False,
        },
    )
    return user


@receiver(pre_save, sender=Odenis)
def odenis_tesdiq_signal(sender, instance, **kwargs):
    instance._tesdiq_transition = False
    if instance.pk:
        try:
            kohne = Odenis.objects.select_for_update().get(pk=instance.pk)
            if kohne.status != 'tesdiq_edildi' and instance.status == 'tesdiq_edildi':
                instance._tesdiq_transition = True
                if instance.nov == 'balans':
                    Profil.objects.filter(
                        istifadeci=instance.istifadeci
                    ).update(balans=F('balans') + instance.mebleg)
        except Odenis.DoesNotExist:
            pass


@receiver(post_save, sender=Odenis)
def odenis_tesdiq_mesaj(sender, instance, created, **kwargs):
    """Ödəniş təsdiq edildikdə istifadəçiyə avtomatik bildiriş mesajı göndərir."""
    if created or not getattr(instance, '_tesdiq_transition', False):
        return

    def _gonder():
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

    transaction.on_commit(_gonder)
