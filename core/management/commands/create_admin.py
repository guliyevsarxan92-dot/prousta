import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User


class Command(BaseCommand):
    help = 'ADMIN_USERNAME / ADMIN_EMAIL / ADMIN_PASSWORD env dəyişənlərindən superuser yaradır və ya şifrəsini yeniləyir. Idempotent — dəfələrlə işlədilə bilər.'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        email = os.environ.get('ADMIN_EMAIL', '')
        password = os.environ.get('ADMIN_PASSWORD')

        if not username or not password:
            self.stdout.write(self.style.WARNING(
                'ADMIN_USERNAME və ya ADMIN_PASSWORD təyin edilməyib — superuser yaradılmadı.'
            ))
            return

        user, created = User.objects.get_or_create(
            username=username,
            defaults={'email': email, 'is_staff': True, 'is_superuser': True},
        )
        user.email = email or user.email
        user.is_staff = True
        user.is_superuser = True
        user.set_password(password)
        user.save()

        if created:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" yaradıldı.'))
        else:
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" yeniləndi (şifrə dəyişdirildi).'))
