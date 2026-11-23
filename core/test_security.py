from decimal import Decimal
from unittest.mock import patch

from django.contrib.auth.models import User
from django.test import Client, TestCase, override_settings

from .models import Odenis, ReklamBanner


class _Resp:
    def __init__(self, data, status_code=200):
        self._data = data
        self.status_code = status_code
        self.content = b'{}'

    def json(self):
        return self._data


@override_settings(SECURE_SSL_REDIRECT=False)
class PaymentSecurityTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='payuser01', password='StrongPass!2026x')
        self.client = Client()
        self.client.login(username='payuser01', password='StrongPass!2026x')

    def _pending(self, xarici_id, mebleg='25.00'):
        return Odenis.objects.create(istifadeci=self.user, nov='balans', mebleg=Decimal(mebleg),
                                     metod='birbank', status='gozlemede', xarici_id=xarici_id)

    @override_settings(DEBUG=False, BIRBANK_MERCHANT_ID='', BIRBANK_MERCHANT_SECRET='')
    def test_simulated_order_never_credits_in_production(self):
        odenis = self._pending('SIM-1-2500')
        self.client.get(f'/odenis/birbank/ugurlu/?odenis_id={odenis.pk}&STATUS=FullyPaid')
        odenis.refresh_from_db()
        self.user.profil.refresh_from_db()
        self.assertNotEqual(odenis.status, 'tesdiq_edildi')
        self.assertEqual(self.user.profil.balans, Decimal('0'))

    @override_settings(DEBUG=False, BIRBANK_MERCHANT_ID='', BIRBANK_MERCHANT_SECRET='')
    def test_simulator_page_hidden_in_production(self):
        odenis = self._pending('SIM-2-2500')
        resp = self.client.get(f'/odenis/birbank/simulator/?odenis_id={odenis.pk}')
        self.assertEqual(resp.status_code, 404)

    @override_settings(BIRBANK_MERCHANT_ID='m', BIRBANK_MERCHANT_SECRET='s')
    def test_amount_mismatch_is_rejected(self):
        odenis = self._pending('776655', mebleg='100.00')
        paid_less = _Resp({'order': {'status': 'FullyPaid', 'amount': '1.00', 'currency': 'AZN'}})
        with patch('requests.get', return_value=paid_less):
            self.client.get(f'/odenis/birbank/ugurlu/?odenis_id={odenis.pk}')
            self.client.get(f'/odenis/birbank/callback/?ID=776655&STATUS=FullyPaid')
        odenis.refresh_from_db()
        self.user.profil.refresh_from_db()
        self.assertNotEqual(odenis.status, 'tesdiq_edildi')
        self.assertEqual(self.user.profil.balans, Decimal('0'))

    @override_settings(BIRBANK_MERCHANT_ID='m', BIRBANK_MERCHANT_SECRET='s')
    def test_callback_ignores_forged_status_parameter(self):
        odenis = self._pending('998877')
        not_paid = _Resp({'order': {'status': 'Preparing', 'amount': '25.00', 'currency': 'AZN'}})
        with patch('requests.get', return_value=not_paid):
            Client().get('/odenis/birbank/callback/?ID=998877&STATUS=FullyPaid')
        odenis.refresh_from_db()
        self.assertEqual(odenis.status, 'gozlemede')

    @override_settings(BIRBANK_MERCHANT_ID='m', BIRBANK_MERCHANT_SECRET='s')
    def test_cannot_confirm_other_users_payment(self):
        other = User.objects.create_user(username='otheruser1', password='StrongPass!2026x')
        odenis = Odenis.objects.create(istifadeci=other, nov='balans', mebleg=Decimal('5.00'),
                                       metod='birbank', status='gozlemede', xarici_id='111')
        resp = self.client.get(f'/odenis/birbank/ugurlu/?odenis_id={odenis.pk}')
        self.assertEqual(resp.status_code, 404)

    @override_settings(BIRBANK_MERCHANT_ID='m', BIRBANK_MERCHANT_SECRET='s')
    def test_untrusted_gateway_redirect_blocked(self):
        evil = _Resp({'order': {'id': 1, 'hppUrl': 'https://evil.example', 'password': 'x'}})
        with patch('requests.post', return_value=evil):
            resp = self.client.post('/odenis/', {'metod': 'birbank', 'mebleg': '10'})
        self.assertEqual(resp.status_code, 200)
        self.assertEqual(Odenis.objects.get(istifadeci=self.user).status, 'legv_edildi')


@override_settings(SECURE_SSL_REDIRECT=False)
class RedirectAndHeaderTests(TestCase):
    def test_banner_click_has_no_open_redirect(self):
        banner = ReklamBanner.objects.create(movqe='ust', link='')
        resp = Client(HTTP_USER_AGENT='Mozilla/5.0').get(
            f'/banner/{banner.pk}/klik/', HTTP_REFERER='https://evil.example/phish')
        self.assertEqual(resp.status_code, 302)
        self.assertEqual(resp['Location'], '/')

    def test_javascript_banner_link_rejected(self):
        banner = ReklamBanner(movqe='sol', link='https://ok.example')
        banner.save()
        ReklamBanner.objects.filter(pk=banner.pk).update(link='javascript:alert(1)')
        resp = Client(HTTP_USER_AGENT='Mozilla/5.0').get(f'/banner/{banner.pk}/klik/')
        self.assertEqual(resp['Location'], '/')

    def test_security_headers_present(self):
        resp = Client().get('/giris/')
        self.assertEqual(resp['X-Frame-Options'], 'DENY')
        self.assertIn('camera=()', resp['Permissions-Policy'])
        self.assertIn('no-store', resp['Cache-Control'])

    def test_unix_socket_proxy_extracts_client_ip(self):
        from django.test import RequestFactory
        from .middleware import TrustedProxyMiddleware
        mw = TrustedProxyMiddleware(lambda request: None)
        req = RequestFactory().get('/', REMOTE_ADDR='', HTTP_X_FORWARDED_FOR='185.43.188.25')
        mw(req)
        self.assertEqual(req.META['REMOTE_ADDR'], '185.43.188.25')

