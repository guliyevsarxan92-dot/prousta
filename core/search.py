"""Shared service search: location affects order, never service availability."""
import re

from django.db.models import Case, CharField, F, IntegerField, Q, Value, When
from django.db.models.functions import Coalesce, Lower, Replace
from django.utils import timezone

from .locations import LOKASIYALAR
from .models import _AZ_MAP


def normalize(text):
    return text.translate(_AZ_MAP).lower()


def _normalized_expression(expression):
    # Translate before Lower so SQLite and PostgreSQL handle AZ capitals alike.
    for source, target in _AZ_MAP.items():
        expression = Replace(expression, Value(chr(source)), Value(target))
    return Lower(expression)


def search_listings(queryset, query='', location=''):
    query = query[:200]
    location = location[:100]
    queryset = queryset.filter(Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=timezone.now()))
    aliases = {normalize(city) for city in (
        'Bakı', 'Abşeron', 'Gəncə', 'Mingəçevir', 'Lənkəran', 'Şəki', 'Quba',
        'Naxçıvan', 'Şirvan', 'Yevlax', 'Şamaxı', 'Qəbələ', 'Zaqatala', 'Bərdə',
        'Sabirabad', 'Salyan', 'Masallı', 'Cəlilabad', 'Göyçay', 'Xaçmaz',
        'Qusar', 'Tovuz', 'Qazax', 'Ağcabədi', 'Şuşa', 'Xankəndi',
    )}
    for item in LOKASIYALAR.values():
        aliases.update(normalize(word) for word in [item['ad'], *item['keywords']])
    # Match phrases first; support "Yasamalda", "Bakıda", etc.
    pattern = r'\b(' + '|'.join(re.escape(word) for word in sorted(aliases, key=len, reverse=True)) + r')(?:da|de|dan|den|nda|nde)?\b'
    places = []

    def remove_place(match):
        places.append(match.group(1))
        return ' '

    service_query = re.sub(pattern, remove_place, normalize(query))
    if places:
        service_query = re.sub(
            r'\b(?:rayon(?:u|unda)?|seher(?:i|inde)?|qesebe(?:si|sinde)?|metro(?:su|sunda)?)\b',
            ' ', service_query,
        )
    tokens = re.findall(r'\w+', service_query)[:8]
    if tokens:
        fields = ('bashliq', 'acaqlama', 'nomre', 'kategori__ad', 'kategori__ust_kategori__ad')
        expressions = {
            f'_search_{i}': _normalized_expression(Coalesce(F(field), Value(''), output_field=CharField()))
            for i, field in enumerate(fields)
        }
        queryset = queryset.alias(**expressions)
        for token in tokens:
            matches = Q()
            for alias in expressions:
                matches |= Q(**{f'{alias}__contains': token})
            queryset = queryset.filter(matches)

    preferred = normalize(location).strip()
    if preferred and preferred != 'butun azerbaycan':
        item = LOKASIYALAR.get(preferred)
        places = [normalize(word) for word in [item['ad'], *item['keywords']]] if item else [preferred]
    if places:
        queryset = queryset.alias(_search_city=_normalized_expression(F('sheher')))
        local = Q()
        for place in set(places):
            local |= Q(_search_city__contains=place)
        queryset = queryset.annotate(is_local=Case(
            When(local, then=Value(1)), default=Value(0), output_field=IntegerField(),
        ))
    return queryset
