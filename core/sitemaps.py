from django.contrib.sitemaps import Sitemap
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone
from .models import Kategori, Elan, Problem
from .seo import indexable_kategori_ids


class AnaSehifeSitemap(Sitemap):
    """Əsas səhifə — ən yüksək prioritet."""
    changefreq = 'daily'
    priority = 1.0

    def items(self):
        return ['index']

    def location(self, item):
        return reverse(item)


class KategoriSitemap(Sitemap):
    """Əsas kateqoriyalar — yalnız məzmunlu və indekslənə bilən səhifələr."""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        valid_ids = indexable_kategori_ids()
        return Kategori.objects.filter(ust_kategori__isnull=True, pk__in=valid_ids).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])


class AltKategoriSitemap(Sitemap):
    """Alt xidmət kateqoriyaları — axtarış tələbatı yüksək olan xidmətlər."""
    changefreq = 'daily'
    priority = 0.9

    def items(self):
        valid_ids = indexable_kategori_ids()
        return Kategori.objects.filter(ust_kategori__isnull=False, pk__in=valid_ids).order_by('pk')

    def location(self, obj):
        return reverse('xidmet_detail', args=[obj.slug])


class ElanSitemap(Sitemap):
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
        ).order_by('-yenilendi')

    def lastmod(self, obj):
        return obj.yenilendi

    def location(self, obj):
        return obj.get_absolute_url()


class ProblemSitemap(Sitemap):
    """Məlumatlandırıcı bloq və problem həlli məqalələri."""
    changefreq = 'weekly'
    priority = 0.7

    def items(self):
        return Problem.objects.filter(aktiv=True).order_by('-yenilendi')

    def lastmod(self, obj):
        return obj.yenilendi

    def location(self, obj):
        return obj.get_absolute_url()


class StatikSitemap(Sitemap):
    """Statik köməkçi səhifələr."""
    changefreq = 'monthly'
    priority = 0.4

    def items(self):
        return ['elan_siyahi', 'haqqimizda', 'mobil_app', 'problemler_siyahi', 'gizlilik', 'istifade_sertleri']

    def location(self, item):
        return reverse(item)
