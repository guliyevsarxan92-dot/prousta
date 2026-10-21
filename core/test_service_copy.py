import importlib
import json
import re
from html import unescape
from types import SimpleNamespace

from django.apps import apps
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.db import connection
from django.template.loader import render_to_string
from django.test import SimpleTestCase, TestCase, override_settings


migration = importlib.import_module('core.migrations.0027_fix_service_copy')
seed = importlib.import_module('core.migrations.0011_seed_kategoriyalar')
old_seo = importlib.import_module('core.migrations.0013_kategori_seo_metn_data')


def plain(text):
    return ' '.join(unescape(re.sub('<[^>]+>', '', text)).split())


@override_settings(STORAGES={'staticfiles': {'BACKEND': 'django.contrib.staticfiles.storage.StaticFilesStorage'}})
class ServiceTemplateTests(SimpleTestCase):
    def test_all_categories_and_local_pages_keep_urls_and_valid_faq(self):
        categories = [(c['ad'], c['slug']) for c in seed.KATEQORIYALAR]
        categories += [row for c in seed.KATEQORIYALAR for row in c['alt']]
        categories.append(('Dizayn \"Studio\" & İnteryer', 'test-dizayn'))
        for name, slug in categories:
            name = migration.NAME_FIXES.get(slug, (name, name))[1]
            category = SimpleNamespace(ad=name, slug=slug, seo_title='', seo_description='', seo_metn='',
                                       ust_kategori=None, alt_kateqoriyalar=SimpleNamespace(all=[]))
            for local in (False, True):
                with self.subTest(category=name, local=local):
                    context = {'aktiv_kategori': category, 'elanlar': Paginator([], 20).page(1),
                               'kat_indexable': True, 'seo_page': 1, 'min_qiymet': 25 if local else None}
                    if local:
                        context.update(lokasiya='yasamal', lokasiya_melumat={
                            'ad': 'Yasamal', 'tam_ad': 'Yasamal rayonu', 'erazi': 'Yeni Yasamal', 'slug': 'yasamal'})
                    html = render_to_string('xidmet_detail.html', context)
                    for bad in ('ustası ustası', 'ustaları ustası', 'xidməti Xidməti', 'xidməti xidməti',
                                'larımızın', 'xidmətnin', 'üzrə xidmət üzrə'):
                        self.assertNotIn(bad, html)
                    url = f'/xidmet/{slug}/' + ('yasamal/' if local else '')
                    self.assertIn(f'<link rel="canonical" href="https://prousta.az{url}">', html)
                    self.assertIn(f'{name} üzrə xidmət göstərirsiniz?', unescape(html))
                    schemas = [json.loads(raw) for raw in re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)]
                    faq = next(item for schema in schemas for item in schema.get('@graph', []) if item['@type'] == 'FAQPage')
                    faq_html = html.split('Tez-tez verilən suallar (FAQ)', 1)[1]
                    visible = re.findall(r'<summary[^>]*>(.*?)</summary>\s*<p[^>]*>(.*?)</p>', faq_html, re.S)
                    self.assertEqual(len(visible), 3)
                    for item, (question, answer) in zip(faq['mainEntity'], visible):
                        self.assertEqual(plain(item['name']), plain(question))
                        self.assertEqual(plain(item['acceptedAnswer']['text']), plain(answer))

    def test_keyword_cleanup_preserves_real_content(self):
        clean = migration.clean_keyword_tail
        for ending in ('\nAçar sözlər: telefon ustasi baki', '\r\n\r\nAçar sözlər: kombi ustasi\r\n'):
            self.assertEqual(clean('Əsas xidmət mətni.' + ending), 'Əsas xidmət mətni.')
        for text in ('Açar sözlər: tək sətir', 'Mətn daxilində Açar sözlər: ifadəsi.',
                     'Mətn\nAçar sözlər: nümunə\nArdınca vacib məlumat.'):
            self.assertEqual(clean(text), text)

    def test_generated_seo_for_every_category(self):
        for group in seed.KATEQORIYALAR:
            for name, slug in group['alt']:
                corrected = migration.fix_generated_seo(old_seo._seo_html(name), name)
                with self.subTest(category=name):
                    self.assertNotIn(name.lower() + 'larımızın', corrected)
                    self.assertNotIn(f'{name} necə sifariş', corrected)
                    self.assertNotIn(f'{name} xidmətinin', corrected)


class CopyMigrationTests(TestCase):
    def test_migration_is_idempotent_and_preserves_ids_urls_and_custom_content(self):
        from core.models import Elan, Kategori
        category = Kategori.objects.get(slug='komputer-ustasi')
        category.ad = 'Komputer ustası'
        category.seo_metn = old_seo._seo_html(category.ad) + '<p>Unikal mətn və <a href="/xidmet/komputer-ustasi/">keçid</a>.</p>'
        category.save()
        user = User.objects.create_user(username='copy-test')
        ad = Elan.objects.create(istifadeci=user, kategori=category, bashliq='Komputer təmiri',
                                 acaqlama='Əsas xidmət mətni.\r\n\r\nAçar sözlər: komputer ustasi baki')
        identity = (ad.nomre, ad.get_absolute_url(), ad.yenilendi)
        for _ in range(2):
            migration.fix_copy(apps, SimpleNamespace(connection=connection))
        category.refresh_from_db()
        ad.refresh_from_db()
        self.assertEqual(category.ad, 'Kompüter ustası')
        self.assertEqual(category.slug, 'komputer-ustasi')
        self.assertIn('Unikal mətn', category.seo_metn)
        self.assertIn('/xidmet/komputer-ustasi/', category.seo_metn)
        self.assertNotIn('ustasılarımızın', category.seo_metn)
        self.assertEqual(ad.acaqlama, 'Əsas xidmət mətni.')
        self.assertEqual((ad.nomre, ad.get_absolute_url(), ad.yenilendi), identity)

    def test_custom_category_and_seo_are_not_overwritten(self):
        from core.models import Kategori
        category = Kategori.objects.get(slug='su-sizma')
        category.ad = 'Xüsusi su sızması xidməti'
        category.seo_metn = '<p>Özəl mətn.</p>'
        category.seo_title = 'Özəl başlıq'
        category.save()
        migration.fix_copy(apps, SimpleNamespace(connection=connection))
        category.refresh_from_db()
        self.assertEqual(category.ad, 'Xüsusi su sızması xidməti')
        self.assertEqual(category.seo_metn, '<p>Özəl mətn.</p>')
        self.assertEqual(category.seo_title, 'Özəl başlıq')

    def test_name_correction_does_not_break_inflected_words(self):
        from core.models import Kategori
        category = Kategori.objects.get(slug='su-sizma')
        category.ad = 'Su sızma'
        category.seo_metn = '<h2>Su sızma</h2><p>su sızması və su sızmalarının təyini.</p>'
        category.save()
        migration.fix_copy(apps, SimpleNamespace(connection=connection))
        category.refresh_from_db()
        self.assertEqual(category.ad, 'Su sızmasının aşkarlanması')
        self.assertIn('su sızması və su sızmalarının təyini.', category.seo_metn)
        self.assertIn('<h2>Su sızmasının aşkarlanması</h2>', category.seo_metn)
