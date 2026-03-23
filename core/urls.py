from django.urls import path
from . import views

urlpatterns = [
    # Ana səhifə
    path('', views.index, name='index'),

    # Qeydiyyat / Giriş / Çıxış
    path('qeydiyyat/', views.qeydiyyat, name='qeydiyyat'),
    path('giris/', views.giris, name='giris'),
    path('cixis/', views.cixis, name='cixis'),

    # Elanlar
    path('elanlar/', views.elan_siyahi, name='elan_siyahi'),
    path('elan/<int:pk>/', views.elan_detail, name='elan_detail'),
    path('elan/yeni/', views.elan_yarat, name='elan_yarat'),
    path('elan/<int:pk>/sil/', views.elan_sil, name='elan_sil'),

    # Profil
    path('profil/', views.profil, name='profil'),

    # Favorit
    path('favorit/<int:pk>/', views.favorit_toggle, name='favorit_toggle'),
]
