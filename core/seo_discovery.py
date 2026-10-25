"""Public crawl policy and a factual, bounded directory of authoritative pages."""
import hashlib
from urllib.parse import urlsplit

from django.core.cache import cache
from django.http import HttpResponse
from django.utils.cache import get_conditional_response
from django.utils.http import quote_etag

from .seo import SITE_URL, indexable_kategori_ids


def text_response(request, text, max_age):
    response = HttpResponse(text, content_type='text/plain; charset=utf-8')
    etag = quote_etag(hashlib.sha256(response.content).hexdigest())
    response['ETag'] = etag
    response['Cache-Control'] = f'public, max-age={max_age}'
    return get_conditional_response(request, etag=etag, response=response)


def robots_response(request):
    private = ['admin/', 'api/', 'profil/', 'mesajlar/', 'mesaj/', 'odenis/', 'qebz/',
               'favorit/', 'elan/yeni/', 'elan/*/duzelis/', 'elan/*/sil/',
               'elan/*/aktivlesdir/', 'elan/*/klik/', 'shekil/', 'vip/', 'cixis/',
               'sifre-unutdum/', 'sifre-yenile/', 'sifre-yenilendi/', 'giris/',
               'qeydiyyat/', 'mobile/', 'social-auth/', 'health/', 'banner/']
    lines = ['User-agent: *', 'Allow: /static/', 'Allow: /media/']
    lines += ['Disallow: /' + path for path in private]
    # Search/facet URLs stay crawlable so their noindex directive can be seen.
    lines += ['', f'Sitemap: {SITE_URL}/sitemap.xml', '']
    return text_response(request, '\n'.join(lines), 3600)


def _markdown_label(value):
    return ' '.join(str(value).split()).replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')


def llms_response(request):
    from .models import Kategori, Problem
    content = cache.get('prousta_llms_txt_v4')
    if content is None:
        categories = list(Kategori.objects.filter(pk__in=indexable_kategori_ids()).order_by('ad').values('ad', 'slug')[:300])
        articles = list(Problem.objects.filter(aktiv=True).order_by('bashliq').values('bashliq', 'slug')[:100])
        lines = [
            '# Prousta.az', '',
            '> Azərbaycanda usta və xidmət elanları platforması. İstifadəçi elanları müqayisə edib elan sahibi ilə telefon və ya WhatsApp vasitəsilə birbaşa əlaqə saxlayır.', '',
            '## Platforma haqqında',
            '- Prousta.az elanları təqdim edən platformadır; xidmətin faktiki icraçısı elan sahibidir.',
            '- Qiymət, ərazi və iş təsviri elan sahibi tərəfindən verilir. Yekun qiymət, gəliş vaxtı və zəmanət şərtləri onunla ayrıca razılaşdırılır.',
            '- VIP nişanı ödənişli göstərim xidmətidir; ixtisas, sertifikat və ya iş keyfiyyətinin təsdiqi deyil.',
            '- Lokal səhifələrdə digər ərazilərin elanları da göstərilə bilər. Xidmətin konkret ünvana göstəriləcəyini elan sahibi ilə dəqiqləşdirmək lazımdır.', '',
            '## Əsas səhifələr',
            f'- [Elanlar]({SITE_URL}/elanlar/)',
            f'- [Platforma haqqında]({SITE_URL}/haqqimizda/)',
            f'- [Təmir bələdçiləri]({SITE_URL}/problemler/)',
            f'- [İstifadə şərtləri]({SITE_URL}/istifade-sertleri/)',
            f'- [Məxfilik siyasəti]({SITE_URL}/gizlilik/)', '',
            '## Xidmət kateqoriyaları',
        ]
        lines += [f'- [{_markdown_label(row["ad"])}]({SITE_URL}/xidmet/{row["slug"]}/)' for row in categories]
        lines += ['', '## Bələdçilər']
        lines += [f'- [{_markdown_label(row["bashliq"])}]({SITE_URL}/problemler/{row["slug"]}/)' for row in articles]
        lines += ['', '## Əlaqə və digər mənbələr', '- Email: info@prousta.az',
                  f'- XML sitemap: {SITE_URL}/sitemap.xml',
                  '- Kataloqdakı elan və qiymətlər dəyişə bilər; cari məlumat üçün əlaqəli səhifəyə baxın.', '']
        content = '\n'.join(lines)
        cache.set('prousta_llms_txt_v4', content, 300)
    return text_response(request, content, 300)


def sitemap_index(request, *args, **kwargs):
    from django.contrib.sitemaps.views import index
    response = index(request, *args, **kwargs)
    for item in response.context_data['sitemaps']:
        parts = urlsplit(item.location)
        item.location = SITE_URL + parts.path + ('?' + parts.query if parts.query else '')
    return response
