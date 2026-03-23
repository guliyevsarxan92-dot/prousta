from django.contrib import admin
from .models import Kategori, Elan, ElanShekil, Profil, Favorit

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ['ad', 'slug']
    prepopulated_fields = {'slug': ('ad',)}

@admin.register(Elan)
class ElanAdmin(admin.ModelAdmin):
    list_display = ['bashliq', 'istifadeci', 'kategori', 'qiymet', 'status', 'yaradildi']
    list_filter = ['status', 'kategori', 'veziyyet']
    search_fields = ['bashliq', 'acaqlama']
    list_editable = ['status']

@admin.register(ElanShekil)
class ElanShekilAdmin(admin.ModelAdmin):
    list_display = ['elan', 'əsas']

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['istifadeci', 'telefon', 'sheher']

@admin.register(Favorit)
class FavoritAdmin(admin.ModelAdmin):
    list_display = ['istifadeci', 'elan', 'yaradildi']
