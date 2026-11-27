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
    ai_bots = ('OAI-SearchBot', 'ChatGPT-User', 'GPTBot', 'Claude-SearchBot',
               'ClaudeBot', 'PerplexityBot', 'Google-Extended', 'Applebot-Extended')
    lines = ['User-agent: *', 'Allow: /static/', 'Allow: /media/']
    lines += ['Disallow: /' + path for path in private]
    for bot in ai_bots:
        lines += ['', f'User-agent: {bot}', 'Allow: /']
        lines += ['Disallow: /' + path for path in private]
    # Search/facet URLs stay crawlable so their noindex directive can be seen.
    lines += ['', f'Sitemap: {SITE_URL}/sitemap.xml', '']
    return text_response(request, '\n'.join(lines), 3600)


def _markdown_label(value):
    return ' '.join(str(value).split()).replace('\\', '\\\\').replace('[', '\\[').replace(']', '\\]')


def llms_response(request):
    from django.db.models import Count, Min, Max
    from .models import Kategori, Problem
    from .seo_locations import active_public_listings, indexable_location_pairs
    from .locations import LOKASIYALAR
    content = cache.get('prousta_llms_txt_v4')
    if content is None:
        categories = list(Kategori.objects.filter(pk__in=indexable_kategori_ids()).order_by('ad').values('pk', 'ad', 'slug', 'ust_kategori_id')[:300])
        articles = list(Problem.objects.filter(aktiv=True).order_by('bashliq').values('bashliq', 'slug')[:100])
        active_ads = active_public_listings()
        stats_by_cat = {
            row['kategori_id']: row
            for row in active_ads.order_by().values('kategori_id').annotate(
                total=Count('pk'), min_p=Min('qiymet'), max_p=Max('qiymet')
            )
        }
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
        for row in categories:
            st = stats_by_cat.get(row['pk'])
            meta_suffix = ''
            if st and st['total']:
                parts = [f"{st['total']} aktiv elan"]
                if st['min_p'] is not None:
                    min_v = int(st['min_p']) if st['min_p'] == int(st['min_p']) else st['min_p']
                    max_v = int(st['max_p']) if st['max_p'] == int(st['max_p']) else st['max_p']
                    price_range = f"{min_v}–{max_v} AZN" if max_v != min_v else f"{min_v} AZN"
                    parts.append(f"elan qiymətləri: {price_range}")
                meta_suffix = ' — ' + ', '.join(parts)
            lines.append(f'- [{_markdown_label(row["ad"])}]({SITE_URL}/xidmet/{row["slug"]}/){meta_suffix}')
        from .service_pages import topics
        valid_categories = set(Kategori.objects.values_list('slug', flat=True))
        lines += ['', '## Xüsusi xidmət bələdçiləri']
        lines += [f'- [{_markdown_label(page["name"])}]({SITE_URL}{page["url"]}): {_markdown_label(page["summary"])}'
                  for page in topics() if page['category'] in valid_categories]
        cat_names = {row['slug']: row['ad'] for row in categories}
        loc_pairs = indexable_location_pairs()
        if loc_pairs:
            lines += ['', '## Rayon və şəhərlər üzrə lokal xidmət səhifələri']
            for cat_slug, loc_slug in loc_pairs[:60]:
                cat_label = cat_names.get(cat_slug, cat_slug)
                loc_info = LOKASIYALAR.get(loc_slug, {})
                loc_label = loc_info.get('ad', loc_slug)
                erazi_note = f' ({loc_info["erazi"]})' if loc_info.get('erazi') else ''
                lines.append(f'- [{_markdown_label(f"{cat_label} — {loc_label}")}]({SITE_URL}/xidmet/{cat_slug}/{loc_slug}/){erazi_note}')
        lines += ['', '## Bələdçilər']
        lines += [f'- [{_markdown_label(row["bashliq"])}]({SITE_URL}/problemler/{row["slug"]}/)' for row in articles]
        from .ru_content import category_name_ru, priority_page_ru
        lines += ['', '## Русская версия (/ru/)',
                  f'- [Главная (Поиск мастеров в Баку)]({SITE_URL}/ru/)',
                  f'- [Все объявления и услуги]({SITE_URL}/ru/elanlar/)',
                  f'- [О платформе]({SITE_URL}/ru/haqqimizda/)']
        for row in categories[:25]:
            ru_label = _markdown_label(category_name_ru(row['slug']) or row['ad'])
            lines.append(f'- [{ru_label}]({SITE_URL}/ru/xidmet/{row["slug"]}/)')
        for page in topics():
            if page['category'] in valid_categories:
                ru_topic = priority_page_ru(page)
                lines.append(f'- [{_markdown_label(ru_topic["name"])}]({SITE_URL}{ru_topic["url"]})')
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
