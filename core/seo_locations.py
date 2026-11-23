"""Local landing pages use published location evidence, never inferred coverage."""
import re
from functools import lru_cache

from django.db.models import Count, F, Q
from django.utils import timezone

from .locations import LOKASIYALAR
from .search import _normalized_expression, normalize


@lru_cache(maxsize=32)
def location_pattern(slug):
    location = LOKASIYALAR[slug]
    # Short/generic aliases such as "bine" and "mkr" can refer to other districts.
    aliases = {normalize(location['ad']), normalize(slug)}
    aliases.update(normalize(word) for word in location['keywords']
                   if len(normalize(word)) >= 6 and normalize(word) not in {'abseron'})
    return r'(^|[^a-z0-9])(' + '|'.join(re.escape(word) for word in sorted(aliases)) + r')([^a-z0-9]|$)'


def in_location(queryset, slug):
    from .service_pages import BAKU_AREAS, provider_coverage_q
    covered = provider_coverage_q() if slug in BAKU_AREAS else Q(pk__in=[])
    return queryset.alias(_seo_city=_normalized_expression(F('sheher'))).filter(
        Q(_seo_city__regex=location_pattern(slug)) | covered)


def matching_locations(city):
    value = normalize(city)
    return [slug for slug in LOKASIYALAR if re.search(location_pattern(slug), value)]


def active_public_listings():
    from .models import Elan
    return Elan.objects.filter(status='aktiv').filter(
        Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=timezone.now()))


def location_counts(queryset):
    from .service_pages import declared_areas
    counts = {}
    for row in queryset.order_by().values('sheher', 'kategori__slug', 'istifadeci__username',
                                         'istifadeci__is_active').annotate(total=Count('pk')):
        for slug in set(matching_locations(row['sheher'])) | declared_areas(row):
            counts[slug] = counts.get(slug, 0) + row['total']
    return counts


def indexable_location_pairs():
    """One grouped inventory query; no category × all-locations Cartesian product."""
    from .models import Kategori
    from .service_pages import declared_areas
    categories = {row['pk']: row for row in Kategori.objects.values('pk', 'slug', 'ust_kategori_id')}
    pairs = set()
    for row in active_public_listings().order_by().values('kategori_id', 'sheher', 'kategori__slug',
            'istifadeci__username', 'istifadeci__is_active').annotate(total=Count('pk')):
        category = categories.get(row['kategori_id'])
        if not category:
            continue
        slugs = set(matching_locations(row['sheher'])) | declared_areas(row)
        for item in (category, categories.get(category['ust_kategori_id'])):
            if item:
                pairs.update((item['slug'], slug) for slug in slugs)
    return sorted(pairs)
