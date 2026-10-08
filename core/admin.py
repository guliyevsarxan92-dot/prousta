from django.contrib import admin
from django.utils.html import format_html
from .models import Kategori, Elan, ElanShekil, Profil, Favorit, Mesaj, Odenis, BankMelumat, Problem, ReklamBanner

@admin.register(Kategori)
class KategoriAdmin(admin.ModelAdmin):
    list_display = ['ad', 'slug', 'ust_kategori']
    # prepopulated_fields silindi — Azərbaycan hərfləri (İ, Ə, Ş...) ilə
    # Django-nun avtomatik slugify funksiyası non-ASCII simvol yaradır və URL
    # reverse-ini sındırır. Slug əl ilə ASCII olaraq daxil edilməlidir.

@admin.register(Elan)
class ElanAdmin(admin.ModelAdmin):
    list_display = ['nomre_link', 'istifadeci', 'kategori', 'status', 'vip_status', 'vip_bitis']
    list_filter = ['status', 'vip_status', 'kategori']
    list_editable = ['status', 'vip_status']
    readonly_fields = ['nomre', 'yaradildi', 'baxish_sayi', 'vip_siralama', 'vip_yenilendi']
    ordering = ['-vip_siralama', '-yaradildi']
    list_per_page = 20

    def nomre_link(self, obj):
        return format_html('<strong>#{}</strong>', obj.nomre)
    nomre_link.short_description = 'Nömrə'

@admin.register(ElanShekil)
class ElanShekilAdmin(admin.ModelAdmin):
    list_display = ['elan', 'esas']

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ['istifadeci', 'ad', 'soyad', 'telefon', 'sheher', 'balans']

@admin.register(Favorit)
class FavoritAdmin(admin.ModelAdmin):
    list_display = ['istifadeci', 'elan', 'yaradildi']

@admin.register(Mesaj)
class MesajAdmin(admin.ModelAdmin):
    list_display = ['gonderici', 'alici', 'elan', 'oxundu', 'yaradildi']

@admin.register(Odenis)
class OdenisAdmin(admin.ModelAdmin):
    list_display = ['istifadeci', 'nov', 'mebleg', 'status', 'qebz_goruntu', 'yaradildi']
    list_editable = ['status']
    list_filter = ['nov']
    readonly_fields = ['qebz_goruntu', 'yaradildi']

    def get_queryset(self, request):
        # Admin panelində yalnız gözləmədə olan ödəniş sorğuları görünsün.
        # Təsdiqlənmiş və ya ləğv edilmiş ödənişlər (VIP alışları və s.) siyahıdan gizlənir.
        return super().get_queryset(request).filter(status='gozlemede')

    def qebz_goruntu(self, obj):
        if obj.qebz:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="height:60px;border-radius:6px"/></a>',
                obj.qebz.url, obj.qebz.url
            )
        return '—'
    qebz_goruntu.short_description = 'Qəbz'

@admin.register(Problem)
class ProblemAdmin(admin.ModelAdmin):
    list_display = ['bashliq', 'kategori', 'aktiv', 'yaradildi']
    list_filter = ['aktiv', 'kategori']
    list_editable = ['aktiv']
    prepopulated_fields = {'slug': ('bashliq',)}
    search_fields = ['bashliq']
    ordering = ['-yaradildi']

@admin.register(BankMelumat)
class BankMelumatAdmin(admin.ModelAdmin):
    list_display = ['bank_adi', 'kart_nomresi', 'kart_sahibi', 'aktiv']
    list_editable = ['aktiv']

# Auth
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group

admin.site.unregister(User)
admin.site.unregister(Group)

class CustomUserAdmin(UserAdmin):
    search_fields = []
    def get_search_fields(self, request):
        return []

class CustomGroupAdmin(GroupAdmin):
    search_fields = []
    def get_search_fields(self, request):
        return []

admin.site.register(User, CustomUserAdmin)
admin.site.register(Group, CustomGroupAdmin)

# Social Auth
from social_django.admin import UserSocialAuthOption, NonceOption, AssociationOption
from social_django.models import UserSocialAuth, Nonce, Association

admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)

class CustomSocialAuthAdmin(UserSocialAuthOption):
    search_fields = []
    list_display = ['user', 'provider', 'uid']
    list_filter = ['provider']
    ordering = ['-id']
    def get_search_fields(self, request):
        return []

class CustomNonceAdmin(NonceOption):
    search_fields = []
    def get_search_fields(self, request):
        return []

class CustomAssociationAdmin(AssociationOption):
    search_fields = []
    def get_search_fields(self, request):
        return []

admin.site.register(UserSocialAuth, CustomSocialAuthAdmin)
admin.site.register(Nonce, CustomNonceAdmin)
admin.site.register(Association, CustomAssociationAdmin)


@admin.register(ReklamBanner)
class ReklamBannerAdmin(admin.ModelAdmin):
    list_display = ['movqe', 'bashliq', 'shekil_baxish', 'animasiya_effekti', 'link', 'aktiv', 'bitis_tarixi', 'yenilendi']
    list_editable = ['aktiv']
    list_filter = ['movqe', 'aktiv', 'animasiya_effekti']
    search_fields = ['bashliq', 'link']

    def shekil_baxish(self, obj):
        if obj.video:
            return format_html('<video src="{}" style="height:45px;max-width:80px;border-radius:4px;object-fit:cover;" autoplay muted loop></video>', obj.video.url)
        if obj.video_url:
            return format_html('<span style="font-size:11px;color:#0284c7;font-weight:700;">Video URL</span>')
        if obj.shekil:
            return format_html('<img src="{}" style="height:45px;max-width:80px;border-radius:4px;object-fit:cover;"/>', obj.shekil.url)
        if obj.html_kod:
            return format_html('<span style="font-size:11px;color:#007b52;font-weight:700;">HTML/Animasiya</span>')
        return '—'
    shekil_baxish.short_description = 'Görüntü / Video'

