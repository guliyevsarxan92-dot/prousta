from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Mesaj, Kategori, ReklamBanner

def oxunmamis_mesaj(request):
    try:
        nav_kateqoriyalar = cache.get('nav_kateqoriyalar')
        if nav_kateqoriyalar is None:
            nav_kateqoriyalar = list(Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar'))
            cache.set('nav_kateqoriyalar', nav_kateqoriyalar, 300)
    except Exception:
        nav_kateqoriyalar = []

    # Reklam bannerləri (Tap.az üslubunda sol, sağ və orta)
    reklamlar = {}
    try:
        reklamlar = cache.get('reklam_bannerleri')
        if reklamlar is None:
            reklamlar = {}
            now = timezone.now()
            for r in ReklamBanner.objects.filter(aktiv=True):
                if r.bitis_tarixi and r.bitis_tarixi < now:
                    continue
                reklamlar[r.movqe] = r
            cache.set('reklam_bannerleri', reklamlar, 180)
    except Exception:
        reklamlar = {}

    ctx = {
        'nav_kateqoriyalar': nav_kateqoriyalar,
        'YANDEX_VERIFICATION': getattr(settings, 'YANDEX_VERIFICATION', ''),
        'reklam_sol': reklamlar.get('sol'),
        'reklam_sag': reklamlar.get('sag'),
        'reklam_orta': reklamlar.get('orta'),
    }
    user = getattr(request, 'user', None)
    if user and getattr(user, 'is_authenticated', False):
        try:
            ctx['oxunmamis_mesaj'] = Mesaj.objects.filter(alici=user, oxundu=False).count()
        except Exception:
            ctx['oxunmamis_mesaj'] = 0
        try:
            ctx['user_balans'] = getattr(user.profil, 'balans', 0)
        except Exception:
            ctx['user_balans'] = 0
    else:
        ctx['oxunmamis_mesaj'] = 0
        ctx['user_balans'] = 0
    return ctx
