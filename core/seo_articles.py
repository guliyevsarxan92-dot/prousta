"""Derive readable summaries and section links from the article's real text."""
import math
import re
from html import escape

from .models import slug_az
from .seo_metadata import plain

ARTICLE_CATEGORY_IMAGES = {
    'kombi-ustasi': '/media/elanlar/kombi_1.jpg',
    'kondisioner-ustasi': '/media/elanlar/kondisioner_1.jpg',
    'havalandirma-ustasi': '/media/elanlar/havalandirma_1.jpg',
    'paltaryuyan-ustasi': '/media/elanlar/paltaryuyan_1.jpg',
    'qabyuyan-ustasi': '/media/elanlar/qabyuyan_1.jpg',
    'soyuducu-ustasi': '/media/elanlar/soyuducu_1.jpg',
    'su-sizma': '/media/elanlar/su_sizma_1.jpg',
    'kanalizasiya-ustasi': '/media/elanlar/kanalizasiya_1.jpg',
}


def article_service_links(article):
    """Məqalə ilə birbaşa əlaqəli əsas xidmət və alt-xidmət (bələdçi) linkləri."""
    category = getattr(article, 'kategori', None)
    if not category:
        return []
    from .search import normalize
    from .service_pages import topics

    links = [{'name': category.ad, 'url': f'/xidmet/{category.slug}/', 'is_primary': True}]
    haystack = normalize(f'{article.bashliq or ""} {plain(article.metn)}')
    matched, others = [], []
    for topic in topics():
        if topic['category'] != category.slug:
            continue
        entry = {'name': topic['name'], 'url': topic['url'], 'is_primary': False}
        if any(term in haystack for term in topic.get('terms', ())):
            matched.append(entry)
        else:
            others.append(entry)
    links.extend((matched + others)[:3])
    return links


def article_location_links(article):
    """Məqalənin aid olduğu kateqoriya üzrə indekslənən (sübutlu) lokal rayon/şəhər səhifələri."""
    category = getattr(article, 'kategori', None)
    if not category:
        return []
    from .locations import LOKASIYALAR, POPULAR_LOKASIYALAR
    from .seo_locations import active_public_listings, location_counts
    from django.db.models import Q

    ads = active_public_listings().filter(
        Q(kategori=category) | Q(kategori__ust_kategori=category)
    )
    counts = location_counts(ads)
    if not counts:
        return []

    # Yüksək axtarış tələbli əraziləri önə çəkirik (Yasamal, Xırdalan, Sumqayıt, Masazır, Nərimanov və s.)
    priority_order = ['yasamal', 'xirdalan', 'sumqayit', 'masazir', *[s for s in POPULAR_LOKASIYALAR if s not in ('yasamal', 'xirdalan', 'sumqayit', 'masazir')]]
    ordered_slugs = [s for s in priority_order if counts.get(s, 0) > 0]
    ordered_slugs.extend(s for s in counts if s not in ordered_slugs and counts.get(s, 0) > 0)

    links = []
    for slug in ordered_slugs[:10]:
        loc = LOKASIYALAR.get(slug)
        if loc:
            links.append({
                'name': f'{category.ad} {loc["ad"]}',
                'short_name': loc['ad'],
                'url': f'/xidmet/{category.slug}/{slug}/',
                'count': counts[slug],
            })
    return links


def article_image_url(article, listings=()):
    """Məqalə üçün unikal şəkil: məqalə daxili <img>, aktiv elan şəkli və ya kateqoriya şəkli."""
    img_match = re.search(r'<img\b[^>]*\bsrc\s*=\s*["\']([^"\']+)["\']', getattr(article, 'metn', '') or '', re.I)
    if img_match:
        return img_match.group(1).strip()
    for ad in listings or ():
        photo = getattr(ad, 'primary_photo', None)
        if photo and getattr(photo, 'shekil', None):
            try:
                return photo.shekil.url
            except Exception:
                pass
    category = getattr(article, 'kategori', None)
    if category and category.slug in ARTICLE_CATEGORY_IMAGES:
        return ARTICLE_CATEGORY_IMAGES[category.slug]
    return ''


def article_context(article, listings=()):
    headings = []
    used = set()

    def section(match):
        level, attributes, body = match.groups()
        label = plain(body)
        existing = re.search(r'(?:^|\s)id\s*=\s*[\"\']([^\"\']+)[\"\']', attributes, re.I)
        anchor = existing.group(1) if existing else 'bolme-' + (slug_az(label, 70) or 'metn')
        candidate, number = anchor, 2
        while candidate in used:
            candidate = f'{anchor}-{number}'
            number += 1
        used.add(candidate)
        if existing:
            attributes = attributes[:existing.start()] + attributes[existing.end():]
        if label and len(headings) < 30:
            headings.append({'label': label, 'anchor': candidate, 'level': level})
        return f'<h{level}{attributes} id="{escape(candidate, quote=True)}">{body}</h{level}>'

    body = re.sub(r'<h([23])\b([^>]*)>(.*?)</h\1\s*>', section, article.metn, flags=re.I | re.S)
    paragraph = re.search(r'<p\b[^>]*>(.*?)</p\s*>', article.metn, flags=re.I | re.S)
    summary = plain(paragraph.group(1) if paragraph else article.metn, 280)
    return {'article_body': body, 'article_toc': headings,
            'article_summary': summary,
            'article_service_links': article_service_links(article),
            'article_location_links': article_location_links(article),
            'article_image': article_image_url(article, listings),
            'article_read_minutes': max(1, math.ceil(len(plain(article.metn).split()) / 200))}
