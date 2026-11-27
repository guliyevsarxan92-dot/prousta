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

    def test_expired_listing_redirects_to_owners_new_listing(self):
        old = Elan.objects.create(istifadeci=self.owner, kategori=self.category,
            bashliq='Köhnə kombi elanı', sheher='Bakı', status='muddeti_bitmis')
        response = self.client.get(old.get_absolute_url())
        self.assertEqual(response.status_code, 301)
        self.assertIn(response['Location'], {self.local.get_absolute_url(), self.remote.get_absolute_url()})
        legacy = self.client.get(f'/elan/{old.pk}/')
        self.assertEqual(legacy.status_code, 301)

    def test_expired_listing_without_replacement_goes_to_service_page(self):
        other = User.objects.create_user('seo-geo-other')
        old = Elan.objects.create(istifadeci=other, kategori=self.category,
            bashliq='Köhnə elan', sheher='Bakı', status='deaktiv')
        response = self.client.get(old.get_absolute_url())
        self.assertRedirects(response, f'/xidmet/{self.category.slug}/', status_code=301,
                             fetch_redirect_response=False)

    def test_pending_listing_redirect_is_temporary_for_visitors(self):
        Elan.objects.filter(pk=self.local.pk).update(status='gozlemede')
        response = self.client.get(self.local.get_absolute_url())
        self.assertEqual(response.status_code, 302)

    def test_deleted_listing_redirects_and_unknown_is_gone(self):
        other = User.objects.create_user('seo-geo-deleted')
        old = Elan.objects.create(istifadeci=other, kategori=self.category,
            bashliq='Silinəcək elan', sheher='Bakı', status='aktiv')
        url = old.get_absolute_url()
        old.delete()
        response = self.client.get(url)
        self.assertRedirects(response, f'/xidmet/{self.category.slug}/', status_code=301,
                             fetch_redirect_response=False)
        self.assertEqual(self.client.get('/elan/999999-yoxdur-baki/').status_code, 410)

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
        self.assertIn('aktiv elan', text)
        self.assertEqual(self.client.get('/llms.txt', HTTP_IF_NONE_MATCH=response['ETag']).status_code, 304)
        robots = self.client.get('/robots.txt').content.decode()
        for ai_bot in ('OAI-SearchBot', 'ChatGPT-User', 'GPTBot', 'ClaudeBot', 'PerplexityBot', 'Google-Extended'):
            self.assertIn(f'User-agent: {ai_bot}', robots)

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

    def test_editorial_service_guide_makes_seed_category_indexable_and_links_related_services(self):
        from .seo import indexable_kategori_ids

        parent = Kategori.objects.get(slug='meiset-texnikasi')
        self.assertIn(parent.pk, indexable_kategori_ids())
        response = self.client.get('/xidmet/kombi-ustasi/')
        self.assertEqual(response.status_code, 200)
        self.assertTrue(meta(response, 'robots').startswith('index,'))
        self.assertContains(response, 'Ekrandakı xəta kodu')
        self.assertContains(response, 'href="/xidmet/santexnik/"')

        empty = Kategori.objects.create(ad='Boş sınaq kateqoriyası', slug='seo-geo-empty')
        cache.clear()
        self.assertNotIn(empty.pk, indexable_kategori_ids())

    def test_empty_template_categories_are_noindex_until_first_active_listing(self):
        from .seo import indexable_kategori_ids
        from .sitemaps import AltKategoriSitemap, KategoriSitemap

        empty_seed = Kategori.objects.get(slug='yukdasima')
        empty_parent = Kategori.objects.get(slug='neqliyyat-texnika')
        self.assertNotIn(empty_seed.pk, indexable_kategori_ids())
        self.assertNotIn(empty_parent.pk, indexable_kategori_ids())
        self.assertNotIn(empty_seed, AltKategoriSitemap().items())
        self.assertNotIn(empty_parent, KategoriSitemap().items())

        resp = self.client.get('/xidmet/yukdasima/')
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(meta(resp, 'robots'), 'noindex, follow')
        self.assertEqual(resp['X-Robots-Tag'], 'noindex, follow')
        self.assertNotIn('/xidmet/yukdasima/', self.client.get('/llms.txt').content.decode())

        kombi_resp = self.client.get('/xidmet/kombi-ustasi/')
        self.assertIn('Kombi ustası', meta(kombi_resp, 'og:title'))
        self.assertContains(kombi_resp, '<h1>Kombi ustası <span>Bakıda</span></h1>')

        ad_resp = self.client.get(self.local.get_absolute_url())
        self.assertIn('AZN', meta(ad_resp, 'og:title'))
        self.assertIn('Əli', meta(ad_resp, 'description'))

        with self.captureOnCommitCallbacks(execute=True):
            ad = Elan.objects.create(
                istifadeci=self.owner, kategori=empty_seed,
                bashliq='Peşəkar yükdaşıma xidməti', acaqlama='Bakı və ətraf ərazilərdə yükdaşıma.',
                sheher='Bakı', telefon='0501234567', status='aktiv',
            )
        self.assertIn(empty_seed.pk, indexable_kategori_ids())
        self.assertIn(empty_parent.pk, indexable_kategori_ids())
        self.assertIn(empty_seed, AltKategoriSitemap().items())
        self.assertIn(empty_parent, KategoriSitemap().items())
        resp_after = self.client.get('/xidmet/yukdasima/')
        self.assertTrue(meta(resp_after, 'robots').startswith('index,'))
        self.assertIn('/xidmet/yukdasima/', self.client.get('/llms.txt').content.decode())

        with self.captureOnCommitCallbacks(execute=True):
            ad.status = 'deaktiv'
            ad.save()
        self.assertNotIn(empty_seed.pk, indexable_kategori_ids())

    def test_problem_articles_pass_internal_links_to_canonical_service_and_topic_pages(self):
        kombi_cat = Kategori.objects.get(slug='kombi-ustasi')
        kombi_article = Problem.objects.create(
            bashliq='Kombi radiatorları zəif isidir və yuyulma vaxtıdır?',
            slug='seo-kombi-radiator-yuyulma',
            kategori=kombi_cat,
            metn='<p>Radiator xəttində çöküntü olduqda dövriyyə zəifləyə bilər.</p><h2>Yoxlama</h2><p>Detallar.</p>',
        )
        detail = self.client.get(kombi_article.get_absolute_url())
        self.assertEqual(detail.status_code, 200)
        html = detail.content.decode()
        self.assertNotIn('/problemler/?kategori=kombi-ustasi', html)
        self.assertContains(detail, 'href="/xidmet/kombi-ustasi/"')
        self.assertContains(detail, 'href="/xidmet/kombi-yuyulmasi/"')
        breadcrumb = next(node for node in graph(detail) if node['@type'] == 'BreadcrumbList')
        crumb_urls = [item['item'] for item in breadcrumb['itemListElement']]
        self.assertIn('https://prousta.az/xidmet/kombi-ustasi/', crumb_urls)

        blog_list = self.client.get('/problemler/')
        self.assertContains(blog_list, 'href="/xidmet/kombi-ustasi/" class="prob-card-kat"')

    def test_multi_area_selection_powers_local_seo_search_web_and_api(self):
        import io
        from PIL import Image
        from django.core.files.uploadedfile import SimpleUploadedFile
        from rest_framework.test import APIClient

        def make_photo(name='work.jpg'):
            buf = io.BytesIO()
            Image.new('RGB', (100, 80), 'green').save(buf, 'JPEG')
            return SimpleUploadedFile(name, buf.getvalue(), content_type='image/jpeg')

        elec = Kategori.objects.get(slug='elektrik')
        self.client.force_login(self.owner)
        create_resp = self.client.post('/elan/yeni/', {
            'bashliq': 'Təcrübəli elektrik ustası',
            'kategori': str(elec.pk),
            'qiymet': '30',
            'telefon': '501234567',
            'sheher': 'Bakı — Yasamal',
            'xidmet_erazileri': ['', 'yasamal', 'xirdalan', 'masazir'],
            'acaqlama': 'Mənzillərdə elektrik xətlərinin çəkilməsi və şit yığılması.',
            'shekillar': [make_photo()],
        })
        self.assertEqual(create_resp.status_code, 302)
        ad = Elan.objects.get(istifadeci=self.owner, kategori=elec)
        self.assertEqual(ad.erazi_sluglari, ['yasamal', 'xirdalan', 'masazir'])

        # Local pages for Xırdalan & Masazır become indexable and enter local sitemap; Yasamal is deduplicated (count=1)
        pairs = XidmetLokasiyaSitemap().items()
        self.assertIn(('elektrik', 'xirdalan'), pairs)
        self.assertIn(('elektrik', 'masazir'), pairs)
        self.assertIn(('temir-tikinti', 'xirdalan'), pairs)
        self.assertNotIn(('elektrik', 'sumqayit'), pairs)

        yasamal_resp = self.client.get('/xidmet/elektrik/yasamal/')
        self.assertEqual(yasamal_resp.context['local_listing_count'], 1)
        xirdalan_resp = self.client.get('/xidmet/elektrik/xirdalan/')
        self.assertTrue(meta(xirdalan_resp, 'robots').startswith('index,'))
        self.assertEqual(xirdalan_resp.context['local_listing_count'], 1)
        self.assertTrue(xirdalan_resp.context['has_declared_coverage'])

        # Search ranking prefers the multi-area listing for Xırdalan over a remote listing
        other_user = User.objects.create_user('remote-elec-owner')
        remote_ad = Elan.objects.create(
            istifadeci=other_user, kategori=elec, bashliq='Gəncə elektrik ustası',
            acaqlama='Elektrik işləri görülür.', sheher='Gəncə', telefon='0551234567', status='aktiv',
        )
        ranked = list(self.client.get('/xidmet/elektrik/xirdalan/').context['elanlar'])
        self.assertEqual([item.pk for item in ranked[:2]], [ad.pk, remote_ad.pk])

        # Listing detail shows clickable local SEO links and AdministrativeArea in JSON-LD
        ad_resp = self.client.get(ad.get_absolute_url())
        self.assertContains(ad_resp, 'href="/xidmet/elektrik/xirdalan/"')
        service_node = next(node for node in graph(ad_resp) if node['@type'] == 'Service')
        self.assertIsInstance(service_node['areaServed'], list)
        self.assertTrue(any(item.get('name') == 'Xırdalan şəhəri' for item in service_node['areaServed']))

        # API PATCH preserves areas when omitted, rejects invalid area, and updates when provided
        api = APIClient()
        api.force_authenticate(self.owner)
        self.assertEqual(
            api.patch(f'/api/v1/elanlar/{ad.pk}/update/', {'bashliq': 'Peşəkar elektrik ustası'}, format='json').status_code,
            200,
        )
        ad.refresh_from_db()
        self.assertEqual(ad.erazi_sluglari, ['yasamal', 'xirdalan', 'masazir'])
        self.assertEqual(
            api.patch(f'/api/v1/elanlar/{ad.pk}/update/', {'xidmet_erazileri': ['namelum-rayon']}, format='json').status_code,
            400,
        )
        patch_resp = api.patch(f'/api/v1/elanlar/{ad.pk}/update/', {'xidmet_erazileri': ['sumqayit']}, format='json')
        self.assertEqual(patch_resp.status_code, 200)
        self.assertEqual(patch_resp.json()['elan']['xidmet_erazileri'], ['sumqayit'])

        # Unchecking all checkboxes in HTML edit form clears areas cleanly
        edit_resp = self.client.post(f'/elan/{ad.pk}/duzelis/', {
            'bashliq': 'Peşəkar elektrik ustası',
            'kategori': str(elec.pk),
            'qiymet': '30',
            'telefon': '501234567',
            'sheher': 'Bakı',
            'xidmet_erazileri': [''],
            'acaqlama': 'Mənzillərdə elektrik xətlərinin çəkilməsi və şit yığılması.',
        })
        self.assertEqual(edit_resp.status_code, 302)
        ad.refresh_from_db()
        self.assertEqual(ad.erazi_sluglari, [])

    def test_russian_pages_hreflang_search_and_sitemap(self):
        # 1. AZ service page links to RU alternate via hreflang, and vice versa
        az_kombi = self.client.get('/xidmet/kombi-ustasi/')
        self.assertContains(az_kombi, '<link rel="alternate" hreflang="az" href="https://prousta.az/xidmet/kombi-ustasi/">')
        self.assertContains(az_kombi, '<link rel="alternate" hreflang="ru" href="https://prousta.az/ru/xidmet/kombi-ustasi/">')
        self.assertContains(az_kombi, '<link rel="alternate" hreflang="x-default" href="https://prousta.az/xidmet/kombi-ustasi/">')

        ru_kombi = self.client.get('/ru/xidmet/kombi-ustasi/')
        self.assertEqual(ru_kombi.status_code, 200)
        self.assertContains(ru_kombi, '<html lang="ru">')
        self.assertContains(ru_kombi, '<link rel="canonical" href="https://prousta.az/ru/xidmet/kombi-ustasi/">')
        self.assertContains(ru_kombi, '<link rel="alternate" hreflang="ru" href="https://prousta.az/ru/xidmet/kombi-ustasi/">')
        self.assertContains(ru_kombi, '<link rel="alternate" hreflang="az" href="https://prousta.az/xidmet/kombi-ustasi/">')
        self.assertContains(ru_kombi, '<link rel="alternate" hreflang="x-default" href="https://prousta.az/xidmet/kombi-ustasi/">')
        self.assertEqual(meta(ru_kombi, 'og:locale'), 'ru_RU')
        self.assertIn('Мастер по комби в Баку', meta(ru_kombi, 'og:title'))
        webpage = next(node for node in graph(ru_kombi) if node['@type'] == 'CollectionPage')
        self.assertEqual(webpage['inLanguage'], 'ru-RU')

        # 2. Priority topic guide in Russian (/ru/xidmet/kombi-yuyulmasi/)
        ru_topic = self.client.get('/ru/xidmet/kombi-yuyulmasi/')
        self.assertEqual(ru_topic.status_code, 200)
        self.assertContains(ru_topic, 'Промывка комби и радиаторов')
        self.assertTrue(meta(ru_topic, 'robots').startswith('index,'))

        # 3. Local district page in Russian (/ru/xidmet/seo-geo-kombi/yasamal/ vs empty nerimanov)
        ru_yasamal = self.client.get(f'/ru/xidmet/{self.category.slug}/yasamal/')
        self.assertEqual(ru_yasamal.status_code, 200)
        self.assertTrue(meta(ru_yasamal, 'robots').startswith('index,'))
        self.assertIn('в Ясамале', meta(ru_yasamal, 'og:title'))
        ru_nerimanov = self.client.get(f'/ru/xidmet/{self.category.slug}/nerimanov/')
        self.assertEqual(meta(ru_nerimanov, 'robots'), 'noindex, follow')

        # 4. Russian query search translates Cyrillic terms to find Azerbaijani listings
        ru_search = self.client.get('/ru/elanlar/', {'q': 'мастер комби ясамал'})
        self.assertEqual(ru_search.status_code, 200)
        self.assertEqual(meta(ru_search, 'robots'), 'noindex, follow')
        self.assertIn(self.local, ru_search.context['elanlar'])
        self.assertEqual(ru_search.context['elanlar'][0].pk, self.local.pk)

        # 5. Russian listing detail (/ru/elan/<id>-<slug>/) renders translated title, city, description, and hreflang
        ru_ad_url = '/ru' + self.local.get_absolute_url()
        ru_ad = self.client.get(ru_ad_url)
        self.assertEqual(ru_ad.status_code, 200)
        self.assertContains(ru_ad, '<html lang="ru">')
        self.assertContains(ru_ad, 'Ремонт комби (Ясамал)')
        self.assertContains(ru_ad, 'Баку, Ясамал')
        self.assertContains(ru_ad, f'<link rel="canonical" href="https://prousta.az{ru_ad_url}">')
        self.assertContains(ru_ad, f'<link rel="alternate" hreflang="az" href="https://prousta.az{self.local.get_absolute_url()}">')

        # 6. Russian sitemap (/sitemap-ru.xml) includes active & priority RU pages, listings, and excludes empty categories
        ru_sitemap = self.client.get('/sitemap-ru.xml')
        self.assertEqual(ru_sitemap.status_code, 200)
        self.assertContains(ru_sitemap, 'https://prousta.az/ru/')
        self.assertContains(ru_sitemap, 'https://prousta.az/ru/xidmet/kombi-ustasi/')
        self.assertContains(ru_sitemap, 'https://prousta.az/ru/xidmet/kombi-yuyulmasi/')
        self.assertContains(ru_sitemap, f'https://prousta.az/ru/xidmet/{self.category.slug}/yasamal/')
        self.assertContains(ru_sitemap, f'https://prousta.az{ru_ad_url}')
        self.assertNotContains(ru_sitemap, 'https://prousta.az/ru/xidmet/yukdasima/')
