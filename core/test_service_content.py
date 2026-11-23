import importlib
from types import SimpleNamespace

from django.test import SimpleTestCase

from core.service_content import (
    additional_html, catalog, get_content, metadata_value,
    source_links, sources,
)


class ServiceContentTests(SimpleTestCase):
    def test_every_seed_category_has_a_complete_unique_brief(self):
        seed = importlib.import_module('core.migrations.0011_seed_kategoriyalar')
        expected = {parent['slug'] for parent in seed.KATEQORIYALAR}
        expected.update(slug for parent in seed.KATEQORIYALAR for _, slug in parent['alt'])
        profiles = catalog()
        self.assertEqual(set(profiles), expected)
        for field in ('heading', 'description', 'intro'):
            self.assertEqual(len({item[field] for item in profiles.values()}), 114)
        valid_sources = set(sources())
        for slug, brief in profiles.items():
            with self.subTest(slug=slug):
                self.assertEqual(len(brief['scope']), 3)
                self.assertEqual(len(brief['pricing']), 3)
                self.assertEqual(len(brief['prepare']), 3)
                self.assertEqual(len(brief['questions']), 2)
                self.assertEqual(len(brief['queries']), 3)
                self.assertTrue(all(len(question) == 2 for question in brief['questions']))
                self.assertTrue(all(target in profiles and target != slug for target in brief['related']))
                self.assertTrue(set(brief['sources']) <= valid_sources)
                self.assertLessEqual(len(brief['description']), 160)
                self.assertLessEqual(len(brief['heading'] + ' | Prousta.az'), 70)

    def test_seed_boilerplate_gets_brief_metadata_but_custom_metadata_is_kept(self):
        legacy = importlib.import_module('core.migrations.0013_kategori_seo_metn_data')
        name = 'Telefon ustası'
        old_description = legacy._seo_html(name)
        default = SimpleNamespace(slug='telefon-ustasi', ad=name, seo_title='', seo_description='')
        self.assertTrue(metadata_value(default, 'seo_title').startswith(get_content(default)['heading']))
        self.assertEqual(metadata_value(default, 'seo_description'), get_content(default)['description'])
        custom = SimpleNamespace(slug='telefon-ustasi', ad=name, seo_title='Mənim başlığım',
                                 seo_description='Mənim izahım')
        self.assertEqual(metadata_value(custom, 'seo_title'), 'Mənim başlığım')
        self.assertEqual(metadata_value(custom, 'seo_description'), 'Mənim izahım')
        renamed = SimpleNamespace(slug='telefon-ustasi', ad='Tam başqa kateqoriya', seo_title='', seo_description='')
        self.assertIsNone(get_content(renamed))
        self.assertEqual(metadata_value(renamed, 'seo_title'), '')
        self.assertIn('Telefon ustası', old_description)

    def test_exact_legacy_blocks_are_hidden_while_custom_html_survives(self):
        legacy = importlib.import_module('core.migrations.0013_kategori_seo_metn_data')
        boilerplate = legacy._seo_html('Telefon ustası')
        block = boilerplate[boilerplate.find('<h2'):boilerplate.find('</p>') + 4]
        edited = block.replace('Telefon ustası', 'Telefon servisi')
        custom = '<p>Usta tərəfindən əlavə edilən məlumat.</p>'
        category = SimpleNamespace(slug='telefon-ustasi', ad='Telefon ustası', seo_metn=block + custom)
        self.assertEqual(additional_html(category), custom)
        category.seo_metn = edited + custom
        self.assertEqual(additional_html(category), edited + custom)
        unknown = SimpleNamespace(slug='özəl', ad='Özəl', seo_metn=boilerplate)
        self.assertEqual(additional_html(unknown), boilerplate)

    def test_source_links_resolve_to_reviewed_manifest(self):
        category = SimpleNamespace(slug='lazer-epilyasiyasi', ad='Lazer epilyasiyası ustası')
        links = source_links(category)
        self.assertEqual(len(links), 1)
        self.assertIn('aad.org', links[0]['url'])

