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
        try:
            peer = ipaddress.ip_address(request.META.get('REMOTE_ADDR', ''))
        except ValueError:
            peer = None
        if peer is not None and self.trusted(peer):
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
