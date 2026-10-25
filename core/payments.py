"""Explicit, transactional paid operations shared by web and mobile."""
from datetime import timedelta
from decimal import Decimal

from django.core.exceptions import ValidationError, PermissionDenied
from django.db import transaction
from django.db.models import F
from django.utils import timezone

from .models import Elan, Odenis, Profil, VipPaket
from .validation import money


def apply_receipt(payment):
    """Called only by Odenis.save while its row is locked. Never call directly."""
    amount = money(payment.mebleg, minimum=Decimal('0.01'), maximum=Decimal('500'))
    Profil.objects.get_or_create(istifadeci_id=payment.istifadeci_id)
    profile = Profil.objects.select_for_update().get(istifadeci_id=payment.istifadeci_id)
    if payment.nov == 'balans':
        Profil.objects.filter(pk=profile.pk).update(balans=F('balans') + amount)
        return
    if payment.nov not in ('vip', 'super_vip', 'ireli_cek') or not payment.elan_id:
        raise ValidationError('Ödəniş növü və ya elan düzgün deyil.')
    ad = Elan.objects.select_for_update().get(pk=payment.elan_id)
    if ad.istifadeci_id != payment.istifadeci_id or ad.status != 'aktiv':
        raise ValidationError('Ödəniş yalnız öz aktiv elanınız üçün tətbiq edilə bilər.')
    now = timezone.now()
    if payment.nov == 'ireli_cek':
        if amount != Decimal('1.00'):
            raise ValidationError('İrəli çəkmə məbləği 1 AZN olmalıdır.')
        Elan.objects.filter(pk=ad.pk).update(ireli_cekildi=now, ireli_cekilme_sayi=F('ireli_cekilme_sayi') + 1)
        return
    package = VipPaket.get_paket(payment.nov)
    if amount != package.qiymet:
        raise ValidationError('Ödəniş məbləği cari VIP tarifinə uyğun deyil.')
    _set_vip(ad, package, now)


def _set_vip(ad, package, now):
    end = max(ad.vip_bitis, now) if ad.is_vip_aktiv() else now
    ad.vip_status = package.nov
    ad.vip_bitis = end + timedelta(days=package.muddet_gun)
    ad.vip_yenilendi = now
    ad.save(update_fields=['vip_status', 'vip_bitis', 'vip_yenilendi', 'vip_siralama'])


@transaction.atomic
def buy_vip(user, ad_id, kind):
    if kind not in ('vip', 'super_vip'):
        raise ValidationError('Yanlış VIP növü.')
    Profil.objects.get_or_create(istifadeci=user)
    profile = Profil.objects.select_for_update().get(istifadeci=user)
    ad = Elan.objects.select_for_update().get(pk=ad_id, istifadeci=user)
    if ad.status != 'aktiv' or (ad.bitis_tarixi and ad.bitis_tarixi <= timezone.now()):
        raise ValidationError('Yalnız aktiv elan VIP edilə bilər.')
    if ad.is_vip_aktiv() and (ad.vip_status == kind or ad.vip_status == 'super_vip'):
        raise ValidationError('Elan artıq bu VIP statusundadır.')
    package = VipPaket.get_paket(kind)
    price = money(package.qiymet, minimum=Decimal('0.01'))
    if profile.balans < price:
        raise ValidationError('Balansınız kifayət deyil.')
    profile.balans -= price
    profile.save(update_fields=['balans'])
    now = timezone.now()
    _set_vip(ad, package, now)
    Odenis.objects.create(istifadeci=user, elan=ad, nov=kind, mebleg=price,
                         status='tesdiq_edildi', applied_at=now)
    return ad, profile, package


@transaction.atomic
def bump_listing(user, ad_id):
    Profil.objects.get_or_create(istifadeci=user)
    profile = Profil.objects.select_for_update().get(istifadeci=user)
    ad = Elan.objects.select_for_update().get(pk=ad_id)
    if ad.istifadeci_id != user.pk and not user.is_superuser:
        raise PermissionDenied
    if ad.status != 'aktiv' or (ad.bitis_tarixi and ad.bitis_tarixi <= timezone.now()):
        raise ValidationError('Yalnız aktiv elan irəli çəkilə bilər.')
    if profile.balans < Decimal('1.00'):
        raise ValidationError('Balansınız kifayət deyil.')
    profile.balans -= Decimal('1.00')
    profile.save(update_fields=['balans'])
    now = timezone.now()
    Elan.objects.filter(pk=ad.pk).update(ireli_cekildi=now, ireli_cekilme_sayi=F('ireli_cekilme_sayi') + 1)
    Odenis.objects.create(istifadeci=user, elan=ad, nov='ireli_cek', mebleg=Decimal('1.00'),
                         status='tesdiq_edildi', applied_at=now)
    return ad, profile
