import os
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import Kategori, Elan


TELEFON = '+994515888884'
SHEHER = 'Bakı'


def _acaqlama(ad: str) -> str:
    """Hər kateqoriya üçün uyğun açıqlama mətni."""
    ad_l = ad.lower()
    return (
        f"Peşəkar {ad_l} xidməti Bakıda və ətraf rayonlarda. "
        f"Çoxillik təcrübəli mütəxəssis komandası, keyfiyyətli iş, "
        f"münasib qiymətlər və zəmanətli xidmət təklif edirik.\n\n"
        f"✅ Pulsuz qiymətləndirmə\n"
        f"✅ Təcili çağırış (eyni gün)\n"
        f"✅ Keyfiyyətli material və orijinal hissələr\n"
        f"✅ Yazılı zəmanət\n"
        f"✅ Şəffaf qiymət siyasəti\n"
        f"✅ Bakının bütün rayonlarına xidmət\n\n"
        f"24/7 əlaqə üçün zəng edin və ya saytdan mesaj göndərin. "
        f"Sifarişiniz qısa müddətdə qəbul ediləcək və ən qısa zamanda "
        f"ünvanınıza usta yönləndiriləcək.\n\n"
        f"Prousta.az — Azərbaycanın etibarlı xidmət platforması."
    )


class Command(BaseCommand):
    help = 'Superadmin (ADMIN_USERNAME) profilində bütün alt-xidmətlər üzrə nümunə elanlar yaradır. Idempotentdir — mövcud elanları dublikatlamır.'

    def handle(self, *args, **options):
        username = os.environ.get('ADMIN_USERNAME')
        if not username:
            self.stdout.write(self.style.WARNING(
                'ADMIN_USERNAME təyin edilməyib — elanlar yaradılmadı.'
            ))
            return

        try:
            admin = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.WARNING(
                f'İstifadəçi "{username}" tapılmadı — əvvəlcə create_admin işlədin.'
            ))
            return

        kateqoriyalar = Kategori.objects.filter(ust_kategori__isnull=False)
        yaradilan = 0
        atlanilan = 0

        for kat in kateqoriyalar:
            # Idempotent: bu admin-in bu kateqoriyada elanı varsa atla
            if Elan.objects.filter(istifadeci=admin, kategori=kat).exists():
                atlanilan += 1
                continue

            elan = Elan.objects.create(
                istifadeci=admin,
                kategori=kat,
                bashliq=f'{kat.ad} — peşəkar xidmət Bakıda',
                acaqlama=_acaqlama(kat.ad),
                qiymet=None,
                sheher=SHEHER,
                telefon=TELEFON,
                status='aktiv',
                bitis_tarixi=timezone.now() + timedelta(days=365),
            )
            yaradilan += 1

        self.stdout.write(self.style.SUCCESS(
            f'Tamamlandı: {yaradilan} yeni elan yaradıldı, {atlanilan} mövcud (atlanıldı).'
        ))
