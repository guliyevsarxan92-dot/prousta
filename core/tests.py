from django.contrib.auth.models import User
from django.core.cache import cache
from django.test import TestCase
from core.image_optimizer import get_banner_image_url, get_card_image_url
from core.models import ReklamBanner


class BannerMotionAndLanguagePersistenceTests(TestCase):
    def setUp(self):
        cache.clear()

    def test_banner_image_url_preserves_full_resolution_without_500px_crop(self):
        raw_url = 'https://res.cloudinary.com/dzu82itfd/image/upload/v1/media/bannerler/Kombi_1120x160_la4r6q'
        banner_url = get_banner_image_url(raw_url)
        card_url = get_card_image_url(raw_url)
        self.assertIn('f_auto,q_auto:best,w_2200,c_limit', banner_url)
        self.assertNotIn('w_500', banner_url)
        self.assertIn('w_500', card_url)

    def test_banners_render_uncropped_urls_and_adblock_resilient_routes(self):
        ReklamBanner.objects.all().delete()
        cache.clear()
        b_ust = ReklamBanner.objects.create(
            movqe='ust',
            bashliq='PROusta Üst Banner',
            link='https://wa.me/994515888884',
            shekil='bannerler/top_test.png',
            aktiv=True,
        )
        b_sol = ReklamBanner.objects.create(
            movqe='sol',
            bashliq='Su Sızma Sol Banner',
            link='https://wa.me/994515888884',
            shekil='bannerler/left_test.png',
            aktiv=True,
        )
        b_orta = ReklamBanner.objects.create(
            movqe='orta',
            bashliq='Kombi Orta Banner',
            link='https://wa.me/994515888884',
            shekil='bannerler/mid_test.png',
            aktiv=True,
        )
        cache.clear()
        resp = self.client.get('/', HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode('utf-8')
        self.assertIn('pu-top-showcase', html)
        self.assertIn('pu-wing-panel--left', html)
        self.assertIn(f'/partnyor/{b_ust.id}/kecid/', html)
        self.assertIn(f'/partnyor/{b_sol.id}/kecid/', html)

        view_resp = self.client.get(f'/partnyor/{b_ust.id}/izle/', HTTP_USER_AGENT='Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0)')
        self.assertEqual(view_resp.status_code, 200)
        b_ust.refresh_from_db()
        self.assertEqual(b_ust.baxis_sayi, 1)

        click_resp = self.client.get(f'/partnyor/{b_orta.id}/kecid/', HTTP_USER_AGENT='Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X)')
        self.assertEqual(click_resp.status_code, 302)
        self.assertEqual(click_resp['Location'], 'https://wa.me/994515888884')
        b_orta.refresh_from_db()
        self.assertEqual(b_orta.klik_sayi, 1)

    def test_russian_banner_placeholders_localized(self):
        ReklamBanner.objects.all().delete()
        cache.clear()
        resp = self.client.get('/ru/', HTTP_USER_AGENT='Mozilla/5.0')
        self.assertEqual(resp.status_code, 200)
        html = resp.content.decode('utf-8')
        self.assertIn('ВЕРХНИЙ РЕКЛАМНЫЙ БАННЕР', html)
        self.assertIn('Боковой баннер', html)

    def test_russian_language_persists_on_profile_and_shared_pages(self):
        user = User.objects.create_user(username='masteruser1', email='master1@example.com', password='Password123')
        self.client.force_login(user)

        # User visits Russian homepage -> sets prousta_lang=ru cookie
        ru_home = self.client.get('/ru/')
        self.assertEqual(ru_home.status_code, 200)
        self.assertEqual(ru_home.cookies['prousta_lang'].value, 'ru')

        # Now user navigates to /profil/ -> stays in Russian!
        prof_resp = self.client.get('/profil/')
        self.assertEqual(prof_resp.status_code, 200)
        prof_html = prof_resp.content.decode('utf-8')
        self.assertIn('<html lang="ru">', prof_html)
        self.assertIn('Мой профиль', prof_html)
        self.assertIn('Текущий баланс', prof_html)
        self.assertIn('Мои объявления', prof_html)

        # Navigating to /odenis/, /mesajlar/, /profil/duzelis/, /elan/yeni/ also stays in Russian
        for url, expected_ru in [
            ('/odenis/', 'Пополнить <span>баланс</span>'),
            ('/mesajlar/', 'Мои <span>сообщения</span>'),
            ('/profil/duzelis/', 'Данные <span>профиля</span>'),
            ('/elan/yeni/', 'Разместить объявление <span>об услуге</span>'),
        ]:
            r = self.client.get(url)
            self.assertEqual(r.status_code, 200)
            body = r.content.decode('utf-8')
            self.assertIn('<html lang="ru">', body)
            self.assertIn(expected_ru, body)

        # Switching back to AZ on /profil/?lang=az switches back to Azerbaijani
        az_prof = self.client.get('/profil/?lang=az')
        self.assertEqual(az_prof.status_code, 200)
        self.assertEqual(az_prof.cookies['prousta_lang'].value, 'az')
        az_html = az_prof.content.decode('utf-8')
        self.assertIn('<html lang="az">', az_html)
        self.assertIn('Cari Balansınız', az_html)
