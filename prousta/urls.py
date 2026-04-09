from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import KategoriSitemap, AltKategoriSitemap, StatikSitemap

sitemaps = {
    'kateqoriyalar': KategoriSitemap,
    'alt_kateqoriyalar': AltKategoriSitemap,
    'statik': StatikSitemap,
}
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
