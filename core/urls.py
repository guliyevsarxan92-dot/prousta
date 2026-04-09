from django.urls import path, re_path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('qeydiyyat/', views.qeydiyyat, name='qeydiyyat'),
    path('giris/', views.giris, name='giris'),
    path('cixis/', views.cixis, name='cixis'),
    path('sifre-unutdum/', views.sifre_unutdum, name='sifre_unutdum'),
    path('elanlar/', views.elan_siyahi, name='elan_siyahi'),
    path('xidmet/<slug:slug>/', views.xidmet_detail, name='xidmet_detail'),
    path('elan/yeni/', views.elan_yarat, name='elan_yarat'),
    re_path(r'^elan/(?P<pk>\d+)-(?P<slug>[a-z0-9-]+)/$', views.elan_detail, name='elan_detail'),
    path('elan/<int:pk>/', views.elan_detail),  # legacy → 301 redirect
    path('elan/<int:pk>/duzelis/', views.elan_duzelis, name='elan_duzelis'),
    path('elan/<int:pk>/sil/', views.elan_sil, name='elan_sil'),
    path('elan/<int:pk>/aktivlesdir/', views.elan_aktivlesdir, name='elan_aktivlesdir'),
    path('profil/', views.profil, name='profil'),
    path('profil/foto/', views.profil_foto, name='profil_foto'),
    path('profil/foto/crop/', views.profil_foto_crop, name='profil_foto_crop'),
    path('profil/duzelis/', views.profil_duzelis, name='profil_duzelis'),
    path('istifadeci/<int:pk>/', views.istifadeci_profil, name='istifadeci_profil'),
    path('favorit/<int:pk>/', views.favorit_toggle, name='favorit_toggle'),
    path('mesajlar/', views.mesajlar, name='mesajlar'),
    path('mesaj/<int:pk>/', views.mesaj_oxu, name='mesaj_oxu'),
    path('mesaj/yeni/<int:elan_pk>/', views.mesaj_yeni, name='mesaj_yeni'),
    path('vip/<int:pk>/', views.vip_et, name='vip_et'),
    path('odenis/', views.odenis, name='odenis'),
    path('odenis/tesdiq/<int:pk>/', views.odenis_tesdiq, name='odenis_tesdiq'),
    path('robots.txt', views.robots_txt, name='robots_txt'),
    path('gizlilik/', views.gizlilik, name='gizlilik'),
    path('istifade-sertleri/', views.istifade_sertleri, name='istifade_sertleri'),
    path('haqqimizda/', views.haqqimizda, name='haqqimizda'),
]
