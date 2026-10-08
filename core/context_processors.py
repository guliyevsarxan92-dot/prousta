from django.conf import settings
from django.core.cache import cache
from django.utils import timezone
from .models import Mesaj, Kategori, ReklamBanner

def oxunmamis_mesaj(request):
    nav_kateqoriyalar = cache.get('nav_kateqoriyalar')
    if nav_kateqoriyalar is None:
        nav_kateqoriyalar = list(Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar'))
        cache.set('nav_kateqoriyalar', nav_kateqoriyalar, 300)

    # Reklam bannerləri (Tap.az üslubunda sol, sağ və orta)
    reklamlar = cache.get('reklam_bannerleri')
    if reklamlar is None:
        reklamlar = {}
        now = timezone.now()
        for r in ReklamBanner.objects.filter(aktiv=True):
            if r.bitis_tarixi and r.bitis_tarixi < now:
                continue
            reklamlar[r.movqe] = r
        cache.set('reklam_bannerleri', reklamlar, 180)

    ctx = {
        'nav_kateqoriyalar': nav_kateqoriyalar,
        'YANDEX_VERIFICATION': getattr(settings, 'YANDEX_VERIFICATION', ''),
        'reklam_sol': reklamlar.get('sol'),
        'reklam_sag': reklamlar.get('sag'),
        'reklam_orta': reklamlar.get('orta'),
    }
    if request.user.is_authenticated:
        ctx['oxunmamis_mesaj'] = Mesaj.objects.filter(alici=request.user, oxundu=False).count()
        try:
            ctx['user_balans'] = request.user.profil.balans
        except Exception:
            ctx['user_balans'] = 0
    else:
        ctx['oxunmamis_mesaj'] = 0
        ctx['user_balans'] = 0
    return ctx
