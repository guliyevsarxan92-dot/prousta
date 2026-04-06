from django.db.models.signals import pre_save, post_save
from django.db.models import F
from django.db import transaction
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Odenis, Profil

@receiver(post_save, sender=User)
def profil_yarat(sender, instance, created, **kwargs):
    if created:
        Profil.objects.get_or_create(istifadeci=instance)

@receiver(pre_save, sender=Odenis)
def odenis_tesdiq_signal(sender, instance, **kwargs):
    if instance.pk:
        try:
            kohne = Odenis.objects.select_for_update().get(pk=instance.pk)
            if kohne.status != 'tesdiq_edildi' and instance.status == 'tesdiq_edildi':
                if instance.nov == 'balans':
                    from .models import Profil
                    Profil.objects.filter(
                        istifadeci=instance.istifadeci
                    ).update(balans=F('balans') + instance.mebleg)
        except Odenis.DoesNotExist:
            pass
