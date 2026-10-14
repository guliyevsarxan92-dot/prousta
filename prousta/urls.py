from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from core.sitemaps import (
    AnaSehifeSitemap, KategoriSitemap, AltKategoriSitemap, StatikSitemap,
    ElanSitemap, ProblemSitemap, XidmetLokasiyaSitemap
)

sitemaps = {
    'ana_sehife': AnaSehifeSitemap,
    'kateqoriyalar': KategoriSitemap,
    'alt_kateqoriyalar': AltKategoriSitemap,
    'lokasiyalar': XidmetLokasiyaSitemap,
    'elanlar': ElanSitemap,
    'problemler': ProblemSitemap,
    'statik': StatikSitemap,
}
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.admin import admin_pending_notifications_api

urlpatterns = [
    path('admin/api/pending-notifications/', admin_pending_notifications_api, name='admin_pending_notifications'),
    path('admin/', admin.site.urls),
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),

    path('social-auth/', include('social_django.urls', namespace='social')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
