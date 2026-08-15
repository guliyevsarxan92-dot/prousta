from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from .models import Kategori, Elan, Problem


class ElanSitemap(Sitemap):
    """Aktiv və müddəti bitməmiş elanlar üçün sitemap."""
    changefreq = 'daily'
    priority = 0.6
    limit = 5000

    def items(self):
        now = timezone.now()
        return Elan.objects.filter(
            status='aktiv'
        ).filter(
            Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=now)
        ).order_by('-yenilendi')

    def lastmod(self, obj):
        return obj.yenilendi

    def location(self, obj):
        return obj.get_absolute_url()


class KategoriSitemap(Sitemap):
    """Əsas kateqoriyalar — SEO mətni olan və ya aktiv elanları olan."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Kategori.objects.filter(ust_kategori__isnull=True).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])


class AltKategoriSitemap(Sitemap):
    """Alt xidmət kateqoriyaları — hamısı sitemap-a daxildir."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Kategori.objects.filter(ust_kategori__isnull=False).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])

class ProblemSitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Problem.objects.filter(aktiv=True).order_by('-yenilendi')

    def lastmod(self, obj):
        return obj.yenilendi

    def location(self, obj):
        return obj.get_absolute_url()


class StatikSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['index', 'elan_siyahi', 'haqqimizda', 'mobil_app', 'problemler_siyahi', 'gizlilik', 'istifade_sertleri']

    def location(self, item):
        return reverse(item)
