"""
Birbank (Kapital Bank) E-Commerce Payment Gateway Integration.
Dəstəklənən mühitlər:
- Test: https://precheckout.kapitalbank.az/api
- Production: https://checkout.kapitalbank.az/api
"""
import base64
import logging
from decimal import Decimal
import requests
from django.conf import settings
from django.urls import reverse

logger = logging.getLogger(__name__)


class BirbankGateway:
    @property
    def env(self):
        return getattr(settings, 'BIRBANK_ENV', 'test').lower()

    @property
    def merchant_id(self):
        return getattr(settings, 'BIRBANK_MERCHANT_ID', '').strip()

    @property
    def merchant_secret(self):
        return getattr(settings, 'BIRBANK_MERCHANT_SECRET', '').strip()

    @property
    def test_url(self):
        return getattr(settings, 'BIRBANK_TEST_URL', 'https://precheckout.kapitalbank.az/api').rstrip('/')

    @property
    def prod_url(self):
        return getattr(settings, 'BIRBANK_PROD_URL', 'https://checkout.kapitalbank.az/api').rstrip('/')

    @property
    def base_url(self):
        return self.prod_url if self.env == 'prod' else self.test_url

    @property
    def is_configured(self):
        return bool(self.merchant_id and self.merchant_secret)

    @property
    def simulator_allowed(self):
        """Simulyasiya (pulsuz təsdiq) yalnız lokal DEBUG mühitində mümkündür."""
        return bool(getattr(settings, 'DEBUG', False)) and not self.is_configured

    def _get_auth_header(self):
        token = f"{self.merchant_id}:{self.merchant_secret}".encode('utf-8')
        encoded = base64.b64encode(token).decode('ascii')
        return {
            'Authorization': f'Basic {encoded}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def create_order(self, odenis_id, amount, description, success_url, fail_url, cancel_url=None):
        """
        Kapital Bank / Birbank Checkout API üzərindən ödəniş sifarişi yaradır.
        Əgər API açarları təyin edilməyibsə, təhlükəsiz simulyasiya/sınaq rejimində işləyir.
        """
        amount_decimal = Decimal(str(amount)).quantize(Decimal('0.01'))
        cancel_url = cancel_url or fail_url

        if not self.is_configured:
            if not self.simulator_allowed:
                logger.error("Birbank konfiqurasiya edilməyib; production-da simulyasiya qadağandır.")
                return {'success': False, 'error': 'Onlayn ödəniş hazırda əlçatan deyil.'}
            logger.info("Birbank konfiqurasiyası tapılmadı. Simulyasiya rejimi aktivləşdirilir.")
            simulated_id = f"SIM-{odenis_id}-{int(amount_decimal * 100)}"
            sim_url = reverse('birbank_simulator') + f"?odenis_id={odenis_id}&amount={amount_decimal}"
            return {
                'success': True,
                'order_id': simulated_id,
                'redirect_url': sim_url,
                'is_simulated': True,
            }

        endpoint = f"{self.base_url}/order"
        payload = {
            "order": {
                "typeRid": "Order_SMS",
                "amount": str(amount_decimal),
                "currency": "AZN",
                "language": "AZ",
                "description": description or f"Prousta.az Balans artirma #{odenis_id}",
                "hppUrl": success_url,
                "cancelUrl": cancel_url,
                "declineUrl": fail_url
            }
        }

        try:
            response = requests.post(
                endpoint,
                json=payload,
                headers=self._get_auth_header(),
                timeout=15
            )
            data = response.json() if response.content else {}
            if response.status_code in (200, 201):
                order_data = data.get('order') or data
                order_id = order_data.get('id')
                hpp_url = order_data.get('hppUrl', '').rstrip('/')
                password = order_data.get('password')

                if order_id and hpp_url and password:
                    redirect_url = f"{hpp_url}/flex?id={order_id}&password={password}"
                elif order_data.get('redirectUrl'):
                    redirect_url = order_data.get('redirectUrl')
                else:
                    redirect_url = hpp_url

                return {
                    'success': True,
                    'order_id': str(order_id),
                    'redirect_url': redirect_url,
                    'raw': data,
                    'is_simulated': False,
                }
            else:
                err_msg = data.get('message') or data.get('error') or f"Status: {response.status_code}"
                logger.error("Birbank create_order xətası: status=%s message=%s", response.status_code, err_msg)
                return {
                    'success': False,
                    'error': 'Bank ödəniş sifarişini qəbul etmədi.',
                }
        except Exception:
            logger.exception("Birbank create_order bağlantı xətası")
            return {
                'success': False,
                'error': 'Bank ilə əlaqə qurulmadı.'
            }

    def check_order_status(self, order_id):
        """
        Sifarişin statusunu Kapital Bank API-dən yoxlayır.
        """
        if not order_id:
            return {'verified': False, 'status': 'Unknown'}

        if str(order_id).startswith('SIM-'):
            if not self.simulator_allowed:
                logger.warning("Production-da simulyasiya sifarişi rədd edildi: %s", order_id)
                return {'verified': False, 'status': 'SimulatorDisabled'}
            return {
                'verified': True,
                'status': 'FullyPaid',
                'is_simulated': True,
            }

        if not self.is_configured:
            return {'verified': False, 'status': 'NotConfigured'}

        endpoint = f"{self.base_url}/order/{order_id}"
        try:
            response = requests.get(
                endpoint,
                headers=self._get_auth_header(),
                timeout=12
            )
            data = response.json() if response.content else {}
            if response.status_code == 200:
                order_data = data.get('order') or data
                status_val = str(order_data.get('status', '')).strip()
                # Kapital Bank statusları: FullyPaid, Approved, APPROVED
                is_success = status_val.lower() in ('fullypaid', 'approved', 'success')
                return {
                    'verified': is_success,
                    'status': status_val,
                    'amount': order_data.get('amount'),
                    'currency': order_data.get('currency'),
                    'raw': data
                }
            return {
                'verified': False,
                'status': f"HTTP_{response.status_code}",
                'raw': data
            }
        except Exception:
            logger.exception("Birbank check_order_status xətası")
            return {
                'verified': False,
                'status': 'GatewayError'
            }


birbank_gateway = BirbankGateway()
