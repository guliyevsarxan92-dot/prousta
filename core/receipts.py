from django.core import signing
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_GET

from .models import Odenis


@require_GET
def download(request, pk):
    payment = get_object_or_404(Odenis, pk=pk)
    user = request.user
    allowed = user.is_authenticated and (user.pk == payment.istifadeci_id or user.has_perm('core.view_odenis'))
    if not allowed:
        try:
            data = signing.loads(request.GET.get('t', ''), salt='receipt-download', max_age=300)
            allowed = data == {'payment': pk, 'user': payment.istifadeci_id}
        except signing.BadSignature:
            pass
    if not allowed or not payment.qebz:
        raise Http404
    try:
        file = payment.qebz.open('rb')
    except (FileNotFoundError, OSError):
        raise Http404
    response = FileResponse(file, content_type='image/jpeg')
    response['Cache-Control'] = 'private, no-store'
    response['Referrer-Policy'] = 'no-referrer'
    response['X-Robots-Tag'] = 'noindex, nofollow'
    return response
