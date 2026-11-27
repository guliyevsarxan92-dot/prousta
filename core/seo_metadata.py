"""One source for canonical URLs, share metadata and safely serialized JSON-LD."""
import json
import re
from html import unescape
from urllib.parse import urljoin, urlsplit

from django.template.defaultfilters import floatformat
from django.utils import timezone
from django.utils.html import strip_tags

from .seo import PUBLIC_VIEWS, SITE_URL, language_paths, seo_context
from .service_content import get_content, metadata_value
from .ru_content import (
    category_name_ru, city_ru, listing_areas_ru, listing_description_ru,
    listing_title_ru, location_ru, priority_page_ru, service_faq_ru,
)

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

STATIC_PAGES_RU = {
    'ru_index': ('Найти мастера в Баку — объявления об услугах и цены | Prousta.az',
                 'Сравните объявления мастеров и цены на услуги в Баку. Электрик, сантехник, мастер по комби, кондиционерам и ремонту — прямой звонок или WhatsApp без посредников.'),
    'ru_elan_siyahi': ('Все мастера и услуги в Баку — объявления и цены | Prousta.az',
                       'Каталог активных объявлений мастеров в Баку и Азербайджане. Сравните цены, районы выезда и свяжитесь с исполнителем напрямую.'),
    'ru_haqqimizda': ('О платформе Prousta.az — поиск мастеров и услуг в Баку',
                      'Узнайте, как работает платформа объявлений Prousta.az, как сравнивать предложения мастеров и договариваться напрямую без посредников.'),
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
    if context.get('is_ru'):
        category = context.get('aktiv_kategori') or context.get('topic_category')
        loc_info = context.get('lokasiya_melumat')
        return service_faq_ru(
            category,
            location_info=loc_info,
            min_price=context.get('min_qiymet'),
            priority_page=context.get('priority_service'),
        )
    if context.get('priority_service'):
        return context['priority_service']['faq']
    category = context['aktiv_kategori']
    location = context.get('lokasiya_melumat')
    area = location['ad'] + ' ərazisində' if location else 'Bakıda'
    sub_areas_note = (
        f' ({location["erazi"]})' if location and location.get('erazi')
        else ' (bütün rayon, qəsəbə, mikrorayon və metro əraziləri üzrə)'
    )
    minimum = context.get('min_qiymet')
    price = (f'Prousta.az-da {category.ad.lower()} üzrə elanlarda qiymətlər təxminən '
             f'{floatformat(minimum, "-2")} AZN-dən başlayır.' if minimum
             else 'Qiymət görüləcək işin həcminə və mürəkkəbliyinə görə dəyişir.')
    location_note = (' Burada digər ərazilərin elanları da göstərilir; elan qiyməti konkret ünvana xidmətin yekun qiymətini təsdiqləmir.' if location else '')
    questions = [
        (f'{area} {category.ad.lower()} üzrə xidmətin qiyməti nə qədərdir?',
         price + f' {area}{sub_areas_note} fəaliyyət göstərən bir neçə mütəxəssisin elanına baxaraq qiymətləri müqayisə edə və ən sərfəli variantı seçə bilərsiniz.' + location_note),
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


GOOGLE_MAPS_CID_URL = 'https://www.google.com/maps?cid=3860573795902979327'
GOOGLE_BUSINESS_PLACE_URL = 'https://www.google.com/maps/place//data=!4m3!3m2!1s0xac1ad4a9b3a0ffe5:0x35938328d49b7fcf!12e1'


def _organization():
    return {
        '@type': ['Organization', 'LocalBusiness'],
        '@id': ORGANIZATION_ID,
        'name': BRAND,
        'alternateName': 'PROusta',
        'url': SITE_URL + '/',
        'image': SITE_URL + '/static/img/icon_512.png',
        'logo': {
            '@type': 'ImageObject',
            'url': SITE_URL + '/static/img/icon_512.png',
        },
        'email': 'info@prousta.az',
        'telephone': '+994515888884',
        'priceRange': '$$',
        'hasMap': GOOGLE_MAPS_CID_URL,
        'address': {
            '@type': 'PostalAddress',
            'addressLocality': 'Bakı',
            'addressRegion': 'Bakı',
            'addressCountry': 'AZ',
        },
        'areaServed': [
            {'@type': 'City', 'name': 'Bakı'},
            {'@type': 'City', 'name': 'Sumqayıt'},
            {'@type': 'AdministrativeArea', 'name': 'Abşeron'},
            {'@type': 'Country', 'name': 'Azərbaycan'},
        ],
        'contactPoint': {
            '@type': 'ContactPoint',
            'telephone': '+994515888884',
            'contactType': 'customer support',
            'areaServed': 'AZ',
            'availableLanguage': ['az', 'ru'],
        },
        'sameAs': [
            GOOGLE_MAPS_CID_URL,
            GOOGLE_BUSINESS_PLACE_URL,
            'https://www.facebook.com/61568796886691',
            'https://www.instagram.com/prousta.az',
            'https://www.youtube.com/@prousta.servis.merkezi',
        ],
    }


def _item_list(page, model='listing'):
    if page is None or not hasattr(page, 'paginator'):
        return None
    items = []
    start = page.start_index()
    for position, item in enumerate(page, start=start):
        entry = {'@type': 'ListItem', 'position': position,
                 'url': absolute_url(item.get_absolute_url()), 'name': plain(item.bashliq)}
        desc_parts = []
        if getattr(item, 'sheher', ''):
            desc_parts.append(plain(item.sheher))
        if getattr(item, 'qiymet', None):
            desc_parts.append(f'{floatformat(item.qiymet, "-2")} AZN')
        if getattr(item, 'acaqlama', ''):
            desc_parts.append(plain(item.acaqlama, 110))
        if desc_parts:
            entry['description'] = ' · '.join(desc_parts)
        items.append(entry)
    return {'@type': 'ItemList', 'numberOfItems': page.paginator.count,
            'itemListElement': items}


def build_metadata(context):
    request = context.get('request')
    category = context.get('aktiv_kategori')
    ad = context.get('elan')
    article = context.get('problem')
    location = context.get('lokasiya_melumat')
    topic = context.get('priority_service') if context.get('topic_category') else None
    match = getattr(request, 'resolver_match', None)
    view = getattr(match, 'url_name', '')
    page_number = context.get('seo_page', 1)
    canonical_path = context.get('seo_canonical') or '/'
    noindex = bool(context.get('seo_noindex'))
    is_ru = bool(context.get('is_ru'))
    if request is not None:
        base = seo_context(request)
        canonical_path, page_number, noindex = base['seo_canonical'], base['seo_page'], base['seo_noindex']
        is_ru = is_ru or base['is_ru']
    prefix = '/ru' if is_ru else ''
    if topic:
        view = 'ru_xidmet_detail' if is_ru else 'xidmet_detail'
        topic_url = topic['url']
        if is_ru and not topic_url.startswith('/ru/'):
            topic_url = '/ru' + topic_url
        canonical_path = topic_url + (f'?page={page_number}' if page_number > 1 else '')
    elif category:
        view = 'ru_xidmet_detail' if is_ru else 'xidmet_detail'
        canonical_path = f'{prefix}/xidmet/{category.slug}/'
        if location:
            canonical_path += location['slug'] + '/'
        if page_number > 1:
            canonical_path += f'?page={page_number}'
        noindex |= not context.get('kat_indexable', False)
    elif ad:
        view = 'ru_elan_detail' if is_ru else 'elan_detail'
        canonical_path = f'{prefix}{ad.get_absolute_url()}'
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
    private_titles_ru = {'giris': 'Вход в аккаунт', 'qeydiyyat': 'Регистрация', 'profil': 'Мой профиль',
                         'profil_duzelis': 'Настройки профиля', 'mesajlar': 'Сообщения',
                         'sifre_unutdum': 'Восстановление пароля', 'elan_yarat': 'Подать объявление',
                         'odenis': 'Пополнение баланса', 'istifadeci_profil': 'Профиль мастера'}
    if is_ru:
        title, description = STATIC_PAGES_RU.get(view, (
            (private_titles_ru[view] + ' | ' + BRAND) if view in private_titles_ru else BRAND,
            'Платформа объявлений мастеров и услуг в Баку.'))
    else:
        title, description = STATIC_PAGES.get(view, (
            (private_titles[view] + ' | ' + BRAND) if view in private_titles else BRAND,
            'Usta və xidmət elanları platforması.'))
    image, image_default = DEFAULT_IMAGE, True
    crumbs = [('Главная', '/ru/')] if is_ru else [('Ana səhifə', '/')]
    page_type = 'WebPage'
    if view in ('haqqimizda', 'ru_haqqimizda'):
        page_type = 'AboutPage'
    extra = []
    if topic:
        title, description = topic['title'], topic['description']
        parent = context['topic_category']
        parent_label = category_name_ru(parent) if is_ru else parent.ad
        services_crumb = ('Услуги', '/ru/elanlar/') if is_ru else ('Xidmətlər', '/elanlar/')
        crumbs += [services_crumb, (parent_label, f'{prefix}/xidmet/{parent.slug}/'),
                   (topic['name'], topic['url'])]
        page_type = 'CollectionPage'
        extra.append({'@type': 'FAQPage', '@id': absolute_url(canonical_path) + '#faq',
                      'mainEntity': [{'@type': 'Question', 'name': question,
                                      'acceptedAnswer': {'@type': 'Answer', 'text': answer}}
                                     for question, answer in topic['faq']]})
    elif category:
        if is_ru:
            cat_ru = category_name_ru(category)
            prio = context.get('priority_service')
            if prio and not location:
                title, description = prio['title'], prio['description']
            else:
                title = f'{cat_ru} в Баку — мастера, объявления и цены | {BRAND}'
                description = (
                    f'{cat_ru} в Баку: сравните активные объявления мастеров, цены и примеры работ. '
                    'Свяжитесь с мастером напрямую по телефону или в WhatsApp без посредников.'
                )
            crumbs += [('Услуги', '/ru/elanlar/')]
            if category.ust_kategori:
                crumbs.append((category_name_ru(category.ust_kategori), f'/ru/xidmet/{category.ust_kategori.slug}/'))
            crumbs.append((cat_ru, f'/ru/xidmet/{category.slug}/'))
            if location:
                count = context.get('local_listing_count', 0)
                loc_ad = location['ad']
                locative = location.get('locative', f'в {loc_ad}')
                min_q = context.get('min_qiymet')
                price_hint_ru = f' (от {floatformat(min_q, "-2")} AZN)' if min_q else ''
                title = f'{cat_ru} {locative} (Баку) — мастера, объявления и цены | {BRAND}'
                inventory = f'Активных объявлений с выездом {locative}: {count}. ' if count else ''
                description = (
                    f'{cat_ru} {locative} ({location["tam_ad"]}){price_hint_ru}: {inventory}'
                    'Сравните предложения мастеров и цены, свяжитесь напрямую по телефону или в WhatsApp.'
                )
                crumbs.append((loc_ad, f'/ru/xidmet/{category.slug}/{location["slug"]}/'))
        else:
            min_q = context.get('min_qiymet')
            title = metadata_value(category, 'seo_title') or f'{category.ad} — ustalar və xidmət qiymətləri | {BRAND}'
            base_desc = metadata_value(category, 'seo_description') or (
                f'{category.ad} üzrə aktiv elanları, qiymətləri və iş nümunələrini müqayisə edin. '
                'Elan sahibi ilə xidmətin ərazisini, vaxtını və yekun qiymətini razılaşdırın.')
            if min_q and 'AZN' not in base_desc:
                description = f'{base_desc} Elanlarda qiymətlər {floatformat(min_q, "-2")} AZN-dən başlayır.'
            else:
                description = base_desc
            crumbs += [('Xidmətlər', '/elanlar/')]
            if category.ust_kategori:
                crumbs.append((category.ust_kategori.ad, f'/xidmet/{category.ust_kategori.slug}/'))
            crumbs.append((category.ad, f'/xidmet/{category.slug}/'))
            if location:
                count = context.get('local_listing_count', 0)
                price_hint = f'Elanlarda qiymətlər {floatformat(min_q, "-2")} AZN-dən başlayır. ' if min_q else ''
                title = f'{category.ad} {location["ad"]} — təmir, servis və qiymətlər | {BRAND}'
                inventory = (f'{location["ad"]} üzrə xidmət məlumatı olan {count} aktiv elan. '
                             if count else '')
                description = (f'{location["tam_ad"]} ({location["erazi"]}) üzrə {category.ad.lower()}: '
                               f'{inventory}{price_hint}Xidmət elanlarını müqayisə edin, usta ilə birbaşa zəng və ya WhatsApp ilə razılaşın.')
                crumbs.append((location['ad'], f'/xidmet/{category.slug}/{location["slug"]}/'))
        page_type = 'CollectionPage'
        faq = service_faq(context)
        extra.append({'@type': 'FAQPage', '@id': absolute_url(canonical_path) + '#faq',
                      'mainEntity': [{'@type': 'Question', 'name': question,
                                      'acceptedAnswer': {'@type': 'Answer', 'text': answer}}
                                     for question, answer in faq]})
    elif ad:
        price_str = f'{floatformat(ad.qiymet, "-2")} AZN' if ad.qiymet else ''
        profile = getattr(ad.istifadeci, 'profil', None)
        provider_name = ' '.join(filter(None, [getattr(profile, 'ad', ''), getattr(profile, 'soyad', '')]))
        if is_ru:
            ru_ad_title = listing_title_ru(ad)
            ru_ad_city = city_ru(ad.sheher or 'Баку')
            title_parts = [ru_ad_title]
            if ru_ad_city.lower() not in ru_ad_title.lower():
                title_parts.append(ru_ad_city)
            if price_str:
                title_parts.append(price_str)
            elif provider_name:
                title_parts.append(provider_name)
            title = ' — '.join(title_parts) + f' | {BRAND}'
            desc_prefix = f'{ru_ad_title} ({ru_ad_city})'
            if price_str:
                desc_prefix += f', цена: {price_str}'
            if provider_name:
                desc_prefix += f', мастер: {provider_name}'
            description = f'{desc_prefix}. ' + plain(listing_description_ru(ad), 130)
            crumbs += [('Объявления', '/ru/elanlar/')]
            if ad.kategori:
                crumbs.append((category_name_ru(ad.kategori), f'/ru/xidmet/{ad.kategori.slug}/'))
            crumbs.append((ru_ad_title, f'/ru{ad.get_absolute_url()}'))
        else:
            area_names = ad.erazi_adlari
            primary_area = area_names[0] if area_names else ''
            location_label = ad.sheher or 'Bakı'
            if primary_area and primary_area.lower() not in location_label.lower():
                location_label = f'{location_label}, {primary_area}'
            title_parts = [ad.bashliq, location_label]
            if price_str:
                title_parts.append(price_str)
            elif provider_name and provider_name.lower() not in ad.bashliq.lower():
                title_parts.append(provider_name)
            elif ad.nomre:
                title_parts.append(f'#{ad.nomre}')
            title = ' — '.join(title_parts) + f' | {BRAND}'
            desc_prefix = f'{ad.bashliq} ({location_label})'
            if price_str:
                desc_prefix += f', qiymət: {price_str}'
            if provider_name:
                desc_prefix += f', icraçı: {provider_name}'
            description = f'{desc_prefix}. ' + plain(ad.acaqlama, 130)
            crumbs += [('Elanlar', '/elanlar/')]
            if ad.kategori:
                crumbs.append((ad.kategori.ad, f'/xidmet/{ad.kategori.slug}/'))
            crumbs.append((ad.bashliq, ad.get_absolute_url()))
        if ad.primary_photo:
            image, image_default = absolute_url(ad.primary_photo.shekil.url), False
    elif article:
        title = article.seo_title or f'{article.bashliq} — səbəblər və həll yolları | {BRAND}'
        description = article.seo_description or context.get('article_summary') or plain(article.metn, 160)
        crumbs += [('Təmir bələdçiləri', '/problemler/')]
        if article.kategori:
            crumbs.append((article.kategori.ad, f'/xidmet/{article.kategori.slug}/'))
        crumbs.append((article.bashliq, article.get_absolute_url()))
        article_img = context.get('article_image')
        if article_img:
            image, image_default = absolute_url(article_img), False
    elif view not in ('index', 'ru_index'):
        crumbs.append((title.split('|')[0].strip(), canonical_path.split('?')[0]))

    if view in ('index', 'elan_siyahi', 'problemler_siyahi', 'ru_index', 'ru_elan_siyahi'):
        page_type = 'CollectionPage'
    if view in ('elan_siyahi', 'ru_elan_siyahi') and context.get('axtaris'):
        suffix = 'результаты поиска' if is_ru else 'axtarış nəticələri'
        title = f'{plain(context["axtaris"], 70)} — {suffix} | {BRAND}'
    if page_number > 1 and view in ('index', 'elan_siyahi', 'problemler_siyahi', 'xidmet_detail',
                                    'ru_index', 'ru_elan_siyahi', 'ru_xidmet_detail'):
        page_word = 'Страница' if is_ru else 'Səhifə'
        title += f' — {page_word} {page_number}'
        description = plain(description, 135) + f' {page_word} {page_number}.'
    canonical = absolute_url(canonical_path)
    title, description = plain(title), plain(description, 180)
    lang_tag = 'ru-RU' if is_ru else 'az-AZ'
    webpage = {'@type': page_type, '@id': canonical + '#webpage', 'url': canonical,
               'name': title, 'description': description, 'inLanguage': lang_tag,
               'isPartOf': {'@id': WEBSITE_ID}, 'publisher': {'@id': ORGANIZATION_ID}}
    page = context.get('problemler') if view == 'problemler_siyahi' else context.get('elanlar')
    if page_type == 'CollectionPage':
        items = _item_list(page)
        if items is not None:
            webpage['mainEntity'] = items
    if location:
        area_node = {'@type': 'AdministrativeArea', 'name': location['tam_ad'],
                     'containedInPlace': {'@type': 'Country', 'name': 'Azərbaycan'}}
        sub_places = location.get('qesebeler') or [p.strip() for p in location.get('erazi', '').split(',') if p.strip()]
        if sub_places:
            area_node['containsPlace'] = [{'@type': 'Place', 'name': place} for place in sub_places[:16]]
        webpage['about'] = area_node
    if len(crumbs) > 1:
        breadcrumb_id = canonical + '#breadcrumb'
        webpage['breadcrumb'] = {'@id': breadcrumb_id}
        extra.append({'@type': 'BreadcrumbList', '@id': breadcrumb_id, 'itemListElement': [
            {'@type': 'ListItem', 'position': index, 'name': plain(label), 'item': absolute_url(path)}
            for index, (label, path) in enumerate(crumbs, start=1)]})
    if ad and not noindex:
        service_id = canonical + '#service'
        areas = listing_areas_ru(ad) if is_ru else ad.erazi_melumatlari
        city_name = city_ru(ad.sheher) if is_ru else ad.sheher
        if areas:
            area_served = [{'@type': 'Place', 'name': city_name},
                           *[{'@type': 'AdministrativeArea', 'name': loc['tam_ad']} for loc in areas]]
        else:
            area_served = {'@type': 'Place', 'name': city_name}
        srv_name = plain(listing_title_ru(ad) if is_ru else ad.bashliq)
        srv_desc = plain(listing_description_ru(ad) if is_ru else ad.acaqlama, 500)
        service = {'@type': 'Service', '@id': service_id, 'url': canonical,
                   'name': srv_name, 'description': srv_desc,
                   'image': image, 'broker': {'@id': ORGANIZATION_ID},
                   'areaServed': area_served}
        profile = getattr(ad.istifadeci, 'profil', None)
        provider_name = ' '.join(filter(None, [getattr(profile, 'ad', ''), getattr(profile, 'soyad', '')]))
        if provider_name:
            service['provider'] = {'@type': 'Person', 'name': provider_name,
                                   'url': SITE_URL + f'/istifadeci/{ad.istifadeci_id}/'}
            if ad.phone_e164:
                service['provider']['telephone'] = ad.phone_e164
        if ad.kategori:
            service['serviceType'] = category_name_ru(ad.kategori) if is_ru else ad.kategori.ad
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
    provider = context.get('service_provider')
    guide = context.get('priority_service')
    if provider and guide and not noindex:
        offer_service = {'@type': 'Service', '@id': canonical + '#provider-service',
                         'name': guide['name'], 'url': canonical,
                         'description': guide['summary'],
                         'broker': {'@id': ORGANIZATION_ID},
                         'provider': {'@type': 'Person', 'name': provider['name'],
                                      'url': absolute_url(provider['profile_url']),
                                      'telephone': provider['phone']},
                         'areaServed': {'@type': 'City', 'name': 'Bakı'}}
        price = provider.get('price')
        if price:
            offer = {'@type': 'Offer', 'url': canonical, 'priceCurrency': 'AZN',
                     'description': price['note']}
            if price['starting']:
                offer['priceSpecification'] = {'@type': 'PriceSpecification',
                                               'minPrice': price['amount'], 'priceCurrency': 'AZN'}
            else:
                offer['price'] = price['amount']
            offer_service['offers'] = offer
        extra.append(offer_service)
    if view in ('index', 'ru_index') and not noindex and page_number == 1:
        home_faq = [
            ('Как найти мастера на Prousta.az?',
             'Выберите нужную категорию услуг или введите запрос в поиск (например: мастер комби, сантехник, электрик, прочистка канализации). Сравните цены в объявлениях и свяжитесь с мастером напрямую по телефону или через WhatsApp.'),
            ('Нужно ли платить комиссию за поиск мастера?',
             'Нет! Для заказчиков платформа Prousta.az полностью бесплатна. Вы общаетесь и рассчитываетесь непосредственно с исполнителем без посредников.'),
            ('Какие услуги представлены на сайте?',
             'Ремонт и промывка комби, установка и сервис кондиционеров, поиск скрытой утечки воды тепловизором, прочистка канализации, услуги сантехника, электрика, чистка вентиляции и зонтов, ремонт бытовой техники и квартир.'),
        ] if is_ru else [
            ('Prousta.az-da usta necə tapılır?',
             'Saytda axtardığınız xidmət kateqoriyasını seçin və ya axtarış bölməsinə ehtiyacınız olan xidməti yazın (məs: kombi ustası, santexnik, elektrik). Elanlarda qiymətlərə və usta məlumatlarına baxaraq birbaşa zəng və ya WhatsApp ilə əlaqə saxlayın.'),
            ('Usta ilə əlaqə saxlamaq üçün ödəniş tələb olunurmu?',
             'Xeyr! Prousta.az müştərilər üçün tamamilə pulsuzdur. Platformada heç bir vasitəçi komissiyası yoxdur, usta ilə birbaşa əlaqə saxlayırsınız.'),
            ('Prousta.az-da hansı xidmətlər mövcuddur?',
             'Kombi və kondisioner servisi, santexnika, elektrik, mebel yığılması və təmiri, məişət texnikası təmiri (soyuducu, paltaryuyan), ev təmiri və tikinti daxil olmaqla 100-dən çox kateqoriyada usta elanları mövcuddur.'),
            ('Usta kimi necə elan yerləşdirmək olar?',
             'Saytda pulsuz qeydiyyatdan keçərək «Elan yerləşdir» düyməsinə klikləyin. Göstərdiyiniz xidməti, qiyməti, əlaqə nömrənizi və gördüyünüz işlərin şəkillərini əlavə edərək minlərlə potensial müştəriyə çatın.'),
        ]
        extra.append({'@type': 'FAQPage', '@id': canonical + '#faq',
                      'mainEntity': [{'@type': 'Question', 'name': q,
                                      'acceptedAnswer': {'@type': 'Answer', 'text': a}}
                                     for q, a in home_faq]})
    website_node = {
        '@type': 'WebSite', '@id': WEBSITE_ID, 'name': BRAND,
        'url': SITE_URL + '/', 'inLanguage': lang_tag,
        'publisher': {'@id': ORGANIZATION_ID},
        'potentialAction': {
            '@type': 'SearchAction',
            'target': {
                '@type': 'EntryPoint',
                'urlTemplate': SITE_URL + ('/ru/elanlar/?q={search_term_string}' if is_ru else '/elanlar/?q={search_term_string}'),
            },
            'query-input': 'required name=search_term_string',
        },
    }
    graph = {'@context': 'https://schema.org', '@graph': [
        _organization(), website_node, webpage, *extra]}
    robots = ('noindex, follow' if public else 'noindex, nofollow') if noindex else (
        'index, follow, max-image-preview:large, max-snippet:-1, max-video-preview:-1')
    if request is not None:
        request._seo_robots = robots
    base_path, _, query_part = canonical_path.partition('?')
    _, az_base, ru_base, has_ru = language_paths(base_path)
    qs = f'?{query_part}' if query_part else ''
    alternate_az = absolute_url(az_base + qs)
    alternate_ru = absolute_url(ru_base + qs) if has_ru else ''
    return {'title': title, 'description': description, 'canonical': canonical,
            'alternate_az': alternate_az, 'alternate_ru': alternate_ru, 'x_default': alternate_az,
            'og_locale': 'ru_RU' if is_ru else 'az_AZ',
            'robots': robots, 'image': image, 'default_image': image_default,
            'og_type': 'article' if article else 'website', 'schema': safe_json(graph) if public else '',
            'published': article.yaradildi if article else None, 'modified': article.yenilendi if article else None}
