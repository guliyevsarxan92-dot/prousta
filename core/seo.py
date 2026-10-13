"""
Mərkəzləşdirilmiş SEO köməkçiləri.

- seo_context: hər səhifə üçün düzgün canonical URL və noindex qərarı.
- CanonicalHostMiddleware: www → apex 301 və texniki domenlərdə (onrender.com və s.) X-Robots-Tag: noindex.
"""
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

SITE_URL = 'https://prousta.az'
CANONICAL_HOST = 'prousta.az'

# Bu GET parametrləri olan səhifələr dublikat/axtarış səhifəsidir → noindex, follow
_NOINDEX_PARAMS = {'q', 'seed', 'ajax', 'kategori', 'next', 'sort', 'utm_source', 'utm_medium',
                   'utm_campaign', 'fbclid', 'gclid'}


def _page_number(request):
    try:
        return max(int(request.GET.get('page', 1)), 1)
    except (TypeError, ValueError):
        return 1


def seo_context(request):
    path = request.path
    page = _page_number(request)
    params = set(request.GET.keys())

    noindex = bool(params & _NOINDEX_PARAMS)
    # Ana səhifənin ?page=N variantları /elanlar/ ilə dublikatdır
    if path == '/' and page > 1:
        noindex = True

    canonical = path
    if page > 1 and path != '/':
        # Google tövsiyəsi: səhifələnmiş siyahılar öz-özünə canonical olmalıdır
        canonical = f'{path}?page={page}'

    return {
        'SITE_URL': SITE_URL,
        'seo_canonical': canonical,
        'seo_noindex': noindex,
        'seo_page': page,
        'GOOGLE_SITE_VERIFICATION': getattr(settings, 'GOOGLE_SITE_VERIFICATION', ''),
    }


def indexable_kategori_ids():
    """
    İndekslənməyə layiq kateqoriya ID-ləri (10 dəq keşlənir):
    - SEO mətni (seo_metn) olan kateqoriyalar — boş olsa belə unikal məzmunu var;
    - aktiv elanı olan kateqoriyalar və onların üst kateqoriyaları.
    View, sitemap və daxili link blokları eyni qaydanı istifadə edir ki, ziddiyyət olmasın.
    """
    from django.core.cache import cache
    from django.db.models import Q
    from django.utils import timezone
    from .models import Kategori, Elan

    ids = cache.get('seo_indexable_kat_ids')
    if ids is not None:
        return ids
    now = timezone.now()
    aktiv = Elan.objects.filter(status='aktiv').filter(
        Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=now)
    )
    with_ads = set(aktiv.values_list('kategori_id', flat=True).distinct())
    parents = set(
        Kategori.objects.filter(pk__in=with_ads, ust_kategori__isnull=False)
        .values_list('ust_kategori_id', flat=True)
    )
    with_text = set(Kategori.objects.exclude(seo_metn='').values_list('pk', flat=True))
    ids = frozenset((with_ads | parents | with_text) - {None})
    cache.set('seo_indexable_kat_ids', ids, 600)
    return ids


class CanonicalHostMiddleware:
    """
    Dublikat domen problemini həll edir:
    - www.prousta.az → https://prousta.az (301)
    - Digər texniki hostlar (*.onrender.com, *.railway.app) indekslənməsin deyə X-Robots-Tag əlavə olunur.
    Yalnız DEBUG=False olduqda işləyir.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if settings.DEBUG:
            return self.get_response(request)

        host = request.get_host().split(':')[0].lower()
        if host == f'www.{CANONICAL_HOST}' and request.method in ('GET', 'HEAD'):
            return HttpResponsePermanentRedirect(f'{SITE_URL}{request.get_full_path()}')

        response = self.get_response(request)
        if host not in (CANONICAL_HOST, f'www.{CANONICAL_HOST}', 'localhost', '127.0.0.1'):
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
