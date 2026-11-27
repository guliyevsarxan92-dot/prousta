"""Distinct service guides; provider offers and coverage declared by the account owner."""
import json
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlencode

from django.db.models import CharField, F, Q, Value
from django.db.models.functions import Coalesce
from django.http import Http404
from django.shortcuts import render

PROVIDER_USERNAME = 'superadmin'
PROVIDER_PHONE = '+994515888884'
# Owner confirmed on 2026-11-12. Surrounding Absheron/Sumgayit areas included for confirmed services.
BAKU_AREAS = frozenset({'yasamal', 'nerimanov', 'nesimi', 'xetai', 'bineqedi',
                        'nizami', 'sebail', 'sabuncu', 'suraxani', 'xezer', 'qaradag', 'pirallahi',
                        'xirdalan', 'masazir', 'sumqayit', 'saray', 'mehdiabad'})
PROVIDER_CATEGORIES = frozenset({'kombi-ustasi', 'su-sizma', 'kanalizasiya-ustasi',
                                 'santexnik', 'havalandirma-ustasi', 'ariston-ustasi',
                                 'kondisioner-ustasi', 'soyuducu-ustasi',
                                 'paltaryuyan-ustasi', 'qabyuyan-ustasi'})
PRICES = {
    'su-sizma': {'amount': '80.00', 'label': '80 AZN', 'starting': False,
                 'note': 'Su sızmasının təyini üçün təklifdir. Təmir və səthin bərpasının daxil olub-olmadığını əvvəl dəqiqləşdirin.'},
    'kanalizasiya-ustasi': {'amount': '80.00', 'label': '80 AZN', 'starting': False,
                          'note': 'Kanalizasiya açılması üçün təklifdir. Xəttin növünü və əlavə işləri əvvəl təsdiqləyin.'},
    'kombi-yuyulmasi': {'amount': '30.00', 'label': '30 AZN-dən', 'starting': True,
                       'note': 'Başlanğıc qiymətdir. Radiator sayı və yuyulacaq hissələrə görə yekun məbləğ dəqiqləşdirilir.'},
}


def provider_coverage_q():
    return Q(istifadeci__username=PROVIDER_USERNAME, istifadeci__is_active=True,
             kategori__slug__in=PROVIDER_CATEGORIES)


def declared_areas(row):
    if (row['istifadeci__username'] == PROVIDER_USERNAME and row['istifadeci__is_active']
            and row['kategori__slug'] in PROVIDER_CATEGORIES):
        return BAKU_AREAS
    return frozenset()


@lru_cache(maxsize=1)
def pages():
    data = json.loads(Path(__file__).with_name('data.json').read_text(encoding='utf-8'))
    for slug, page in data.items():
        page.update(slug=slug, url=f'/xidmet/{slug}/')
    return data


def topics():
    return [page for page in pages().values() if page['category'] != page['slug']]


def guide_for_category(category):
    from core.service_content import get_content
    return pages().get(category.slug) if get_content(category) else None


def page_context(page, user=None, is_ru=False):
    from django.contrib.auth.models import User
    from core.listings import visible_listings
    from core.models import Kategori
    from core.service_content import sources
    from core.ru_content import priority_page_ru
    from django.contrib.auth.models import AnonymousUser
    active_page = priority_page_ru(page) if is_ru else page
    owner = User.objects.filter(username=PROVIDER_USERNAME, is_active=True).select_related('profil').first()
    provider = None
    # A guide remains useful without inventory; a provider offer needs a live listing.
    ads = visible_listings(user or AnonymousUser()).filter(
        istifadeci__username=PROVIDER_USERNAME, istifadeci__is_active=True,
        kategori__slug=page['category']).order_by('pk')
    ad = ads.first() if owner else None
    # These related services were also explicitly declared by the owner. Reuse
    # their real public account, without manufacturing a category listing.
    fallback_categories = {'santexnik': ('su-sizma', 'kanalizasiya-ustasi'),
                           'ariston-ustasi': ('kombi-ustasi',)}
    if owner and not ad and page['category'] in fallback_categories:
        ad = visible_listings(user or AnonymousUser()).filter(
            istifadeci=owner, kategori__slug__in=fallback_categories[page['category']]).order_by('pk').first()
    if ad:
        profile = getattr(owner, 'profil', None)
        name = ' '.join(filter(None, [getattr(profile, 'ad', ''), getattr(profile, 'soyad', '')]))
        if is_ru:
            message = f'Здравствуйте, хочу уточнить объём работ, стоимость и гарантию по услуге «{active_page["name"]}».'
        else:
            message = f'Salam, {page["name"]} üçün iş həcmini, qiyməti və zəmanət şərtlərini dəqiqləşdirmək istəyirəm.'
        price = PRICES.get(page['slug'])
        if price and is_ru:
            price = dict(price)
            if active_page.get('price_label'):
                price['label'] = active_page['price_label']
            if active_page.get('price_note'):
                price['note'] = active_page['price_note']
        provider = {'name': name or owner.get_full_name() or owner.username,
                    'profile_url': f'/istifadeci/{owner.pk}/', 'listing_url': ad.get_absolute_url(),
                    'phone': PROVIDER_PHONE, 'price': price,
                    'whatsapp': 'https://wa.me/' + PROVIDER_PHONE[1:] + '?' + urlencode({'text': message})}
    registry = pages()
    valid_categories = set(Kategori.objects.filter(slug__in=page['related']).values_list('slug', flat=True))
    related = [
        (priority_page_ru(registry[slug]) if is_ru else registry[slug])
        for slug in page['related']
        if slug in registry and (registry[slug]['category'] != slug or slug in valid_categories)
    ]
    return {'priority_service': active_page, 'service_provider': provider,
            'service_sources': [sources()[key] for key in page['sources']],
            'service_related': related}


def matching_listings(queryset, page):
    from core.search import _normalized_expression
    queryset = queryset.filter(kategori__slug=page['category'])
    if page.get('terms'):
        queryset = queryset.alias(
            _topic_title=_normalized_expression(Coalesce(F('bashliq'), Value(''), output_field=CharField())),
            _topic_text=_normalized_expression(Coalesce(F('acaqlama'), Value(''), output_field=CharField())))
        evidence = Q()
        for term in page['terms']:
            evidence |= Q(_topic_title__contains=term) | Q(_topic_text__contains=term)
        queryset = queryset.filter(evidence)
    return queryset


def topic_response(request, page, is_ru=False):
    from core.listings import visible_listings
    from core.models import Kategori
    from core.rotation import apply_fair_rotation
    from core.views import get_or_create_listing_seed, strict_page
    from django.core.paginator import Paginator
    category = Kategori.objects.filter(slug=page['category']).first()
    if category is None:
        raise Http404('Xidmət bölməsi tapılmadı.')
    seed = get_or_create_listing_seed(request, session_key='topic_' + page['slug'])
    listings = matching_listings(visible_listings(request.user), page).select_related(
        'kategori', 'istifadeci__profil').prefetch_related('shekillar')
    result = strict_page(Paginator(apply_fair_rotation(listings, seed), 12), request.GET.get('page', 1))
    template_name = 'ru/service_topic.html' if is_ru else 'service_topic.html'
    return render(request, template_name, {
        **page_context(page, request.user, is_ru=is_ru),
        'is_ru': is_ru,
        'topic_category': category,
        'elanlar': result,
        'page_range': list(result.paginator.get_elided_page_range(result.number)),
        'elan_seed': seed,
    })
