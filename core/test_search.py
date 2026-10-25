import json
import re
from datetime import timedelta

from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase, override_settings
from django.utils import timezone

from .models import Elan, Kategori
from .sitemaps import XidmetLokasiyaSitemap


@override_settings(STORAGES={
    'default': {'BACKEND': 'django.core.files.storage.FileSystemStorage'},
    'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'},
})
class LocationSearchTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.user = User.objects.create_user(username='search-test')
        cls.parent = Kategori.objects.create(ad='İstilik xidmətləri', slug='search-heating')
        cls.category = Kategori.objects.create(ad='Kombi ustası', slug='search-kombi', ust_kategori=cls.parent)
        cls.remote = Elan.objects.create(
            istifadeci=cls.user, kategori=cls.category, bashliq='İstilik təmiri',
            acaqlama='Quraşdırma və texniki xidmət', sheher='Gəncə', status='aktiv',
        )
        cls.local = Elan.objects.create(
            istifadeci=cls.user, kategori=cls.category, bashliq='Kombi təmiri',
            acaqlama='Texniki xidmət', sheher='Yasamal', status='aktiv',
        )
        cls.other = Elan.objects.create(
            istifadeci=cls.user, bashliq='Mebel yığılması', acaqlama='Mebel', status='aktiv',
        )
        cls.expired = Elan.objects.create(
            istifadeci=cls.user, kategori=cls.category, bashliq='Kombi ustası',
            acaqlama='Təmir', status='aktiv', bitis_tarixi=timezone.now() - timedelta(days=1),
        )

    def setUp(self):
        cache.clear()

    def test_web_search_ignores_location_but_keeps_service_relevance(self):
        for query in ('Yasamal kombi ustasi', 'KOMBİ USTASI Yasamalda', 'Bakıda kombi ustası',
                      'kombi ustasi Gəncədə', 'kombi ustasi 28 May', 'Yasamal rayonunda kombi ustası'):
            with self.subTest(query=query):
                response = self.client.get('/elanlar/', {'q': query})
                self.assertEqual(response.status_code, 200)
                self.assertEqual({ad.pk for ad in response.context['elanlar']}, {self.remote.pk, self.local.pk})

    def test_location_only_search_and_local_page_keep_other_areas(self):
        response = self.client.get('/elanlar/', {'q': 'Yasamal'})
        self.assertEqual(response.context['elanlar'][0].pk, self.local.pk)
        self.assertIn(self.remote, response.context['elanlar'])
        for slug in (self.category.slug, self.parent.slug):
            response = self.client.get(f'/xidmet/{slug}/yasamal/')
            self.assertEqual([ad.pk for ad in response.context['elanlar']], [self.local.pk, self.remote.pk])

    def test_api_city_is_ordering_preference_and_search_matches_web(self):
        for city in ('Yasamal', 'Sumqayıt', 'Bütün Azərbaycan'):
            response = self.client.get('/api/v1/elanlar/', {'kategori': self.category.slug, 'seher': city,
                                                         'q': 'Yasamal kombi ustasi'})
            self.assertEqual(response.status_code, 200)
            self.assertEqual({ad['id'] for ad in response.json()['results']}, {self.local.pk, self.remote.pk})
            if city == 'Yasamal':
                self.assertEqual(response.json()['results'][0]['id'], self.local.pk)

    def test_unknown_service_does_not_fall_back_to_unrelated_ads(self):
        response = self.client.get(f'/xidmet/{self.category.slug}/yasamal/', {'q': 'tapilmayanxidmet'})
        self.assertEqual(response.context['elanlar'].paginator.count, 0)
        self.assertContains(response, 'Axtarışınıza uyğun elan tapılmadı')
        self.assertNotContains(response, 'Bu kateqoriyada hələ aktiv elan yoxdur')

    def test_seed_pagination_is_indexable_and_has_consistent_canonical(self):
        for i in range(20):
            Elan.objects.create(istifadeci=self.user, kategori=self.category, bashliq=f'Kombi {i}',
                                acaqlama='Təmir', status='aktiv')
        path = f'/xidmet/{self.category.slug}/yasamal/'
        response = self.client.get(path, {'page': 2, 'seed': 'pagination', 'utm_source': 'test'})
        self.assertContains(response, f'<link rel="canonical" href="https://prousta.az{path}?page=2">')
        self.assertNotContains(response, 'noindex, follow')
        schemas = [json.loads(raw) for raw in re.findall(
            r'<script type="application/ld\+json">(.*?)</script>', response.content.decode(), re.S)]
        collection = next(item for schema in schemas for item in schema.get('@graph', [])
                          if item['@type'] == 'CollectionPage')
        self.assertEqual(collection['mainEntity']['itemListElement'][0]['position'], 21)

    def test_empty_local_pages_are_noindex_and_excluded_from_sitemap(self):
        empty = Kategori.objects.create(ad='Boş xidmət', slug='search-empty', seo_metn='Unikal mətn')
        response = self.client.get(f'/xidmet/{empty.slug}/yasamal/')
        self.assertContains(response, 'noindex, follow')
        items = XidmetLokasiyaSitemap().items()
        self.assertNotIn((empty.slug, 'yasamal'), items)
        self.assertIn((self.category.slug, 'yasamal'), items)
        self.assertIn((self.parent.slug, 'yasamal'), items)

    def test_search_noindex_remains_crawlable(self):
        response = self.client.get('/elanlar/', {'q': 'kombi'})
        self.assertContains(response, 'noindex, follow')
        response = self.client.get('/robots.txt')
        self.assertNotContains(response, 'Disallow: /*?*q=')
        self.assertNotContains(response, 'Disallow: /*?*seed=')

    def test_expired_ads_are_hidden_even_when_status_cleanup_is_cached(self):
        cache.set('elan_status_update', True, 60)
        response = self.client.get('/api/v1/elanlar/', {'kategori': self.category.slug})
        self.assertNotIn(self.expired.pk, {ad['id'] for ad in response.json()['results']})
        response = self.client.get(f'/xidmet/{self.category.slug}/yasamal/')
        self.assertNotIn(self.expired, response.context['elanlar'])

    def test_crawlers_keep_the_same_rotation_across_requests(self):
        path = f'/xidmet/{self.category.slug}/'
        first = self.client.get(path, HTTP_USER_AGENT='Googlebot')
        second = self.client.get(path, {'page': 1}, HTTP_USER_AGENT='Googlebot')
        self.assertEqual(first.context['elan_seed'], second.context['elan_seed'])
