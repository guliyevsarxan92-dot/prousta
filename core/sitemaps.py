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
    changefreq = 'weekly'
    priority = 0.6

    def items(self):
        return Kategori.objects.filter(ust_kategori=None)

    def location(self, obj):
        return f'/elanlar/?kategori={obj.slug}'

class StatikSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.5

    def items(self):
        return ['index', 'elan_siyahi', 'giris', 'qeydiyyat']

    def location(self, item):
        return reverse(item)
