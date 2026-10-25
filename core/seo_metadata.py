"""One source for canonical URLs, share metadata and safely serialized JSON-LD."""
import json
import re
from html import unescape
from urllib.parse import urljoin, urlsplit

from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.utils.html import strip_tags

from .seo import PUBLIC_VIEWS, SITE_URL, seo_context
from .service_content import get_content, metadata_value

BRAND = 'Prousta.az'
ORGANIZATION_ID = SITE_URL + '/#organization'
WEBSITE_ID = SITE_URL + '/#website'
DEFAULT_IMAGE = SITE_URL + '/static/og-image.jpg'

STATIC_PAGES = {
    'index': ('Usta tapın — xidmət elanları və qiymətlər | Prousta.az',
              'Usta və xidmət elanlarını müqayisə edin. Elektrik, santexnik, kombi, kondisioner və digər xidmətlər üçün elan sahibinə birbaşa zəng və ya WhatsApp ilə yazın.'),
    'elan_siyahi': ('Usta elanları və xidmət qiymətləri | Prousta.az',
                    'Aktiv usta elanlarını, qiymətləri və iş nümunələrini müqayisə edin. Xidmətin ərazisini, vaxtını və yekun qiymətini elan sahibi ilə razılaşdırın.'),
    'problemler_siyahi': ('Texniki problemlər və təmir bələdçiləri | Prousta.az',
                         'Məişət texnikası və ev təmiri problemləri haqqında bələdçilər. Nasazlıq əlamətlərini, mümkün səbəbləri və xidmət seçimi barədə məlumatı oxuyun.'),
    'haqqimizda': ('Haqqımızda — xidmət elanları platforması | Prousta.az',
                  'Prousta.az platformasının necə işlədiyini, xidmət elanlarını necə müqayisə etməyi və elan sahibi ilə necə əlaqə saxlamağı öyrənin.'),
    'gizlilik': ('Məxfilik siyasəti | Prousta.az', 'Prousta.az platformasında şəxsi məlumatların emalı və məxfiliyə dair qaydalar.'),
    'istifade_sertleri': ('İstifadə şərtləri | Prousta.az', 'Prousta.az platformasından istifadə, elan yerləşdirmə və xidmətlə bağlı şərtlər.'),
    'mobil_app': ('Prousta.az mobil tətbiqi', 'Prousta.az mobil tətbiqi ilə xidmət elanlarını axtarın və elan sahibləri ilə birbaşa əlaqə saxlayın.'),
}


def plain(value, limit=None):
    value = ' '.join(unescape(strip_tags(str(value or ''))).split())
    if limit and len(value) > limit:
        return value[:limit - 1].rsplit(' ', 1)[0] + '…'
    return value


def absolute_url(value):
    value = str(value or '')
    url = urljoin(SITE_URL + '/', value)
    return url if urlsplit(url).scheme in ('http', 'https') else DEFAULT_IMAGE


def safe_json(value):
    # Raw JSON script content is not HTML-escaped; escape script terminators instead.
    return json.dumps(value, ensure_ascii=False, separators=(',', ':')).replace(
        '<', '\\u003C').replace('>', '\\u003E').replace('&', '\\u0026').replace(
        '\u2028', '\\u2028').replace('\u2029', '\\u2029')


def service_faq(context):
    category = context['aktiv_kategori']
    location = context.get('lokasiya_melumat')
    area = location['ad'] + ' ərazisində' if location else 'Bakıda'
    minimum = context.get('min_qiymet')
    price = (f'Prousta.az-da {category.ad.lower()} üzrə elanlarda qiymətlər təxminən '
             f'{floatformat(minimum, "-2")} AZN-dən başlayır.' if minimum
             else 'Qiymət görüləcək işin həcminə və mürəkkəbliyinə görə dəyişir.')
    location_note = (' Burada digər ərazilərin elanları da göstərilir; elan qiyməti konkret ünvana xidmətin yekun qiymətini təsdiqləmir.' if location else '')
    questions = [
        (f'{area} {category.ad.lower()} üzrə xidmətin qiyməti nə qədərdir?',
         price + ' Bir neçə mütəxəssisin elanına baxaraq qiymətləri müqayisə edə və ən sərfəli variantı seçə bilərsiniz.' + location_note),
        (f'{category.ad} üzrə xidmət necə sifariş edilir?',
         'Prousta.az-da heç bir vasitəçi yoxdur. Elan kartındakı «Zəng et» və ya «WhatsApp» düymələrinə toxunaraq birbaşa mütəxəssislə əlaqə saxlaya və sifarişinizi qeydiyyatdan keçirə bilərsiniz.'),
        ('Xidmətə və görülən işə zəmanət verilirmi?',
         'Zəmanət şərtləri xidmətin növünə və mütəxəssisin təklifinə görə dəyişir. Sifarişdən əvvəl görüləcək işi, zəmanətin olub-olmadığını və müddətini seçdiyiniz mütəxəssislə dəqiqləşdirin.'),
    ]
    content = get_content(category)
    if content:
        question, answer = questions[0]
        answer += ' Qiymətə təsir edən amillər: ' + '; '.join(content['pricing']) + '.'
        return [(question, answer), *[tuple(item) for item in content['questions']]]
    return questions


def _organization():
    return {'@type': 'Organization', '@id': ORGANIZATION_ID, 'name': BRAND,
            'url': SITE_URL + '/', 'logo': {'@type': 'ImageObject',
            'url': SITE_URL + '/static/img/icon_512.png'}, 'email': 'info@prousta.az',
            'contactPoint': {'@type': 'ContactPoint', 'telephone': '+994515888884',
                             'contactType': 'customer support', 'availableLanguage': ['az']},
            'sameAs': ['https://www.facebook.com/61568796886691',
                       'https://www.instagram.com/prousta.az',
                       'https://www.youtube.com/@prousta.servis.merkezi']}


def _item_list(page, model='listing'):
    if page is None or not hasattr(page, 'paginator'):
        return None
    items = []
    start = page.start_index()
    for position, item in enumerate(page, start=start):
        items.append({'@type': 'ListItem', 'position': position,
                      'url': absolute_url(item.get_absolute_url()), 'name': plain(item.bashliq)})
    return {'@type': 'ItemList', 'numberOfItems': page.paginator.count,
            'itemListElement': items}


def build_metadata(context):
    request = context.get('request')
    category = context.get('aktiv_kategori')
    ad = context.get('elan')
    article = context.get('problem')
    location = context.get('lokasiya_melumat')
    match = getattr(request, 'resolver_match', None)
    view = getattr(match, 'url_name', '')
    page_number = context.get('seo_page', 1)
    canonical_path = context.get('seo_canonical') or '/'
    noindex = bool(context.get('seo_noindex'))
    if request is not None:
        base = seo_context(request)
        canonical_path, page_number, noindex = base['seo_canonical'], base['seo_page'], base['seo_noindex']
    if category:
        view = 'xidmet_detail'
        canonical_path = f'/xidmet/{category.slug}/'
        if location:
            canonical_path += location['slug'] + '/'
        if page_number > 1:
            canonical_path += f'?page={page_number}'
        noindex |= not context.get('kat_indexable', False)
    elif ad:
        view = 'elan_detail'
        canonical_path = ad.get_absolute_url()
        noindex |= ad.status != 'aktiv' or bool(ad.bitis_tarixi and ad.bitis_tarixi <= timezone.now())
    elif article:
        view = 'problem_detail'
        canonical_path = article.get_absolute_url()

    public = view in PUBLIC_VIEWS
    noindex |= not public or bool(context.get('home_is_demo'))
    private_titles = {'giris': 'Daxil olun', 'qeydiyyat': 'Qeydiyyat', 'profil': 'Profilim',
                      'profil_duzelis': 'Profili redaktə et', 'mesajlar': 'Mesajlar',
                      'sifre_unutdum': 'Şifrənin bərpası', 'elan_yarat': 'Elan yerləşdir',
                      'odenis': 'Ödəniş', 'istifadeci_profil': 'Elan sahibinin profili'}
    title, description = STATIC_PAGES.get(view, (
        (private_titles[view] + ' | ' + BRAND) if view in private_titles else BRAND,
        'Usta və xidmət elanları platforması.'))
    image, image_default = DEFAULT_IMAGE, True
    crumbs = [('Ana səhifə', '/')]
    page_type = 'WebPage'
    if view == 'haqqimizda':
        page_type = 'AboutPage'
    extra = []
    if category:
        title = metadata_value(category, 'seo_title') or f'{category.ad} — ustalar və xidmət qiymətləri | {BRAND}'
        description = metadata_value(category, 'seo_description') or (
            f'{category.ad} üzrə aktiv elanları, qiymətləri və iş nümunələrini müqayisə edin. '
            'Elan sahibi ilə xidmətin ərazisini, vaxtını və yekun qiymətini razılaşdırın.')
        crumbs += [('Xidmətlər', '/elanlar/')]
        if category.ust_kategori:
            crumbs.append((category.ust_kategori.ad, f'/xidmet/{category.ust_kategori.slug}/'))
        crumbs.append((category.ad, f'/xidmet/{category.slug}/'))
        if location:
            count = context.get('local_listing_count', 0)
            title = f'{category.ad} — {location["ad"]} üzrə elanlar | {BRAND}'
            description = (f'{location["tam_ad"]} üzrə {category.ad.lower()} axtarışı. '
                           f'Ərazisini {location["ad"]} göstərən {count} aktiv elan; digər ərazilərin təklifləri də göstərilir. Gəlişi elan sahibi ilə razılaşdırın.')
            crumbs.append((location['ad'], f'/xidmet/{category.slug}/{location["slug"]}/'))
        page_type = 'CollectionPage'
        faq = service_faq(context)
        extra.append({'@type': 'FAQPage', '@id': absolute_url(canonical_path) + '#faq',
                      'mainEntity': [{'@type': 'Question', 'name': question,
                                      'acceptedAnswer': {'@type': 'Answer', 'text': answer}}
                                     for question, answer in faq]})
    elif ad:
        title = f'{ad.bashliq} — {ad.sheher} | {BRAND}'
        description = f'{ad.bashliq} — {ad.sheher}. ' + plain(ad.acaqlama, 130)
        crumbs += [('Elanlar', '/elanlar/')]
        if ad.kategori:
            crumbs.append((ad.kategori.ad, f'/xidmet/{ad.kategori.slug}/'))
        crumbs.append((ad.bashliq, ad.get_absolute_url()))
        if ad.primary_photo:
            image, image_default = absolute_url(ad.primary_photo.shekil.url), False
    elif article:
        title = article.seo_title or f'{article.bashliq} — səbəblər və həll yolları | {BRAND}'
        description = article.seo_description or context.get('article_summary') or plain(article.metn, 160)
        crumbs += [('Təmir bələdçiləri', '/problemler/'), (article.bashliq, article.get_absolute_url())]
    elif view != 'index':
        crumbs.append((title.split('|')[0].strip(), canonical_path.split('?')[0]))

    if view in ('index', 'elan_siyahi', 'problemler_siyahi'):
        page_type = 'CollectionPage'
    if view == 'elan_siyahi' and context.get('axtaris'):
        title = f'{plain(context["axtaris"], 70)} — axtarış nəticələri | {BRAND}'
    if page_number > 1 and view in ('index', 'elan_siyahi', 'problemler_siyahi', 'xidmet_detail'):
        title += f' — Səhifə {page_number}'
        description = plain(description, 135) + f' Səhifə {page_number}.'
    canonical = absolute_url(canonical_path)
    title, description = plain(title), plain(description, 180)
    webpage = {'@type': page_type, '@id': canonical + '#webpage', 'url': canonical,
               'name': title, 'description': description, 'inLanguage': 'az-AZ',
               'isPartOf': {'@id': WEBSITE_ID}, 'publisher': {'@id': ORGANIZATION_ID}}
    page = context.get('problemler') if view == 'problemler_siyahi' else context.get('elanlar')
    if page_type == 'CollectionPage':
        items = _item_list(page)
        if items is not None:
            webpage['mainEntity'] = items
    if location:
        webpage['about'] = {'@type': 'AdministrativeArea', 'name': location['tam_ad'],
                            'containedInPlace': {'@type': 'Country', 'name': 'Azərbaycan'}}
    if len(crumbs) > 1:
        breadcrumb_id = canonical + '#breadcrumb'
        webpage['breadcrumb'] = {'@id': breadcrumb_id}
        extra.append({'@type': 'BreadcrumbList', '@id': breadcrumb_id, 'itemListElement': [
            {'@type': 'ListItem', 'position': index, 'name': plain(label), 'item': absolute_url(path)}
            for index, (label, path) in enumerate(crumbs, start=1)]})
    if ad and not noindex:
        service_id = canonical + '#service'
        service = {'@type': 'Service', '@id': service_id, 'url': canonical,
                   'name': plain(ad.bashliq), 'description': plain(ad.acaqlama, 500),
                   'image': image, 'broker': {'@id': ORGANIZATION_ID},
                   'areaServed': {'@type': 'Place', 'name': ad.sheher}}
        profile = getattr(ad.istifadeci, 'profil', None)
        provider_name = ' '.join(filter(None, [getattr(profile, 'ad', ''), getattr(profile, 'soyad', '')]))
        if provider_name:
            service['provider'] = {'@type': 'Person', 'name': provider_name,
                                   'url': SITE_URL + f'/istifadeci/{ad.istifadeci_id}/'}
            if ad.phone_e164:
                service['provider']['telephone'] = ad.phone_e164
        if ad.kategori:
            service['serviceType'] = ad.kategori.ad
        if ad.qiymet:
            service['offers'] = {'@type': 'Offer', 'price': format(ad.qiymet, '.2f'),
                                 'priceCurrency': 'AZN', 'url': canonical}
        webpage['mainEntity'] = {'@id': service_id}
        webpage.update(datePublished=ad.yaradildi.isoformat(), dateModified=ad.yenilendi.isoformat())
        extra.append(service)
    if article and not noindex:
        article_id = canonical + '#article'
        webpage['mainEntity'] = {'@id': article_id}
        extra.append({'@type': 'Article', '@id': article_id, 'url': canonical,
                      'headline': plain(article.bashliq), 'description': description,
                      'image': [image], 'inLanguage': 'az-AZ',
                      'datePublished': article.yaradildi.isoformat(), 'dateModified': article.yenilendi.isoformat(),
                      'author': {'@id': ORGANIZATION_ID}, 'publisher': {'@id': ORGANIZATION_ID},
                      'mainEntityOfPage': {'@id': webpage['@id']}})
    graph = {'@context': 'https://schema.org', '@graph': [
        _organization(), {'@type': 'WebSite', '@id': WEBSITE_ID, 'name': BRAND,
                          'url': SITE_URL + '/', 'inLanguage': 'az-AZ',
                          'publisher': {'@id': ORGANIZATION_ID}}, webpage, *extra]}
    robots = ('noindex, follow' if public else 'noindex, nofollow') if noindex else (
        'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1')
    if request is not None:
        request._seo_robots = robots
    return {'title': title, 'description': description, 'canonical': canonical,
            'robots': robots, 'image': image, 'default_image': image_default,
            'og_type': 'article' if article else 'website', 'schema': safe_json(graph) if public else '',
            'published': article.yaradildi if article else None, 'modified': article.yenilendi if article else None}
