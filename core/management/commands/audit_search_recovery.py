"""Inspect historical search URLs without reactivating or modifying listings."""
import csv
from urllib.parse import urlsplit

from django.core.management.base import BaseCommand
from core.models import Elan, Kategori
from core.seo_locations import active_public_listings, in_location
from core.locations import LOKASIYALAR


class Command(BaseCommand):
    help = 'Read-only audit of historical search URLs. Never reactivates an expired, rejected or deleted listing.'

    def add_arguments(self, parser):
        parser.add_argument('--source', required=True, help='CSV file with a URL column')
        parser.add_argument('--output', help='Output CSV path; defaults to stdout')

    def handle(self, *args, **options):
        with open(options['source'], encoding='utf-8-sig', newline='') as source:
            rows = list(csv.DictReader(source))
        results = []
        for row in rows:
            url = row.get('URL', '')
            parsed = urlsplit(url)
            if parsed.netloc not in ('prousta.az', 'www.prousta.az'):
                results.append([url, 'foreign_url', '', 'Only prousta.az URLs are inspected'])
                continue
            parts = parsed.path.strip('/').split('/')
            state, count, action = 'manual_review', '', 'Inspect this URL in Search Console'
            if len(parts) == 2 and parts[0] == 'elan':
                number = parts[1].split('-', 1)[0]
                ad = Elan.objects.filter(pk=int(number)).first() if number.isdigit() else None
                if not ad:
                    state, action = 'missing_listing', 'Record is absent; do not invent a replacement or redirect to the homepage'
                elif active_public_listings().filter(pk=ad.pk).exists():
                    state = 'active_listing'
                    action = 'Current canonical: ' + ad.get_absolute_url()
                else:
                    state, action = 'not_public_listing', f'Status={ad.status}; investigate expiry/moderation and owner before changing it'
            elif len(parts) == 3 and parts[0] == 'xidmet' and parts[2] in LOKASIYALAR:
                category = Kategori.objects.filter(slug=parts[1]).first()
                if category:
                    ads = active_public_listings().filter(kategori_id__in=[category.pk, *category.alt_kateqoriyalar.values_list('pk', flat=True)])
                    count = in_location(ads, parts[2]).count()
                    state = 'location_has_evidence' if count else 'location_without_evidence'
                    action = ('Check live index/canonical and sitemap after deployment' if count
                              else 'Keep noindex until real public inventory or declared service coverage exists')
                else:
                    state, action = 'missing_category', 'Investigate the historical category and any genuine successor'
            results.append([url, state, count, action])
        out = open(options['output'], 'w', encoding='utf-8-sig', newline='') if options.get('output') else self.stdout
        try:
            writer = csv.writer(out)
            writer.writerow(['URL', 'State', 'Matching_active_listings', 'Action'])
            writer.writerows(results)
        finally:
            if options.get('output'):
                out.close()
