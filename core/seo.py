"""
Mərkəzləşdirilmiş SEO köməkçiləri.

- seo_context: hər səhifə üçün düzgün canonical URL və noindex qərarı.
- CanonicalHostMiddleware: www → apex 301 və texniki hostlarda (IP ünvanı və s.) X-Robots-Tag: noindex.
"""
from django.conf import settings
from django.http import HttpResponsePermanentRedirect

SITE_URL = 'https://prousta.az'
CANONICAL_HOST = 'prousta.az'

# Bu GET parametrləri olan səhifələr dublikat/axtarış səhifəsidir → noindex, follow
_NOINDEX_PARAMS = {'q', 'ajax', 'kategori', 'k', 'next', 'sort', 'sheher', 'city', 'min_price', 'max_price'}
_PAGINATED_PATHS = ('/elanlar/', '/problemler/', '/xidmet/')
PUBLIC_VIEWS = {
    'index', 'elan_siyahi', 'xidmet_detail', 'xidmet_lokasiya_detail', 'elan_detail',
    'problemler_siyahi', 'problem_detail', 'haqqimizda', 'gizlilik',
    'istifade_sertleri', 'mobil_app',
}


def _page_number(request):
    try:
        return max(int(request.GET.get('page', 1)), 1)
    except (TypeError, ValueError):
        return 1


def seo_context(request):
    path = request.path
    page = _page_number(request)
    params = {key for key, value in request.GET.items() if value.strip()}

    noindex = bool(params & _NOINDEX_PARAMS)
    # Ana səhifənin ?page=N variantları /elanlar/ ilə dublikatdır
    if path == '/' and page > 1:
        noindex = True

    canonical = path
    paginated = path.startswith(_PAGINATED_PATHS)
    if page > 1 and paginated:
        # Google tövsiyəsi: səhifələnmiş siyahılar öz-özünə canonical olmalıdır
        canonical = f'{path}?page={page}'
    elif page > 1:
        noindex = True

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
    with_text = set(Kategori.objects.exclude(seo_metn__regex=r'^\s*$').values_list('pk', flat=True))
    ids = frozenset((with_ads | parents | with_text) - {None})
    next_expiry = aktiv.filter(bitis_tarixi__isnull=False).order_by('bitis_tarixi').values_list('bitis_tarixi', flat=True).first()
    timeout = min(60, max(1, int((next_expiry - now).total_seconds()))) if next_expiry else 60
    cache.set('seo_indexable_kat_ids', ids, timeout)
    return ids


class CanonicalHostMiddleware:
    """
    Dublikat domen problemini həll edir:
    - www.prousta.az → https://prousta.az (301)
    - Digər texniki hostlar (məs. birbaşa IP ünvanı) indekslənməsin deyə X-Robots-Tag əlavə olunur.
    Yalnız DEBUG=False olduqda işləyir.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/'):
            if request.method == 'OPTIONS':
                from django.http import HttpResponse
                resp = HttpResponse(status=200)
                resp['Access-Control-Allow-Origin'] = '*'
                resp['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
                resp['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
                return resp
            response = self.get_response(request)
            response['X-Robots-Tag'] = 'noindex, nofollow'
            response['Access-Control-Allow-Origin'] = '*'
            response['Access-Control-Allow-Methods'] = 'GET, POST, PUT, PATCH, DELETE, OPTIONS'
            response['Access-Control-Allow-Headers'] = 'Origin, Content-Type, Accept, Authorization'
            return response

        if settings.DEBUG:
            return self.finish(request, self.get_response(request))

        host = request.get_host().split(':')[0].lower()
        if host == f'www.{CANONICAL_HOST}' and request.method in ('GET', 'HEAD'):
            return HttpResponsePermanentRedirect(f'{SITE_URL}{request.get_full_path()}')

        response = self.finish(request, self.get_response(request))
        if host not in (CANONICAL_HOST, f'www.{CANONICAL_HOST}', 'localhost', '127.0.0.1'):
            response['X-Robots-Tag'] = 'noindex, nofollow'
        return response

    @staticmethod
    def finish(request, response):
        if response.status_code >= 400:
            response['X-Robots-Tag'] = 'noindex, nofollow'
        elif getattr(request, '_seo_robots', '').startswith('noindex'):
            response['X-Robots-Tag'] = request._seo_robots
        elif getattr(request, 'resolver_match', None) and request.resolver_match.url_name not in PUBLIC_VIEWS:
            if request.path not in ('/robots.txt', '/llms.txt') and not request.path.startswith('/sitemap'):
                response['X-Robots-Tag'] = 'noindex, nofollow'
        return response
