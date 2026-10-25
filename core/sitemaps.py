from django.contrib.sitemaps import Sitemap
from django.db.models import Q, Max
from django.urls import reverse
from django.utils import timezone
from .models import Kategori, Elan, Problem
from .seo import indexable_kategori_ids


class PublicSitemap(Sitemap):
    protocol = 'https'

    def get_urls(self, page=1, site=None, protocol=None):
        from types import SimpleNamespace
        # Technical/staging hosts must never leak into a submitted sitemap.
        return super().get_urls(page=page, site=SimpleNamespace(domain='prousta.az'), protocol='https')


class AnaSehifeSitemap(PublicSitemap):
    """Əsas səhifə — ən yüksək prioritet."""
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)


class KategoriSitemap(PublicSitemap):
    """Əsas kateqoriyalar — yalnız məzmunlu və indekslənə bilən səhifələr."""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        valid_ids = indexable_kategori_ids()
        return Kategori.objects.filter(ust_kategori__isnull=True, pk__in=valid_ids).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])


class AltKategoriSitemap(PublicSitemap):
    """Alt xidmət kateqoriyaları — axtarış tələbatı yüksək olan xidmətlər."""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        valid_ids = indexable_kategori_ids()
        return Kategori.objects.filter(ust_kategori__isnull=False, pk__in=valid_ids).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])


class ElanSitemap(PublicSitemap):
    """Aktiv və müddəti bitməmiş elanlar."""
    changefreq = 'daily'
    priority = 0.8
    limit = 5000

    def items(self):
        now = timezone.now()
        return Elan.objects.filter(
            status='aktiv'
        ).filter(
            Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=now)
        ).order_by('-yenilendi', '-pk').prefetch_related('shekillar')

    def lastmod(self, obj):
        return obj.yenilendi

    def get_latest_lastmod(self):
        return self.items().aggregate(latest=Max('yenilendi'))['latest']

    def get_urls(self, page=1, site=None, protocol=None):
        from .seo_metadata import absolute_url
        urls = super().get_urls(page=page, site=site, protocol=protocol)
        for item in urls:
            item['images'] = [absolute_url(photo.shekil.url)
                              for photo in item['item'].shekillar.all() if photo.shekil][:5]
        return urls

    def location(self, obj):
        return obj.get_absolute_url()


class ProblemSitemap(PublicSitemap):
    """Məlumatlandırıcı bloq və problem həlli məqalələri."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Problem.objects.filter(aktiv=True).order_by('-yenilendi')

    def lastmod(self, obj):
        return obj.yenilendi

    def get_latest_lastmod(self):
        return self.items().aggregate(latest=Max('yenilendi'))['latest']

    def location(self, obj):
        return obj.get_absolute_url()


from .locations import LOKASIYALAR


class XidmetLokasiyaSitemap(PublicSitemap):
    """
    Bakı və Abşeron rayonları üzrə lokal xidmət səhifələri (/xidmet/<slug>/<lokasiya>/).
    Lokal SEO və Google axtarışları üçün yüksək dəyərli açar söz səhifələri.
    """
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        from .seo_locations import indexable_location_pairs
        return indexable_location_pairs()

    def location(self, item):
        return reverse('xidmet_lokasiya_detail', args=[item[0], item[1]])


class StatikSitemap(PublicSitemap):
    """Statik köməkçi səhifələr."""
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return ['elan_siyahi', 'haqqimizda', 'mobil_app', 'problemler_siyahi', 'gizlilik', 'istifade_sertleri']

    def location(self, item):
        return reverse(item)
