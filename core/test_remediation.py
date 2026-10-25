import io
from datetime import timedelta
from decimal import Decimal
from unittest.mock import patch

from PIL import Image
from django.contrib import admin
from django.contrib.auth.models import User
from django.core import mail, signing
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db import connection
from django.test import Client, RequestFactory, TestCase
from django.test.utils import CaptureQueriesContext
from django.utils import timezone
from rest_framework.authtoken.models import Token
from rest_framework.test import APIClient

from .admin import OdenisAdmin, SafeCSVWriter
from .identity import google_user
from .models import Bloklama, Elan, ElanShekil, Kategori, Mesaj, Odenis, Profil, ReklamBanner
from .payments import buy_vip
from .validation import image_upload


def photo(name='photo.jpg'):
    buffer = io.BytesIO()
    Image.new('RGB', (80, 60), 'grey').save(buffer, 'JPEG')
    return SimpleUploadedFile(name, buffer.getvalue(), content_type='image/jpeg')


class RemediationTests(TestCase):
    def setUp(self):
        cache.clear()
        self.user = User.objects.create_user('testowner', password='Strongpassword42', email='owner@example.com')
        self.other = User.objects.create_user('testother', password='Strongpassword42')
        self.category = Kategori.objects.first()
        self.ad = Elan.objects.create(istifadeci=self.user, kategori=self.category,
                                     bashliq='Kombi xidməti', acaqlama='Peşəkar təmir və texniki xidmət',
                                     telefon='0501234567', status='aktiv')
        self.api = APIClient()
        self.api.force_authenticate(self.user)
        self.web = Client()
        self.web.force_login(self.user, backend='django.contrib.auth.backends.ModelBackend')

    def test_payment_cannot_be_credited_twice_or_reversed(self):
        payment = Odenis.objects.create(istifadeci=self.user, nov='balans', mebleg=10)
        payment.status = 'tesdiq_edildi'
        payment.save()
        payment.save()
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 10)
        payment.status = 'legv_edildi'
        with self.assertRaises(ValidationError):
            payment.save()
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 10)

    def test_stale_payment_instance_does_not_credit_again(self):
        payment = Odenis.objects.create(istifadeci=self.user, nov='balans', mebleg=10)
        stale = Odenis.objects.get(pk=payment.pk)
        payment.status = 'tesdiq_edildi'
        payment.save()
        stale.status = 'tesdiq_edildi'
        stale.save()
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 10)

    def test_payment_failure_rolls_back_status_and_balance(self):
        payment = Odenis.objects.create(istifadeci=self.user, elan=self.ad, nov='vip', mebleg=Decimal('0.01'))
        payment.status = 'tesdiq_edildi'
        with self.assertRaises(ValidationError):
            payment.save()
        payment.refresh_from_db()
        self.assertEqual(payment.status, 'gozlemede')
        self.assertIsNone(payment.applied_at)

    def test_admin_approval_works(self):
        staff = User.objects.create_superuser('testadmin', password='Strongpassword42')
        payment = Odenis.objects.create(istifadeci=self.user, nov='balans', mebleg=7)
        request = RequestFactory().post('/')
        request.user = staff
        model_admin = OdenisAdmin(Odenis, admin.site)
        with patch.object(model_admin, 'message_user'):
            model_admin.tesdiq_et_action(request, Odenis.objects.filter(pk=payment.pk))
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 7)

    def test_vip_purchase_charges_once(self):
        Profil.objects.filter(istifadeci=self.user).update(balans=20)
        buy_vip(self.user, self.ad.pk, 'vip')
        with self.assertRaises(ValidationError):
            buy_vip(self.user, self.ad.pk, 'vip')
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 17)
        self.assertEqual(Odenis.objects.filter(istifadeci=self.user).count(), 1)

    def test_vip_purchase_insufficient_balance_has_no_side_effect(self):
        with self.assertRaises(ValidationError):
            buy_vip(self.user, self.ad.pk, 'vip')
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 0)
        self.assertFalse(Odenis.objects.exists())

    def test_expired_vip_is_not_renewed_by_edit(self):
        Elan.objects.filter(pk=self.ad.pk).update(vip_status='vip', vip_bitis=timezone.now() - timedelta(days=1))
        self.ad.refresh_from_db()
        self.ad.bashliq = 'Yeni elan başlığı'
        self.ad.save()
        self.ad.refresh_from_db()
        self.assertEqual(self.ad.vip_status, 'normal')
        self.assertFalse(self.ad.is_vip_aktiv())

    def test_weak_password_and_invalid_json_are_400(self):
        client = APIClient()
        self.assertEqual(client.post('/api/v1/auth/register/', {
            'username': 'newusername', 'email': 'valid@example.com', 'password': '123456'
        }, format='json').status_code, 400)
        self.assertEqual(client.post('/api/v1/auth/login/', {
            'username': None, 'password': 'anything'
        }, format='json').status_code, 400)
        self.assertEqual(client.post('/api/v1/auth/login/', [], format='json').status_code, 400)

    def test_auth_rate_limit(self):
        client = APIClient()
        for _ in range(5):
            client.post('/api/v1/auth/login/', {'username': 'absent', 'password': 'invalid'}, format='json')
        self.assertEqual(client.post('/api/v1/auth/login/', {}, format='json').status_code, 429)

    def test_google_does_not_attach_to_unverified_local_email(self):
        with self.assertRaises(ValidationError):
            google_user({'email': self.user.email, 'email_verified': True, 'sub': 'unrelated-google-id'})
        self.assertTrue(User.objects.get(pk=self.user.pk).check_password('Strongpassword42'))

    def test_google_subject_is_stable_and_inactive_user_rejected(self):
        info = {'email': 'newgoogle@example.com', 'email_verified': True, 'sub': 'stable-google-id'}
        user = google_user(info)
        self.assertEqual(google_user(info).pk, user.pk)
        user.is_active = False
        user.save()
        with self.assertRaises(ValidationError):
            google_user(info)

    def test_legacy_passwordless_google_account_is_claimed_and_old_tokens_revoked(self):
        legacy = User.objects.create_user('legacy-google', email='legacy@example.com')
        token = Token.objects.create(user=legacy)
        user = google_user({'email': legacy.email, 'email_verified': True, 'sub': 'legacy-subject'})
        self.assertEqual(user.pk, legacy.pk)
        self.assertFalse(Token.objects.filter(pk=token.pk).exists())
        self.assertTrue(user.social_auth.filter(uid='legacy-subject').exists())

    def test_primary_photo_and_phone_are_consistent(self):
        ElanShekil.objects.create(elan=self.ad, shekil=photo('first.jpg'))
        primary = ElanShekil.objects.create(elan=self.ad, shekil=photo('primary.jpg'), esas=True)
        self.assertEqual(self.ad.primary_photo.pk, primary.pk)
        self.assertEqual(self.ad.phone_e164, '+994501234567')

    def test_database_cache_is_shared_between_independent_instances(self):
        from django.core.cache.backends.db import DatabaseCache
        first = DatabaseCache('prousta_cache', {})
        second = DatabaseCache('prousta_cache', {})
        first.set('shared-test', 'value', timeout=30)
        self.assertEqual(second.get('shared-test'), 'value')

    def test_mobile_login_ticket_is_single_use(self):
        import hashlib
        from .models import MobileLoginTicket
        MobileLoginTicket.objects.create(user=self.user, digest=hashlib.sha256(b'one-use').hexdigest(),
                                          expires=timezone.now() + timedelta(seconds=60))
        self.assertRedirects(Client().get('/mobile/session/?t=one-use'), '/', fetch_redirect_response=False)
        self.assertRedirects(Client().get('/mobile/session/?t=one-use'), '/giris/', fetch_redirect_response=False)

    def test_mobile_google_login_is_rate_limited_before_provider_request(self):
        client = Client()
        for _ in range(5):
            self.assertEqual(client.post('/mobile/google-login/', data='{}',
                                         content_type='application/json').status_code, 400)
        response = client.post('/mobile/google-login/', data='{}', content_type='application/json')
        self.assertEqual(response.status_code, 429)
        self.assertEqual(response['Retry-After'], '60')

    def test_profile_lists_are_bounded_and_totals_cover_all_pages(self):
        Elan.objects.filter(pk=self.ad.pk).update(baxish_sayi=7)
        Elan.objects.bulk_create([
            Elan(istifadeci=self.user, kategori=self.category, nomre=f'PAGE{i:05d}',
                 bashliq='Səhifəli elan', status='aktiv', baxish_sayi=2)
            for i in range(31)
        ])
        response = self.web.get('/profil/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['elanlar']), 30)
        self.assertEqual(response.context['elanlar'].paginator.count, 32)
        self.assertEqual(response.context['cemi_baxish'], 69)
        self.assertContains(response, '?ads_page=2#elanlarim')
        self.assertEqual(len(self.web.get('/profil/?ads_page=2').context['elanlar']), 2)
        public = Client().get(f'/istifadeci/{self.user.pk}/')
        self.assertEqual(public.status_code, 200)
        self.assertEqual(len(public.context['elanlar']), 30)
        self.assertEqual(public.context['elanlar'].paginator.count, 32)
        self.assertEqual(Client().get(f'/istifadeci/{self.user.pk}/?page=999').status_code, 404)

    def test_password_change_revokes_token(self):
        token = Token.objects.create(user=self.user)
        self.user.set_password('Changedpassword42')
        self.user.save()
        self.assertFalse(Token.objects.filter(key=token.key).exists())

    def test_expired_token_is_rejected(self):
        token = Token.objects.create(user=self.user)
        Token.objects.filter(pk=token.pk).update(created=timezone.now() - timedelta(days=31))
        client = APIClient()
        client.credentials(HTTP_AUTHORIZATION='Token ' + token.key)
        self.assertEqual(client.get('/api/v1/auth/me/').status_code, 401)

    def test_reset_sends_link_without_changing_password_and_hides_email_existence(self):
        first = self.web.post('/sifre-unutdum/', {'email': self.user.email}, follow=True)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password('Strongpassword42'))
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('/sifre-yenile/', mail.outbox[0].body)
        self.assertNotIn('Strongpassword42', mail.outbox[0].body)
        second = self.web.post('/sifre-unutdum/', {'email': 'unknown@example.com'}, follow=True)
        self.assertEqual(first.status_code, second.status_code)
        self.assertContains(first, 'Hesab mövcuddursa')
        self.assertContains(second, 'Hesab mövcuddursa')

    def test_invalid_images_are_rejected_and_valid_images_reencoded(self):
        with self.assertRaises(ValidationError):
            image_upload(SimpleUploadedFile('fake.html', b'<html>audit</html>', content_type='image/jpeg'))
        normalized = image_upload(photo('original.png'))
        self.assertTrue(normalized.name.endswith('.jpg'))
        self.assertEqual(Image.open(normalized).format, 'JPEG')

    def test_payment_type_amount_and_receipt_validated(self):
        for kind, amount, upload in [('unknown', '5', photo()), ('balans', '501', photo()),
                                     ('vip', '0.01', photo()),
                                     ('balans', '5', SimpleUploadedFile('fake.html', b'<html/>'))]:
            response = self.api.post('/api/v1/payments/create/', {
                'nov': kind, 'mebleg': amount, 'elan_id': self.ad.pk if kind == 'vip' else '', 'qebz': upload
            }, format='multipart')
            self.assertEqual(response.status_code, 400)
        self.assertFalse(Odenis.objects.exists())

    def test_image_update_limit_and_multi_delete(self):
        for i in range(5):
            ElanShekil.objects.create(elan=self.ad, shekil=photo(str(i) + '.jpg'), esas=i == 0)
        url = f'/api/v1/elanlar/{self.ad.pk}/update/'
        self.assertEqual(self.api.patch(url, {'shekillar': photo()}, format='multipart').status_code, 400)
        ids = list(self.ad.shekillar.values_list('pk', flat=True))[:2]
        self.assertEqual(self.api.patch(url, {'silinecek_shekiller': ids}, format='json').status_code, 200)
        self.assertEqual(self.ad.shekillar.count(), 3)
        self.assertEqual(self.ad.shekillar.filter(esas=True).count(), 1)

    def test_negative_price_and_duplicate_category_edit_rejected(self):
        url = f'/api/v1/elanlar/{self.ad.pk}/update/'
        self.assertEqual(self.api.patch(url, {'qiymet': '-1'}, format='json').status_code, 400)
        category = Kategori.objects.exclude(pk=self.category.pk).first()
        second = Elan.objects.create(istifadeci=self.user, kategori=category, bashliq='Digər xidmət',
                                     acaqlama='Peşəkar təmir və texniki xidmət', telefon='+994501234567', status='aktiv')
        self.assertEqual(self.api.patch(f'/api/v1/elanlar/{second.pk}/update/', {
            'kategori': self.category.pk}, format='json').status_code, 400)

    def test_pending_listing_is_private_and_owner_can_preview(self):
        self.ad.status = 'gozlemede'
        self.ad.save()
        self.assertEqual(Client().get(self.ad.get_absolute_url()).status_code, 404)
        self.assertEqual(APIClient().get(f'/api/v1/elanlar/{self.ad.pk}/').status_code, 404)
        self.assertEqual(self.web.get(self.ad.get_absolute_url()).status_code, 200)

    def test_blocking_applies_to_web_and_api(self):
        Bloklama.objects.create(bloklayan=self.other, bloklanan=self.user)
        other_ad = Elan.objects.create(istifadeci=self.other, bashliq='Digər elan', acaqlama='Digər mətn', status='aktiv')
        self.assertEqual(self.web.post(f'/mesaj/yeni/{other_ad.pk}/', {'metn': 'spam'}).status_code, 404)
        self.assertEqual(self.api.post(f'/api/v1/messages/{self.other.pk}/', {'metn': 'spam'}, format='json').status_code, 403)
        self.assertEqual(self.api.get(f'/api/v1/messages/{self.other.pk}/').status_code, 403)
        self.assertFalse(Mesaj.objects.filter(gonderici=self.user, alici=self.other).exists())

    def test_owner_can_reply_to_customer(self):
        original = Mesaj.objects.create(gonderici=self.other, alici=self.user, elan=self.ad, metn='Sual')
        response = self.web.post(f'/mesaj/{original.pk}/cavab/', {'metn': 'Cavab'})
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Mesaj.objects.filter(gonderici=self.user, alici=self.other, metn='Cavab').exists())

    def test_staff_without_permissions_cannot_export(self):
        staff = User.objects.create_user('limitedstaff', is_staff=True)
        self.web.force_login(staff, backend='django.contrib.auth.backends.ModelBackend')
        self.assertEqual(self.web.get('/admin/core/elan/cixaris/?export=csv').status_code, 403)
        self.assertEqual(self.web.get('/admin/api/pending-notifications/').status_code, 403)

    def test_csv_formula_is_neutralized(self):
        output = io.StringIO()
        SafeCSVWriter(output).writerow(['=1+1', '+994501234567', 'normal'])
        self.assertTrue(output.getvalue().startswith("'=1+1,'+994"))

    def test_chat_query_count_is_bounded_and_history_has_cursor(self):
        for i in range(105):
            Mesaj.objects.create(gonderici=self.other, alici=self.user, metn=str(i))
        with CaptureQueriesContext(connection) as queries:
            response = self.api.get(f'/api/v1/messages/{self.other.pk}/')
        self.assertEqual(len(response.data), 100)
        self.assertLessEqual(len(queries), 7)
        older = self.api.get(f'/api/v1/messages/{self.other.pk}/', {'before_id': response.data[0]['id']})
        self.assertEqual(len(older.data), 5)
        delta = self.api.get(f'/api/v1/messages/{self.other.pk}/', {'after_id': response.data[-1]['id']})
        self.assertEqual(delta.data, [])

    def test_expired_vip_not_in_vip_filter(self):
        Elan.objects.filter(pk=self.ad.pk).update(vip_status='vip', vip_bitis=timezone.now() - timedelta(days=1))
        response = self.api.get('/api/v1/elanlar/?vip_only=1')
        self.assertNotIn(self.ad.pk, [ad['id'] for ad in response.data['results']])

    def test_beacon_get_and_expired_banner(self):
        banner = ReklamBanner.objects.create(movqe='ust', bitis_tarixi=timezone.now() - timedelta(days=1))
        self.assertEqual(Client(enforce_csrf_checks=True).get(f'/banner/{banner.pk}/baxis/', HTTP_USER_AGENT='Mozilla/5.0').status_code, 200)
        self.assertEqual(APIClient().get('/api/v1/banners/').data, [])

    def test_invalid_page_is_404_and_sitemap_index_exposes_sections(self):
        self.assertEqual(self.web.get(f'/xidmet/{self.category.slug}/?page=999999').status_code, 404)
        self.assertContains(self.web.get('/sitemap.xml'), 'sitemap-elanlar.xml')

    def test_receipts_require_owner_or_short_lived_signature(self):
        payment = Odenis.objects.create(istifadeci=self.user, nov='balans', mebleg=5, qebz=photo())
        url = f'/qebz/{payment.pk}/'
        self.assertEqual(Client().get(url).status_code, 404)
        response = self.web.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Cache-Control'], 'private, no-store')
        self.assertTrue(b''.join(response.streaming_content))
        signed_response = Client().get(payment.receipt_url)
        self.assertEqual(signed_response.status_code, 200)
        self.assertTrue(b''.join(signed_response.streaming_content))
        token = signing.dumps({'payment': payment.pk + 1, 'user': self.user.pk}, salt='receipt-download')
        self.assertEqual(Client().get(url, {'t': token}).status_code, 404)

    def test_deleted_storage_is_removed_only_after_commit(self):
        image = ElanShekil.objects.create(elan=self.ad, shekil=photo())
        storage, name = image.shekil.storage, image.shekil.name
        with self.captureOnCommitCallbacks(execute=True):
            image.delete()
            self.assertTrue(storage.exists(name))
        self.assertFalse(storage.exists(name))

    def test_failed_media_cleanup_is_queued_and_retried(self):
        from .models import MediaCleanupTask
        from .media_cleanup import process_task
        image = ElanShekil.objects.create(elan=self.ad, shekil=photo())
        storage, name = image.shekil.storage, image.shekil.name
        with patch.object(storage, 'delete', side_effect=OSError('storage unavailable')):
            with self.captureOnCommitCallbacks(execute=True):
                image.delete()
        task = MediaCleanupTask.objects.get(name=name)
        self.assertEqual(task.attempts, 1)
        self.assertTrue(storage.exists(name))
        process_task(task.pk)
        self.assertFalse(storage.exists(name))
        self.assertFalse(MediaCleanupTask.objects.filter(pk=task.pk).exists())

    def test_partial_upload_failure_rolls_back_listing_and_cleans_uploaded_file(self):
        from . import listings
        from .models import MediaCleanupTask
        real_store = listings.store_image
        stored = []
        def fail_second(*args, **kwargs):
            if stored:
                raise OSError('second upload failed')
            image = real_store(*args, **kwargs)
            stored.append((image.shekil.storage, image.shekil.name))
            return image
        category = Kategori.objects.exclude(pk=self.category.pk).first()
        with self.captureOnCommitCallbacks(execute=True):
            with patch('core.listings.store_image', side_effect=fail_second):
                with self.assertRaises(OSError):
                    listings.create_listing(self.user, {'kategori': category.pk, 'bashliq': 'Yeni xidmət',
                        'acaqlama': 'Peşəkar təmir və texniki xidmət', 'telefon': '0501234567'}, [photo(), photo()])
        self.assertEqual(Elan.objects.filter(istifadeci=self.user).count(), 1)
        self.assertFalse(stored[0][0].exists(stored[0][1]))
        self.assertFalse(MediaCleanupTask.objects.exists())

    def test_personal_lists_preserve_legacy_array_and_support_pagination(self):
        legacy = self.api.get('/api/v1/my-elanlar/')
        self.assertIsInstance(legacy.data, list)
        self.assertEqual(legacy['X-Result-Limit'], '1000')
        page = self.api.get('/api/v1/my-elanlar/?page=1')
        self.assertEqual(page.data['count'], 1)
        self.assertEqual(page.data['results'][0]['id'], self.ad.pk)

    def test_only_trusted_proxy_headers_are_used(self):
        from .middleware import TrustedProxyMiddleware
        middleware = TrustedProxyMiddleware(lambda request: None)
        untrusted = RequestFactory().get('/', REMOTE_ADDR='198.51.100.1',
            HTTP_X_FORWARDED_FOR='203.0.113.1', HTTP_X_FORWARDED_PROTO='https')
        middleware(untrusted)
        self.assertEqual(untrusted.META['REMOTE_ADDR'], '198.51.100.1')
        self.assertNotIn('HTTP_X_FORWARDED_PROTO', untrusted.META)
        trusted = RequestFactory().get('/', REMOTE_ADDR='127.0.0.1',
            HTTP_X_FORWARDED_FOR='203.0.113.1, 127.0.0.1', HTTP_X_FORWARDED_PROTO='https')
        middleware(trusted)
        self.assertEqual(trusted.META['REMOTE_ADDR'], '203.0.113.1')

    def test_readiness_hides_error_details(self):
        response = self.web.get('/health/')
        self.assertEqual(response.status_code, 200)
        with patch('core.health.cache.get', side_effect=RuntimeError('private details')):
            response = self.web.get('/health/')
        self.assertEqual(response.status_code, 503)
        self.assertNotContains(response, 'private details', status_code=503)
