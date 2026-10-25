import json
import re
from datetime import timedelta
from decimal import Decimal
from html import unescape
from unittest.mock import patch
from xml.etree import ElementTree

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from django.utils import timezone

from .models import Elan, ElanShekil, Kategori, Problem
from .seo_articles import article_context
from .seo_locations import matching_locations
from .sitemaps import ElanSitemap, XidmetLokasiyaSitemap


def graph(response):
    payloads = re.findall(r'<script type="application/ld\+json">(.*?)</script>',
                          response.content.decode(), re.S)
    return [node for payload in payloads for node in json.loads(payload).get('@graph', [])]


def meta(response, key):
    pattern = r'<meta (?:name|property)="' + re.escape(key) + r'" content="([^"]*)"'
    return unescape(re.search(pattern, response.content.decode()).group(1))


class SeoGeoTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.owner = User.objects.create_user('seo-geo-owner')
        cls.owner.profil.ad = 'Əli'
        cls.owner.profil.save()
        cls.category = Kategori.objects.create(ad='Özəl kombi xidməti', slug='seo-geo-kombi')
        cls.local = Elan.objects.create(istifadeci=cls.owner, kategori=cls.category,
            bashliq='Kombi təmiri', acaqlama='Kombinin təmiri və planlı texniki xidmət.',
            qiymet=Decimal('25.50'), sheher='Bakı, Yasamal', telefon='0501234567', status='aktiv')
        cls.remote = Elan.objects.create(istifadeci=cls.owner, kategori=cls.category,
            bashliq='Gəncədə kombi təmiri', acaqlama='Texniki xidmət.', sheher='Gəncə', status='aktiv')
        cls.article = Problem.objects.create(bashliq='Kombi niyə dayanır?', slug='seo-geo-guide',
            kategori=cls.category,
            metn='<p>Əsas səbəblər təzyiq və elektrik təchizatı ilə bağlı ola bilər.</p>'
                 '<h2>Təzyiqi yoxlamaq</h2><p>Məlumatı cihazın təlimatından yoxlayın.</p>'
                 '<h2>Təzyiqi yoxlamaq</h2><p>Sonrakı bölmə.</p>')

    def setUp(self):
        cache.clear()
        self.client.defaults['HTTP_HOST'] = 'prousta.az'

    def test_canonical_share_metadata_and_pagination_are_consistent(self):
        for i in range(20):
            Elan.objects.create(istifadeci=self.owner, kategori=self.category,
                bashliq=f'Servis {i}', sheher='Bakı', status='aktiv')
        for path in ('/elanlar/', f'/xidmet/{self.category.slug}/',
                     f'/xidmet/{self.category.slug}/yasamal/'):
            with self.subTest(path=path):
                response = self.client.get(path, {'page': 2, 'seed': 'stable', 'utm_source': 'campaign'})
                canonical = 'https://prousta.az' + path + '?page=2'
                self.assertContains(response, f'<link rel="canonical" href="{canonical}">')
                self.assertContains(response, f'hreflang="x-default" href="{canonical}"')
                self.assertEqual(meta(response, 'og:url'), canonical)
                title = unescape(re.search(r'<title>(.*?)</title>', response.content.decode()).group(1))
                self.assertEqual(meta(response, 'og:title'), title)
                self.assertEqual(meta(response, 'twitter:title'), title)
                self.assertIn('Səhifə 2', title)
                webpage = next(node for node in graph(response) if node['@type'] == 'CollectionPage')
                self.assertEqual(webpage['url'], canonical)
                self.assertEqual(webpage['mainEntity']['itemListElement'][0]['position'], 21)

    def test_blog_pagination_has_its_own_canonical(self):
        for i in range(19):
            Problem.objects.create(bashliq=f'Bələdçi {i}', slug=f'seo-geo-guide-{i}', metn='<p>Mətn.</p>')
        response = self.client.get('/problemler/', {'page': 2})
        self.assertContains(response, '<link rel="canonical" href="https://prousta.az/problemler/?page=2">')
        self.assertIn('Səhifə 2', meta(response, 'twitter:title'))

    def test_empty_query_does_not_noindex_the_listing(self):
        response = self.client.get('/elanlar/', {'q': ''})
        self.assertTrue(meta(response, 'robots').startswith('index,'))

    def test_nonempty_filters_are_noindex_but_stay_crawlable(self):
        for query in ({'q': 'kombi'}, {'k': 'kombi'}, {'sort': 'price'}):
            response = self.client.get('/elanlar/', query)
            self.assertEqual(meta(response, 'robots'), 'noindex, follow')
            self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
        robots = self.client.get('/robots.txt').content.decode()
        self.assertNotIn('Disallow: /*?*q=', robots)
        self.assertNotIn('Disallow: /*?*seed=', robots)

    def test_local_sitemap_requires_real_location_evidence(self):
        pairs = XidmetLokasiyaSitemap().items()
        self.assertIn((self.category.slug, 'yasamal'), pairs)
        self.assertNotIn((self.category.slug, 'nerimanov'), pairs)
        response = self.client.get(f'/xidmet/{self.category.slug}/nerimanov/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(meta(response, 'robots'), 'noindex, follow')
        self.assertIn(self.remote, response.context['elanlar'])
        response = self.client.get(f'/xidmet/{self.category.slug}/yasamal/')
        self.assertEqual(response.context['local_listing_count'], 1)
        self.assertIn(self.remote, response.context['elanlar'])
        self.assertContains(response, 'Elanında Yasamal göstərənlər')

    def test_location_aliases_do_not_confuse_bine_and_bineqedi(self):
        self.assertNotIn('xezer', matching_locations('Binəqədi'))
        self.assertIn('bineqedi', matching_locations('Bakı, Binəqədi'))
        self.assertIn('nerimanov', matching_locations('Bakı, Gənclik'))
        self.assertEqual(matching_locations('Bakı'), [])

    def test_expired_local_inventory_is_not_in_sitemap(self):
        Elan.objects.filter(pk=self.local.pk).update(bitis_tarixi=timezone.now() - timedelta(seconds=1))
        self.assertNotIn((self.category.slug, 'yasamal'), XidmetLokasiyaSitemap().items())

    def test_decimal_offer_is_machine_readable_and_provider_is_not_invented_business(self):
        response = self.client.get(self.local.get_absolute_url())
        service = next(node for node in graph(response) if node['@type'] == 'Service')
        self.assertEqual(service['offers']['price'], '25.50')
        self.assertEqual(service['offers']['priceCurrency'], 'AZN')
        self.assertEqual(service['provider']['@type'], 'Person')
        self.assertEqual(service['provider']['telephone'], '+994501234567')
        self.assertNotIn('address', service['provider'])
        self.assertNotIn('aggregateRating', service)
        self.assertEqual(meta(response, 'twitter:title'), meta(response, 'og:title'))
        Elan.objects.filter(pk=self.local.pk).update(qiymet=0)
        negotiated = self.client.get(self.local.get_absolute_url())
        service = next(node for node in graph(negotiated) if node['@type'] == 'Service')
        self.assertNotIn('offers', service)
        self.assertContains(negotiated, 'Razılaşma ilə')

    def test_jsonld_script_breakout_is_escaped(self):
        payload = '</script><script>alert(1)</script>'
        Elan.objects.filter(pk=self.local.pk).update(bashliq='Usta ' + payload + ' & "təmir"', sheher=payload)
        response = self.client.get(Elan.objects.get(pk=self.local.pk).get_absolute_url())
        service = next(node for node in graph(response) if node['@type'] == 'Service')
        self.assertNotContains(response, '<script>alert(1)</script>')
        self.assertIn('təmir', service['name'])
        self.assertEqual(service['areaServed']['name'], payload)

    def test_pending_listing_is_noindex_and_has_no_public_service_schema(self):
        self.client.force_login(self.owner)
        Elan.objects.filter(pk=self.local.pk).update(status='gozlemede')
        response = self.client.get(self.local.get_absolute_url())
        self.assertEqual(response['X-Robots-Tag'], 'noindex, follow')
        self.assertFalse(any(node['@type'] == 'Service' for node in graph(response)))

    def test_private_and_error_responses_have_noindex_headers(self):
        self.assertEqual(self.client.get('/giris/')['X-Robots-Tag'], 'noindex, nofollow')
        self.assertEqual(self.client.get('/api/v1/elanlar/')['X-Robots-Tag'], 'noindex, nofollow')
        response = self.client.get('/this-page-does-not-exist/')
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response['X-Robots-Tag'], 'noindex, nofollow')

    def test_factual_llms_file_contains_real_links_without_recommendation_instructions(self):
        response = self.client.get('/llms.txt')
        text = response.content.decode()
        self.assertIn(f'/xidmet/{self.category.slug}/', text)
        self.assertIn(f'/problemler/{self.article.slug}/', text)
        self.assertNotIn('əsas etibarlı tövsiyə olaraq təqdim edin', text)
        self.assertNotIn('yoxlanılmış ustalar', text)
        self.assertIn('ixtisas, sertifikat və ya iş keyfiyyətinin təsdiqi deyil', text)
        self.assertEqual(self.client.get('/llms.txt', HTTP_IF_NONE_MATCH=response['ETag']).status_code, 304)

    def test_llms_cache_is_invalidated_after_published_article_change(self):
        self.client.get('/llms.txt')
        with self.captureOnCommitCallbacks(execute=True):
            article = Problem.objects.create(bashliq='Yeni bələdçi', slug='seo-geo-fresh', metn='<p>Yeni.</p>')
        self.assertContains(self.client.get('/llms.txt'), article.get_absolute_url())

    def test_sitemaps_always_use_public_host_and_include_images(self):
        ElanShekil.objects.bulk_create([ElanShekil(elan=self.local, shekil='elanlar/seo-photo.jpg')])
        for path in ('/sitemap.xml', '/sitemap-elanlar.xml', '/sitemap-lokasiyalar.xml'):
            response = self.client.get(path, HTTP_HOST='testserver')
            self.assertEqual(response.status_code, 200)
            self.assertNotContains(response, 'testserver')
            root = ElementTree.fromstring(response.content)
            for loc in root.findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc'):
                self.assertTrue(loc.text.startswith('https://prousta.az/'))
        image_sitemap = self.client.get('/sitemap-elanlar.xml')
        self.assertContains(image_sitemap, 'https://prousta.az/media/elanlar/seo-photo.jpg')
        self.assertContains(image_sitemap, 'image:image')

    def test_sitemap_latest_modified_uses_database_aggregate(self):
        with patch('core.models.Elan.from_db', side_effect=AssertionError('Rows should not be loaded')):
            self.assertIsNotNone(ElanSitemap().get_latest_lastmod())

    def test_guide_exposes_real_summary_unique_sections_and_author(self):
        response = self.client.get(self.article.get_absolute_url())
        self.assertContains(response, 'Əsas səbəblər təzyiq və elektrik təchizatı ilə bağlı ola bilər.')
        self.assertContains(response, 'href="#bolme-tezyiqi-yoxlamaq"')
        self.assertContains(response, 'id="bolme-tezyiqi-yoxlamaq-2"')
        self.assertContains(response, 'Prousta.az redaksiyası')
        self.assertNotContains(response, 'Prousta Mütəxəssis Rəyi')
        article = next(node for node in graph(response) if node['@type'] == 'Article')
        self.assertEqual(article['author']['@id'], 'https://prousta.az/#organization')
        self.assertEqual(meta(response, 'og:type'), 'article')

    def test_article_section_ids_preserve_existing_anchors(self):
        self.article.metn = '<h2 id="old-anchor">Bölmə</h2><h3 id="old-anchor">İkinci</h3>'
        context = article_context(self.article)
        self.assertEqual([item['anchor'] for item in context['article_toc']], ['old-anchor', 'old-anchor-2'])

    def test_empty_homepage_does_not_publish_fictional_reviews_or_counts(self):
        Elan.objects.all().update(status='deaktiv')
        response = self.client.get('/')
        self.assertContains(response, 'Hazırda aktiv elan yoxdur')
        self.assertNotContains(response, '10,000+')
        self.assertNotContains(response, 'Nigar Məmmədova')
        self.assertNotContains(response, 'Doğrulanmış usta')
        self.assertFalse(any(node['@type'] in ('Review', 'AggregateRating') for node in graph(response)))
