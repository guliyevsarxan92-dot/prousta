"""Real row-lock tests. SQLite cannot validate these guarantees."""
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest import skipUnless

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import connection, close_old_connections
from django.test import TransactionTestCase

from .models import Elan, Kategori, Odenis, Profil
from .payments import buy_vip
from .listings import create_listing
from .test_remediation import photo


@skipUnless(connection.vendor == 'postgresql', 'Requires isolated PostgreSQL row locks')
class PaymentConcurrencyTests(TransactionTestCase):
    def setUp(self):
        self.user = User.objects.create_user('concurrent-user')
        self.category = Kategori.objects.create(ad='Concurrent service', slug='concurrent-service')
        self.ad = Elan.objects.create(istifadeci=self.user, kategori=self.category, bashliq='Service',
                                     acaqlama='Service description', status='aktiv')
        Profil.objects.filter(istifadeci=self.user).update(balans=20)

    def parallel(self, operation):
        barrier = Barrier(2)
        def worker():
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                return operation()
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as executor:
            return list(executor.map(lambda _: worker(), range(2)))

    def test_parallel_approval_credits_only_once(self):
        payment = Odenis.objects.create(istifadeci=self.user, nov='balans', mebleg=10)
        def approve():
            row = Odenis.objects.get(pk=payment.pk)
            row.status = 'tesdiq_edildi'
            row.save()
        self.parallel(approve)
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 30)

    def test_parallel_vip_charges_only_once(self):
        def purchase():
            try:
                buy_vip(User.objects.get(pk=self.user.pk), self.ad.pk, 'vip')
                return True
            except ValidationError:
                return False
        self.assertEqual(sorted(self.parallel(purchase)), [False, True])
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 17)
        self.assertEqual(Odenis.objects.count(), 1)

    def test_parallel_paid_listings_cannot_overdraw(self):
        for i in range(3):
            category = Kategori.objects.create(ad=f'Existing {i}', slug=f'existing-{i}')
            Elan.objects.create(istifadeci=self.user, kategori=category, bashliq='Existing service',
                                acaqlama='Existing service description', status='aktiv')
        candidates = [Kategori.objects.create(ad=f'New {i}', slug=f'new-{i}').pk for i in range(2)]
        Profil.objects.filter(istifadeci=self.user).update(balans=1)
        barrier = Barrier(2)
        def create(index):
            close_old_connections()
            try:
                barrier.wait(timeout=10)
                create_listing(User.objects.get(pk=self.user.pk), {
                    'kategori': candidates[index], 'bashliq': 'Yeni xidmət elanı',
                    'acaqlama': 'Peşəkar təmir və texniki xidmət', 'telefon': '0501234567',
                }, [photo()])
                return True
            except ValidationError:
                return False
            finally:
                close_old_connections()
        with ThreadPoolExecutor(max_workers=2) as executor:
            self.assertEqual(sorted(executor.map(create, range(2))), [False, True])
        self.assertEqual(Profil.objects.get(istifadeci=self.user).balans, 0)
        self.assertEqual(Elan.objects.filter(istifadeci=self.user).count(), 5)
