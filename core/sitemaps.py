from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from .models import Elan, Kategori

class ElanSitemap(Sitemap):
    changefreq = 'daily'
    priority = 0.8

    def items(self):
        return Elan.objects.filter(status='aktiv')

    def location(self, obj):
        return f'/elan/{obj.pk}/'

    def lastmod(self, obj):
        return obj.yenilendi

class KategoriSitemap(Sitemap):
    """Əsas kateqoriyalar (10 ədəd) üçün sitemap."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Kategori.objects.filter(ust_kategori__isnull=True).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])


class AltKategoriSitemap(Sitemap):
    """Alt xidmət kateqoriyaları (120+ ədəd) üçün sitemap — hər xidmət ayrı URL."""
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Kategori.objects.filter(ust_kategori__isnull=False).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])

class StatikSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['index', 'elan_siyahi', 'giris', 'qeydiyyat']

    def location(self, item):
        return reverse(item)
