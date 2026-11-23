import json
import re
from datetime import timedelta
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory

from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone

from core.models import Elan, Kategori
from core.seo_locations import in_location, location_counts, indexable_location_pairs
from core.service_pages import BAKU_AREAS, PROVIDER_CATEGORIES, pages, topics
from core.test_seo_geo import graph, meta


class FocusedServicePagesTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('superadmin')
        cls.owner.profil.ad = 'Xidmət icraçısı'
        cls.owner.profil.save()
        cls.ads = {}
        for slug in PROVIDER_CATEGORIES:
            category = Kategori.objects.get(slug=slug)
            cls.ads[slug] = Elan.objects.create(istifadeci=cls.owner, kategori=category,
                bashliq=category.ad, sheher='Bakı', status='aktiv', telefon='+994515888884',
                acaqlama='Kombi yuyulması, radiator yuma, boyler və qazan. Havalandırma montajı, zont və mühərrik təmizliyi.')

    def setUp(self):
        cache.clear()
        self.client.defaults['HTTP_HOST'] = 'prousta.az'

    def test_every_guide_renders_and_topic_urls_are_canonical(self):
        self.assertEqual(len(pages()), 11)
        self.assertEqual(len(topics()), 6)
        for slug, page in pages().items():
            with self.subTest(slug=slug):
                response = self.client.get(page['url'])
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, page['name'])
                self.assertContains(response, 'İşi qəbul edərkən yoxlayın')
                self.assertContains(response, 'Sifariş məlumatını hazırlayın')
                self.assertContains(response, 'href="https://prousta.az' + page['url'] + '"')
                self.assertTrue(meta(response, 'robots').startswith('index,'))
                faq = next(n for n in graph(response) if n['@type'] == 'FAQPage')
                self.assertEqual([n['name'] for n in faq['mainEntity']], [q for q, a in page['faq']])
                self.assertNotContains(response, 'Prousta Təcili Xidmət')

    def test_exact_and_starting_prices_are_attributed_to_real_provider(self):
        for slug in ('su-sizma', 'kanalizasiya-ustasi', 'kombi-yuyulmasi'):
            response = self.client.get(pages()[slug]['url'])
            service = next(n for n in graph(response) if n['@type'] == 'Service')
            self.assertEqual(service['provider']['url'], f'https://prousta.az/istifadeci/{self.owner.pk}/')
            self.assertEqual(service['provider']['telephone'], '+994515888884')
            self.assertEqual(service['broker']['@id'], 'https://prousta.az/#organization')
            if slug == 'kombi-yuyulmasi':
                self.assertNotIn('price', service['offers'])
                self.assertEqual(service['offers']['priceSpecification']['minPrice'], '30.00')
                self.assertContains(response, 'Radiator sayı')
            else:
                self.assertEqual(service['offers']['price'], '80.00')
                self.assertContains(response, '80 AZN')

    def test_provider_and_price_disappear_when_account_or_listing_is_not_public(self):
        self.owner.is_active = False
        self.owner.save(update_fields=['is_active'])
        response = self.client.get('/xidmet/su-sizma/')
        self.assertNotContains(response, 'Elan sahibinin təklifi')
        self.assertFalse(any(n['@type'] == 'Service' for n in graph(response)))
        self.owner.is_active = True
        self.owner.save(update_fields=['is_active'])
        Elan.objects.filter(pk=self.ads['su-sizma'].pk).update(bitis_tarixi=timezone.now() - timedelta(seconds=1))
        response = self.client.get('/xidmet/su-sizma/')
        self.assertNotContains(response, 'Elan sahibinin təklifi')

    def test_declared_related_service_uses_existing_account_without_creating_an_ad(self):
        Elan.objects.filter(pk__in=[self.ads['santexnik'].pk, self.ads['ariston-ustasi'].pk]).delete()
        before = Elan.objects.count()
        for path in ('/xidmet/santexnik/', '/xidmet/boyler-yuyulmasi/'):
            response = self.client.get(path)
            self.assertContains(response, 'Elan sahibinin təklifi')
            self.assertContains(response, f'href="/istifadeci/{self.owner.pk}/"')
        self.assertEqual(Elan.objects.count(), before)

    def test_declared_baku_coverage_restores_only_confirmed_service_local_pages(self):
        for area in BAKU_AREAS:
            response = self.client.get(f'/xidmet/kombi-ustasi/{area}/')
            self.assertEqual(response.status_code, 200)
            self.assertTrue(meta(response, 'robots').startswith('index,'))
            self.assertEqual(response.context['local_listing_count'], 1)
            self.assertContains(response, 'elan sahibinin bildirdiyi xidmət əhatəsinə')
        for area in ('xirdalan', 'masazir', 'sumqayit', 'saray', 'mehdiabad'):
            response = self.client.get(f'/xidmet/kombi-ustasi/{area}/')
            self.assertEqual(meta(response, 'robots'), 'noindex, follow')
        pairs = indexable_location_pairs()
        self.assertIn(('kombi-ustasi', 'yasamal'), pairs)
        self.assertIn(('meiset-texnikasi', 'yasamal'), pairs)
        self.assertNotIn(('kombi-ustasi', 'sumqayit'), pairs)

    def test_location_evidence_is_deduplicated_and_expires(self):
        ad = self.ads['kombi-ustasi']
        Elan.objects.filter(pk=ad.pk).update(sheher='Bakı, Yasamal')
        ads = Elan.objects.filter(pk=ad.pk)
        self.assertEqual(location_counts(ads)['yasamal'], 1)
        self.assertEqual(list(in_location(ads, 'yasamal')), list(ads))
        Elan.objects.filter(pk=ad.pk).update(bitis_tarixi=timezone.now() - timedelta(seconds=1))
        self.assertNotIn(('kombi-ustasi', 'pirallahi'), indexable_location_pairs())

    def test_coverage_is_not_applied_to_another_owner_or_unconfirmed_service(self):
        other = User.objects.create_user('another-service-owner')
        Elan.objects.filter(pk=self.ads['kombi-ustasi'].pk).update(istifadeci=other)
        response = self.client.get('/xidmet/kombi-ustasi/yasamal/')
        self.assertEqual(meta(response, 'robots'), 'noindex, follow')
        massage = Kategori.objects.get(slug='masaj-xidmeti')
        Elan.objects.create(istifadeci=self.owner, kategori=massage, bashliq='Masaj',
                           status='aktiv', sheher='Bakı', acaqlama='Xidmət')
        response = self.client.get('/xidmet/masaj-xidmeti/yasamal/')
        self.assertEqual(meta(response, 'robots'), 'noindex, follow')

    def test_topics_select_relevant_ads_without_falling_back_to_unrelated_inventory(self):
        Elan.objects.filter(pk=self.ads['kombi-ustasi'].pk).update(acaqlama='Yalnız plata təmiri')
        response = self.client.get('/xidmet/kombi-yuyulmasi/')
        self.assertEqual(response.context['elanlar'].paginator.count, 0)
        self.assertContains(response, 'aktiv elan yoxdur')
        self.assertEqual(self.client.get('/xidmet/kombi-yuyulmasi/yasamal/').status_code, 404)
        self.assertEqual(self.client.get('/xidmet/kombi-yuyulmasi/?page=2').status_code, 404)
        self.assertEqual(self.client.get('/xidmet/kombi-yuyulmasi/?page=bad').status_code, 404)

    def test_pagination_and_discovery_have_consistent_urls(self):
        for i in range(12):
            Elan.objects.create(istifadeci=self.owner, kategori=self.ads['kombi-ustasi'].kategori,
                bashliq=f'Kombi yuyulması {i}', acaqlama='Radiator yuma', sheher='Bakı', status='aktiv')
        response = self.client.get('/xidmet/kombi-yuyulmasi/?page=2&seed=test&utm_source=chatgpt.com')
        self.assertContains(response, '<link rel="canonical" href="https://prousta.az/xidmet/kombi-yuyulmasi/?page=2">')
        self.assertIn('Səhifə 2', meta(response, 'og:title'))
        for path in ('/llms.txt', '/sitemap-xidmet_beledcileri.xml'):
            response = self.client.get(path)
            for page in topics():
                self.assertContains(response, page['url'])

    def test_guides_are_visible_without_javascript_or_provider_inventory(self):
        Elan.objects.all().delete()
        response = self.client.get('/xidmet/boyler-yuyulmasi/')
        self.assertContains(response, 'Çən və serpantin')
        self.assertContains(response, 'Texniki məlumatın mənbələri')
        self.assertContains(response, '<noscript>')
        self.assertNotContains(response, 'Elan sahibinin təklifi')
        self.assertTrue(meta(response, 'robots').startswith('index,'))

    def test_recovery_audit_does_not_change_listing_lifecycle(self):
        ad = self.ads['kombi-ustasi']
        Elan.objects.filter(pk=ad.pk).update(status='deaktiv')
        with TemporaryDirectory() as directory:
            source = Path(directory) / 'urls.csv'
            source.write_text('URL\nhttps://prousta.az/elan/' + str(ad.pk) + '-old/\n'
                              'https://prousta.az/xidmet/su-sizma/yasamal/\n'
                              'https://prousta.az/xidmet/su-sizma/sumqayit/\n'
                              'https://prousta.az/elan/999999-old/\n')
            out = StringIO()
            call_command('audit_search_recovery', source=str(source), stdout=out)
            self.assertIn('not_public_listing', out.getvalue())
            self.assertIn('location_has_evidence', out.getvalue())
            self.assertIn('location_without_evidence', out.getvalue())
            self.assertIn('missing_listing', out.getvalue())
        ad.refresh_from_db()
        self.assertEqual(ad.status, 'deaktiv')
