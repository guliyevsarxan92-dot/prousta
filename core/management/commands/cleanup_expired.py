from django.core.management.base import BaseCommand
from django.db.models import Q
from django.utils import timezone
from core.models import Elan, MobileLoginTicket


class Command(BaseCommand):
    help = 'Expire listing/VIP flags and remove consumed/expired login tickets. Schedule once per minute.'

    def handle(self, *args, **options):
        now = timezone.now()
        expired = Elan.objects.filter(status='aktiv', bitis_tarixi__lte=now).update(status='muddeti_bitmis')
        vip = Elan.objects.exclude(vip_status='normal').filter(
            Q(vip_bitis__lte=now) | Q(vip_bitis__isnull=True)).update(vip_status='normal', vip_siralama=0)
        tickets, _ = MobileLoginTicket.objects.filter(expires__lte=now).delete()
        self.stdout.write(f'Expired listings: {expired}; VIP: {vip}; tickets: {tickets}')
