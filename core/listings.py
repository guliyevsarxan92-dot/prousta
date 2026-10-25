from datetime import timedelta
from decimal import Decimal
from contextlib import contextmanager

from django.core.exceptions import PermissionDenied, ValidationError
from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from .models import Bloklama, Elan, ElanShekil, Kategori, Profil, Odenis
from .validation import image_upload, listing_values
from .watermark import filigran_yoxla


def visible_listings(user):
    qs = Elan.objects.filter(status='aktiv').filter(
        Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=timezone.now()))
    return qs.exclude(istifadeci_id__in=Bloklama.bloklanmis_idler(user))


def check_access(ad, user):
    if user.is_authenticated and (user.pk == ad.istifadeci_id or user.has_perm('core.view_elan')):
        return
    if (ad.status != 'aktiv' or (ad.bitis_tarixi and ad.bitis_tarixi <= timezone.now())
            or ad.istifadeci_id in Bloklama.bloklanmis_idler(user)):
        from django.http import Http404
        raise Http404


def check_messaging(user, other_id):
    if other_id == user.pk or other_id in Bloklama.bloklanmis_idler(user):
        raise PermissionDenied('Bu istifadəçi ilə mesajlaşma mümkün deyil.')


def category(value):
    try:
        return Kategori.objects.get(pk=int(value))
    except (ValueError, TypeError, Kategori.DoesNotExist):
        raise ValidationError('Kateqoriya tapılmadı.')


def prepare_images(files):
    if len(files) > 5:
        raise ValidationError('Maksimum 5 şəkil yükləyə bilərsiniz.')
    result = []
    for file in files:
        normalized = image_upload(file)
        blocked, reason = filigran_yoxla(file)
        if blocked:
            raise ValidationError(reason)
        result.append(normalized)
    return result


@contextmanager
def upload_guard():
    written = []
    try:
        yield written
    except Exception:
        from .media_cleanup import enqueue
        for name in written:
            enqueue(name)
        raise


def store_image(ad, image, written, *, primary=False):
    record = ElanShekil(elan=ad, shekil=image, esas=primary)
    try:
        record.save()
    finally:
        if record.shekil and record.shekil._committed:
            written.append(record.shekil.name)
    return record


def active_for_user(user):
    return Elan.objects.filter(istifadeci=user).filter(
        Q(status='gozlemede') | (Q(status='aktiv') & (
            Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=timezone.now()))))


def check_duplicate(user, cat, exclude=None):
    qs = active_for_user(user).filter(kategori=cat)
    if exclude:
        qs = qs.exclude(pk=exclude)
    if qs.exists():
        raise ValidationError('Bu kateqoriyada artıq aktiv elanınız var.')


def create_listing(user, data, files):
    values = listing_values(data)
    cat = category(data.get('kategori'))
    if not files:
        raise ValidationError('Ən azı 1 şəkil yükləyin.')
    images = prepare_images(files)
    with upload_guard() as written, transaction.atomic():
        Profil.objects.get_or_create(istifadeci=user)
        profile = Profil.objects.select_for_update().get(istifadeci=user)
        check_duplicate(user, cat)
        charged = active_for_user(user).count() >= 4
        if charged:
            if profile.balans < Decimal('1.00'):
                raise ValidationError('Pulsuz elan limiti bitib. Balansınız kifayət deyil.')
            profile.balans -= Decimal('1.00')
            profile.save(update_fields=['balans'])
        ad = Elan.objects.create(istifadeci=user, kategori=cat, status='aktiv',
                                 bitis_tarixi=timezone.now() + timedelta(days=30), **values)
        if charged:
            Odenis.objects.create(istifadeci=user, elan=ad, nov='elan', mebleg=Decimal('1.00'),
                                  status='tesdiq_edildi', applied_at=timezone.now())
        for index, image in enumerate(images):
            store_image(ad, image, written, primary=index == 0)
        return ad


def update_listing(user, ad_id, data, files, delete_ids=()):
    images = prepare_images(files)
    try:
        if isinstance(delete_ids, str):
            import json
            delete_ids = json.loads(delete_ids)
        if not isinstance(delete_ids, (list, tuple)):
            raise ValueError
        delete_ids = [int(value) for value in delete_ids]
    except (ValueError, TypeError):
        raise ValidationError('Silinəcək şəkillərin siyahısı düzgün deyil.')
    with upload_guard() as written, transaction.atomic():
        Profil.objects.get_or_create(istifadeci=user)
        Profil.objects.select_for_update().get(istifadeci=user)
        ad = Elan.objects.select_for_update().get(pk=ad_id, istifadeci=user)
        merged = {key: data.get(key, getattr(ad, key)) for key in (
            'bashliq', 'acaqlama', 'qiymet', 'telefon', 'sheher')}
        values = listing_values(merged)
        cat = category(data.get('kategori') or data.get('kategori_id') or ad.kategori_id)
        if ad.status in ('aktiv', 'gozlemede'):
            check_duplicate(user, cat, exclude=ad.pk)
        remaining = ad.shekillar.exclude(pk__in=delete_ids).count()
        if remaining + len(images) > 5:
            raise ValidationError('Maksimum 5 şəkil yükləyə bilərsiniz.')
        for key, value in values.items():
            setattr(ad, key, value)
        ad.kategori = cat
        ad.save()
        ad.shekillar.filter(pk__in=delete_ids).delete()
        for image in images:
            store_image(ad, image, written)
        if not ad.shekillar.filter(esas=True).exists():
            first = ad.shekillar.order_by('pk').first()
            if first:
                first.esas = True
                first.save(update_fields=['esas'])
        return ad


@transaction.atomic
def reactivate_listing(user, ad_id):
    Profil.objects.get_or_create(istifadeci=user)
    profile = Profil.objects.select_for_update().get(istifadeci=user)
    ad = Elan.objects.select_for_update().get(pk=ad_id, istifadeci=user)
    if active_for_user(user).filter(pk=ad.pk).exists():
        raise ValidationError('Elan artıq aktivdir və ya moderasiyadadır.')
    check_duplicate(user, ad.kategori, exclude=ad.pk)
    if active_for_user(user).count() >= 4:
        if profile.balans < Decimal('1.00'):
            raise ValidationError('Pulsuz elan limiti bitib. Balansınız kifayət deyil.')
        profile.balans -= Decimal('1.00')
        profile.save(update_fields=['balans'])
        Odenis.objects.create(istifadeci=user, elan=ad, nov='elan', mebleg=Decimal('1.00'),
                              status='tesdiq_edildi', applied_at=timezone.now())
    ad.status = 'gozlemede'
    ad.bitis_tarixi = timezone.now() + timedelta(days=30)
    ad.save()
    return ad
