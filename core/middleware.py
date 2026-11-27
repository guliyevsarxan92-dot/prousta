import ipaddress

from django.conf import settings


class TrustedProxyMiddleware:
    """Accept forwarded addresses/protocol only from configured proxy networks."""
    def __init__(self, get_response):
        self.get_response = get_response
        self.networks = [ipaddress.ip_network(cidr) for cidr in settings.TRUSTED_PROXY_CIDRS]

    def trusted(self, address):
        return any(address in network for network in self.networks)

    def __call__(self, request):
        raw_peer = request.META.get('REMOTE_ADDR', '')
        try:
            peer = ipaddress.ip_address(raw_peer)
        except ValueError:
            peer = None
        # Local Unix socket (Nginx -> Gunicorn) sets REMOTE_ADDR == ''
        if raw_peer == '' or (peer is not None and self.trusted(peer)):
            chain = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')
            try:
                addresses = [ipaddress.ip_address(value.strip()) for value in chain if value.strip()]
            except ValueError:
                addresses = []
            for address in reversed(addresses):
                if not self.trusted(address):
                    request.META['REMOTE_ADDR'] = str(address)
                    break
        else:
            request.META.pop('HTTP_X_FORWARDED_PROTO', None)
        request.META.pop('HTTP_X_FORWARDED_FOR', None)
        return self.get_response(request)


class SecurityHeadersMiddleware:
    """Brauzer səviyyəsində əlavə qoruyucu başlıqlar və şəxsi səhifələrin keşlənməməsi."""
    PRIVATE_PREFIXES = ('/profil', '/odenis', '/mesaj', '/qebz', '/admin', '/api/', '/sifre', '/giris', '/qeydiyyat')

    def __init__(self, get_response):
        self.get_response = get_response
        self.permissions_policy = getattr(settings, 'PERMISSIONS_POLICY', '')

    def __call__(self, request):
        response = self.get_response(request)
        if self.permissions_policy:
            response.setdefault('Permissions-Policy', self.permissions_policy)
        response.setdefault('X-Content-Type-Options', 'nosniff')
        # Şəxsi məlumat olan səhifələr (balans, mesaj, ödəniş) paylaşılan keşlərdə saxlanmasın.
        if request.path.startswith(self.PRIVATE_PREFIXES) or getattr(request, 'user', None) and request.user.is_authenticated:
            if 'no-store' not in response.get('Cache-Control', ''):
                response['Cache-Control'] = 'private, no-store, max-age=0'

        # İstifadəçinin seçdiyi dili (az / ru) cookie-də saxla ki, /profil/, /mesajlar/, /odenis/ kimi
        # ortaq səhifələrə keçdikdə dil avtomatik dəyişməsin.
        path = request.path or '/'
        q_lang = request.GET.get('lang', '').strip().lower()
        target_lang = None
        if q_lang in ('az', 'ru'):
            target_lang = q_lang
        elif path == '/ru' or path.startswith('/ru/'):
            target_lang = 'ru'
        elif (
            path == '/'
            or path.startswith(('/elanlar/', '/xidmet/', '/haqqimizda/'))
            or (path.startswith('/elan/') and not path.startswith('/elan/yeni/') and '/klik/' not in path and '/ireli-cek/' not in path)
        ):
            target_lang = 'az'

        if target_lang and request.COOKIES.get('prousta_lang') != target_lang:
            response.set_cookie(
                'prousta_lang',
                target_lang,
                max_age=365 * 24 * 3600,
                path='/',
                samesite='Lax',
            )
        return response
