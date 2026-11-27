"""Normalize xidmet_erazileri to canonical slugs, populate from explicit location mentions, and extend expired active listings."""
from datetime import timedelta
from django.db import migrations
from django.utils import timezone


def populate_listing_areas_and_extend_expiry(apps, schema_editor):
    from core.locations import LOKASIYALAR
    from core.seo_locations import matching_locations, selected_areas

    Elan = apps.get_model('core', 'Elan')
    alias = schema_editor.connection.alias
    now = timezone.now()
    future_expiry = now + timedelta(days=90)

    extra_map = {
        'türkan': 'xezer', 'turkan': 'xezer', 'zirə': 'xezer', 'zire': 'xezer',
        'bilgəh': 'sabuncu', 'bilgeh': 'sabuncu', 'pirşağı': 'sabuncu', 'pirsagi': 'sabuncu',
        'ramanı': 'sabuncu', 'ramani': 'sabuncu', 'kürdəxanı': 'sabuncu', 'kurdexani': 'sabuncu',
        'məhəmmədi': 'suraxani', 'mehemmedi': 'suraxani', 'zığ': 'suraxani', 'zig': 'suraxani',
        'günəşli': 'suraxani', 'gunesli': 'suraxani',
        'dərnəgül': 'bineqedi', 'dernegul': 'bineqedi', 'avtovağzal': 'bineqedi',
        'xocasən': 'bineqedi', 'xocasen': 'bineqedi',
        'bibiheybət': 'sebail', 'bibiheybet': 'sebail',
        'müşfiqabad': 'qaradag', 'musfiqabad': 'qaradag',
        'hökməli': 'xirdalan', 'hokmeli': 'xirdalan', 'novxanı': 'sumqayit', 'novxani': 'sumqayit',
        'fatmayı': 'mehdiabad', 'fatmayi': 'mehdiabad', 'binə ərazisində': 'xezer',
    }

    for ad in Elan.objects.using(alias).all().iterator():
        updates = {}
        existing_slugs = set(selected_areas(ad.xidmet_erazileri))
        first_line = (ad.acaqlama or '').splitlines()[0] if ad.acaqlama else ''
        haystack = f"{ad.sheher or ''} {ad.bashliq or ''} {first_line}"
        found = set(matching_locations(haystack))
        low_line = first_line.lower()
        for term, slug in extra_map.items():
            if term in low_line and slug in LOKASIYALAR:
                found.add(slug)
        combined = [slug for slug in LOKASIYALAR if slug in (existing_slugs | found)]
        canonical_str = ','.join(combined)
        if canonical_str and canonical_str != (ad.xidmet_erazileri or ''):
            updates['xidmet_erazileri'] = canonical_str

        # Reactivate listings whose 30-day window expired
        if ad.bitis_tarixi and ad.bitis_tarixi <= now and ad.status in ('aktiv', 'muddeti_bitmis'):
            updates['status'] = 'aktiv'
            updates['bitis_tarixi'] = future_expiry

        if updates:
            Elan.objects.using(alias).filter(pk=ad.pk).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0034_elan_xidmet_erazileri'),
    ]

    operations = [
        migrations.RunPython(populate_listing_areas_and_extend_expiry, migrations.RunPython.noop),
    ]
