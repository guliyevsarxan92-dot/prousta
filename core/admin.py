from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.html import format_html
from django.utils.safestring import mark_safe

from unfold.admin import ModelAdmin, TabularInline, StackedInline
from unfold.contrib.filters.admin import ChoicesDropdownFilter, RelatedDropdownFilter
from unfold.decorators import display, action
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

from social_django.models import UserSocialAuth, Nonce, Association

from .models import (
    Kategori,
    Elan,
    ElanShekil,
    Profil,
    Favorit,
    Mesaj,
    Odenis,
    BankMelumat,
    Problem,
    ReklamBanner,
)


# ==============================================================================
# Dynamic Navigation Badges & Dashboard Callback
# ==============================================================================

def badge_elan_gozlemede(request):
    """Sidebar menyuda təsdiq gözləyən elanların sayını göstərir."""
    try:
        count = Elan.objects.filter(status='gozlemede').count()
        return str(count) if count > 0 else None
    except Exception:
        return None


def badge_odenis_gozlemede(request):
    """Sidebar menyuda təsdiq gözləyən ödənişlərin sayını göstərir."""
    try:
        count = Odenis.objects.filter(status='gozlemede').count()
        return str(count) if count > 0 else None
    except Exception:
        return None


def dashboard_callback(request, context):
    """Əsas səhifədə (Dashboard) göstəriləcək statistikalar və bildirişlər."""
    try:
        now = timezone.now()
        thirty_days_ago = now - timedelta(days=30)

        # Elan statistikaları
        total_elan = Elan.objects.count()
        gozlemede_elan = Elan.objects.filter(status='gozlemede').count()
        aktiv_elan = Elan.objects.filter(status='aktiv').count()
        vip_elan = Elan.objects.filter(vip_status__in=['vip', 'super_vip']).count()

        # Ödəniş statistikaları
        gozlemede_odenis = Odenis.objects.filter(status='gozlemede').count()
        tesdiq_odenis_sayi = Odenis.objects.filter(status='tesdiq_edildi').count()
        odenis_mebleg_sum = Odenis.objects.filter(
            status='tesdiq_edildi',
            yaradildi__gte=thirty_days_ago
        ).aggregate(sum=models.Sum('mebleg'))['sum'] or 0

        # İstifadəçi və Banner statistikaları
        total_user = User.objects.count()
        total_profil = Profil.objects.count()
        aktiv_banner = ReklamBanner.objects.filter(aktiv=True).count()
        total_kategori = Kategori.objects.count()

        # Son gözləmədə olan elanlar (Dashboard-da birbaşa baxmaq və təsdiq etmək üçün)
        son_gozlemede_elanlar = Elan.objects.filter(
            status='gozlemede'
        ).select_related('istifadeci', 'kategori').prefetch_related('shekillar')[:6]

        # Son gözləmədə olan ödənişlər
        son_gozlemede_odenisler = Odenis.objects.filter(
            status='gozlemede'
        ).select_related('istifadeci', 'elan')[:6]

        context.update({
            'kpi_total_elan': total_elan,
            'kpi_gozlemede_elan': gozlemede_elan,
            'kpi_aktiv_elan': aktiv_elan,
            'kpi_vip_elan': vip_elan,
            'kpi_gozlemede_odenis': gozlemede_odenis,
            'kpi_tesdiq_odenis_sayi': tesdiq_odenis_sayi,
            'kpi_odenis_mebleg_sum': f"{odenis_mebleg_sum:.2f}",
            'kpi_total_user': total_user,
            'kpi_total_profil': total_profil,
            'kpi_aktiv_banner': aktiv_banner,
            'kpi_total_kategori': total_kategori,
            'son_gozlemede_elanlar': son_gozlemede_elanlar,
            'son_gozlemede_odenisler': son_gozlemede_odenisler,
        })
    except Exception:
        pass
    return context


# ==============================================================================
# Kateqoriya İdarəetməsi
# ==============================================================================

@admin.register(Kategori)
class KategoriAdmin(ModelAdmin):
    list_display = ['ad', 'slug', 'ust_kategori', 'elan_sayi_link']
    search_fields = ['ad', 'slug']
    list_filter = [('ust_kategori', RelatedDropdownFilter)]
    list_per_page = 25
    ordering = ['ad']

    def elan_sayi_link(self, obj):
        count = obj.elan_set.count()
        url = reverse('admin:core_elan_changelist') + f'?kategori__id__exact={obj.id}'
        return format_html(
            '<a href="{}" class="font-bold text-primary-600 hover:underline">{} elan ↗</a>',
            url, count
        )
    elan_sayi_link.short_description = 'Elan Sayı'


# ==============================================================================
# Elan və Şəkil İdarəetməsi
# ==============================================================================

class ElanShekilInline(TabularInline):
    model = ElanShekil
    extra = 1
    fields = ['shekil', 'shekil_preview', 'esas']
    readonly_fields = ['shekil_preview']

    def shekil_preview(self, obj):
        if obj and obj.shekil:
            return format_html(
                '<a href="{}" target="_blank" title="Böyüt">'
                '<img src="{}" style="height:50px;width:70px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0;"/>'
                '</a>',
                obj.shekil.url, obj.shekil.url
            )
        return '—'
    shekil_preview.short_description = 'Önbaxış'


@admin.register(Elan)
class ElanAdmin(ModelAdmin):
    list_display = [
        'shekil_thumb',
        'nomre_link',
        'bashliq_display',
        'istifadeci_info',
        'kategori',
        'qiymet_display',
        'status_badge',
        'vip_badge',
        'saytda_bax',
        'yaradildi_display',
    ]
    list_display_links = ['nomre_link', 'bashliq_display']
    list_filter = [
        ('status', ChoicesDropdownFilter),
        ('vip_status', ChoicesDropdownFilter),
        ('kategori', RelatedDropdownFilter),
        'sheher',
        'yaradildi',
    ]
    search_fields = [
        'nomre',
        'bashliq',
        'istifadeci__username',
        'istifadeci__email',
        'telefon',
        'sheher',
    ]
    readonly_fields = [
        'nomre',
        'yaradildi',
        'yenilendi',
        'baxish_sayi',
        'vip_siralama',
        'vip_yenilendi',
        'saytda_bax_btn',
    ]
    inlines = [ElanShekilInline]
    ordering = ['-vip_siralama', '-yaradildi']
    list_per_page = 25

    fieldsets = (
        ('Əsas Məlumatlar', {
            'fields': (
                ('nomre', 'saytda_bax_btn'),
                'bashliq',
                ('kategori', 'istifadeci'),
                ('qiymet', 'sheher', 'telefon'),
            )
        }),
        ('Açıqlama Mətni', {
            'fields': ('acaqlama',),
        }),
        ('Status və Vaxt Tənzimləmələri', {
            'fields': (
                ('status', 'bitis_tarixi'),
            )
        }),
        ('VIP Parametrləri', {
            'fields': (
                ('vip_status', 'vip_bitis'),
                ('vip_siralama', 'vip_yenilendi'),
            ),
            'classes': ('collapse',),
        }),
        ('Statistika və Tarixçə', {
            'fields': (
                ('baxish_sayi', 'yaradildi', 'yenilendi'),
            ),
            'classes': ('collapse',),
        }),
    )

    actions = [
        'tesdiq_et_action',
        'deaktiv_et_action',
        'vip_10_gun_action',
        'super_vip_30_gun_action',
        'vip_legv_action',
    ]

    def shekil_thumb(self, obj):
        first_img = obj.shekillar.filter(esas=True).first() or obj.shekillar.first()
        if first_img and first_img.shekil:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="height:44px;width:58px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0;"/>'
                '</a>',
                first_img.shekil.url, first_img.shekil.url
            )
        return format_html(
            '<div style="height:44px;width:58px;background:#f1f5f9;border-radius:6px;display:flex;align-items:center;justify-content:center;color:#94a3b8;font-size:11px;">Yoxdur</div>'
        )
    shekil_thumb.short_description = 'Şəkil'

    def nomre_link(self, obj):
        return format_html('<span class="font-mono font-bold text-primary-600">#{}</span>', obj.nomre)
    nomre_link.short_description = 'Nömrə'

    def bashliq_display(self, obj):
        title = obj.bashliq or 'Başlıqsız'
        truncated = (title[:42] + '...') if len(title) > 42 else title
        return format_html('<span title="{}"><strong>{}</strong></span>', title, truncated)
    bashliq_display.short_description = 'Başlıq'

    def istifadeci_info(self, obj):
        u = obj.istifadeci
        url = reverse('admin:auth_user_change', args=[u.pk])
        return format_html(
            '<a href="{}" class="font-medium text-slate-800 dark:text-slate-200 hover:text-primary-600">{}</a>',
            url, u.username
        )
    istifadeci_info.short_description = 'İstifadəçi'

    def qiymet_display(self, obj):
        if obj.qiymet is not None:
            return format_html('<strong>{} ₼</strong>', obj.qiymet)
        return '—'
    qiymet_display.short_description = 'Qiymət'

    @display(
        description='Status',
        label={
            'aktiv': 'success',
            'gozlemede': 'warning',
            'deaktiv': 'danger',
            'muddeti_bitmis': 'base',
        }
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    @display(
        description='VIP',
        label={
            'super_vip': 'primary',
            'vip': 'info',
            'normal': 'base',
        }
    )
    def vip_badge(self, obj):
        return obj.vip_status, obj.get_vip_status_display()

    def saytda_bax(self, obj):
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" class="inline-flex items-center px-2 py-1 text-xs font-semibold rounded bg-slate-100 hover:bg-primary-50 text-slate-700 hover:text-primary-700 dark:bg-base-800 dark:text-base-300" title="Saytda bax">'
            'Bax ↗'
            '</a>',
            url
        )
    saytda_bax.short_description = 'Sayt'

    def saytda_bax_btn(self, obj):
        if obj.pk:
            return format_html(
                '<a href="{}" target="_blank" class="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-default bg-primary-600 text-white font-medium text-xs hover:bg-primary-700">'
                '🌐 Saytda Gör ↗'
                '</a>',
                obj.get_absolute_url()
            )
        return '—'
    saytda_bax_btn.short_description = 'Saytda Baxış'

    def yaradildi_display(self, obj):
        return obj.yaradildi.strftime('%d.%m.%Y %H:%M')
    yaradildi_display.short_description = 'Tarix'

    # Toplu əməliyyatlar
    @action(description='✅ Seçilmiş elanları TƏSDİQLƏ (Aktiv et)')
    def tesdiq_et_action(self, request, queryset):
        now = timezone.now()
        count = 0
        for elan in queryset:
            elan.status = 'aktiv'
            if not elan.bitis_tarixi or elan.bitis_tarixi <= now:
                elan.bitis_tarixi = now + timedelta(days=30)
            elan.save()
            count += 1
        self.message_user(request, f"{count} elan uğurla aktiv edildi.")

    @action(description='⏸️ Seçilmiş elanları DEAKTİV et')
    def deaktiv_et_action(self, request, queryset):
        count = queryset.update(status='deaktiv')
        self.message_user(request, f"{count} elan deaktiv edildi.")

    @action(description='⭐ 10 Günlük VIP et')
    def vip_10_gun_action(self, request, queryset):
        now = timezone.now()
        count = 0
        for elan in queryset:
            elan.vip_status = 'vip'
            elan.vip_bitis = now + timedelta(days=10)
            elan.vip_yenilendi = now
            elan.vip_siralama = 1
            elan.save()
            count += 1
        self.message_user(request, f"{count} elan 10 günlük VIP edildi.")

    @action(description='💎 30 Günlük SUPER VIP et')
    def super_vip_30_gun_action(self, request, queryset):
        now = timezone.now()
        count = 0
        for elan in queryset:
            elan.vip_status = 'super_vip'
            elan.vip_bitis = now + timedelta(days=30)
            elan.vip_yenilendi = now
            elan.vip_siralama = 2
            elan.save()
            count += 1
        self.message_user(request, f"{count} elan 30 günlük Super VIP edildi.")

    @action(description='🔄 VIP statusu ləğv et (Normal et)')
    def vip_legv_action(self, request, queryset):
        count = queryset.update(vip_status='normal', vip_siralama=0, vip_bitis=None)
        self.message_user(request, f"{count} elanın VIP statusu ləğv edildi.")


# ==============================================================================
# Ödənişlər İdarəetməsi
# ==============================================================================

@admin.register(Odenis)
class OdenisAdmin(ModelAdmin):
    list_display = [
        'istifadeci_link',
        'nov_badge',
        'mebleg_display',
        'status_badge',
        'elan_link',
        'qebz_goruntu',
        'yaradildi_display',
    ]
    list_filter = [
        ('status', ChoicesDropdownFilter),
        ('nov', ChoicesDropdownFilter),
        'yaradildi',
    ]
    search_fields = [
        'istifadeci__username',
        'istifadeci__email',
        'elan__nomre',
        'elan__bashliq',
        'qeyd',
    ]
    readonly_fields = ['qebz_goruntu_large', 'yaradildi']
    ordering = ['-yaradildi']
    list_per_page = 25

    actions = ['tesdiq_et_action', 'legv_et_action']

    def istifadeci_link(self, obj):
        u = obj.istifadeci
        url = reverse('admin:auth_user_change', args=[u.pk])
        profil = getattr(u, 'profil', None)
        tel = f" ({profil.telefon})" if profil and profil.telefon else ""
        return format_html(
            '<a href="{}" class="font-bold text-slate-800 dark:text-slate-100 hover:text-primary-600">{}{}</a>',
            url, u.username, tel
        )
    istifadeci_link.short_description = 'İstifadəçi'

    @display(
        description='Növ',
        label={
            'balans': 'success',
            'vip': 'info',
            'super_vip': 'primary',
        }
    )
    def nov_badge(self, obj):
        return obj.nov, obj.get_nov_display()

    def mebleg_display(self, obj):
        return format_html('<span class="font-bold text-slate-900 dark:text-white">{} ₼</span>', obj.mebleg)
    mebleg_display.short_description = 'Məbləğ'

    @display(
        description='Status',
        label={
            'tesdiq_edildi': 'success',
            'gozlemede': 'warning',
            'legv_edildi': 'danger',
        }
    )
    def status_badge(self, obj):
        return obj.status, obj.get_status_display()

    def elan_link(self, obj):
        if obj.elan:
            url = reverse('admin:core_elan_change', args=[obj.elan.pk])
            return format_html(
                '<a href="{}" class="text-xs font-semibold text-primary-600 hover:underline">#{} {}</a>',
                url, obj.elan.nomre, (obj.elan.bashliq[:25] + '...') if len(obj.elan.bashliq) > 25 else obj.elan.bashliq
            )
        return '—'
    elan_link.short_description = 'Əlaqəli Elan'

    def qebz_goruntu(self, obj):
        if obj.qebz:
            return format_html(
                '<a href="{}" target="_blank" title="Tam ölçüdə bax">'
                '<img src="{}" style="height:50px;width:70px;object-fit:cover;border-radius:6px;border:1px solid #e2e8f0;"/>'
                '</a>',
                obj.qebz.url, obj.qebz.url
            )
        return '—'
    qebz_goruntu.short_description = 'Qəbz'

    def qebz_goruntu_large(self, obj):
        if obj.qebz:
            return format_html(
                '<a href="{}" target="_blank">'
                '<img src="{}" style="max-height:350px;border-radius:8px;border:1px solid #cbd5e1;box-shadow:0 4px 12px rgba(0,0,0,0.08);"/>'
                '</a>',
                obj.qebz.url, obj.qebz.url
            )
        return 'Qəbz şəkli yüklənməyib'
    qebz_goruntu_large.short_description = 'Qəbz Şəkli'

    def yaradildi_display(self, obj):
        return obj.yaradildi.strftime('%d.%m.%Y %H:%M')
    yaradildi_display.short_description = 'Tarix'

    @action(description='✅ Seçilmiş ödənişləri TƏSDİQLƏ (Balans/VIP aktiv et)')
    def tesdiq_et_action(self, request, queryset):
        count = 0
        for odenis in queryset:
            if odenis.status != 'tesdiq_edildi':
                odenis.status = 'tesdiq_edildi'
                odenis.save()  # pre_save balansı artırır, post_save bildiriş mesajı göndərir
                if odenis.elan and odenis.nov in ('vip', 'super_vip'):
                    now = timezone.now()
                    days = 30 if odenis.nov == 'super_vip' else 10
                    odenis.elan.vip_status = odenis.nov
                    odenis.elan.vip_bitis = now + timedelta(days=days)
                    odenis.elan.vip_yenilendi = now
                    odenis.elan.vip_siralama = 2 if odenis.nov == 'super_vip' else 1
                    odenis.elan.save()
                count += 1
        self.message_user(request, f"{count} ödəniş təsdiqləndi və xidmətlər aktiv edildi.")

    @action(description='❌ Seçilmiş ödənişləri LƏĞV ET')
    def legv_et_action(self, request, queryset):
        count = queryset.update(status='legv_edildi')
        self.message_user(request, f"{count} ödəniş ləğv edildi.")


# ==============================================================================
# İstifadəçi və Profil İdarəetməsi
# ==============================================================================

class ProfilInline(StackedInline):
    model = Profil
    can_delete = False
    fk_name = 'istifadeci'
    fields = (('ad', 'soyad'), ('telefon', 'sheher'), ('balans', 'avatar'))
    extra = 0


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class CustomUserAdmin(BaseUserAdmin, ModelAdmin):
    form = UserChangeForm
    add_form = UserCreationForm
    change_password_form = AdminPasswordChangeForm
    inlines = [ProfilInline]

    list_display = [
        'username',
        'email',
        'get_full_name_custom',
        'get_telefon',
        'get_balans',
        'is_staff',
        'is_active',
        'date_joined',
    ]
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
        'profil__ad',
        'profil__soyad',
        'profil__telefon',
    ]
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'date_joined']
    ordering = ['-date_joined']

    def get_full_name_custom(self, obj):
        profil = getattr(obj, 'profil', None)
        ad = (profil.ad if profil and profil.ad else obj.first_name) or ''
        soyad = (profil.soyad if profil and profil.soyad else obj.last_name) or ''
        tam = f"{ad} {soyad}".strip()
        return tam or '—'
    get_full_name_custom.short_description = 'Ad Soyad'

    def get_telefon(self, obj):
        profil = getattr(obj, 'profil', None)
        return profil.telefon if profil and profil.telefon else '—'
    get_telefon.short_description = 'Telefon'

    def get_balans(self, obj):
        profil = getattr(obj, 'profil', None)
        if profil:
            return format_html('<strong>{} ₼</strong>', profil.balans)
        return '0 ₼'
    get_balans.short_description = 'Balans'


@admin.register(Group)
class CustomGroupAdmin(BaseGroupAdmin, ModelAdmin):
    search_fields = ['name']


@admin.register(Profil)
class ProfilAdmin(ModelAdmin):
    list_display = [
        'avatar_preview',
        'istifadeci_link',
        'tam_ad',
        'telefon',
        'sheher',
        'balans_display',
        'elanlar_link',
        'yaradildi_display',
    ]
    search_fields = [
        'istifadeci__username',
        'istifadeci__email',
        'ad',
        'soyad',
        'telefon',
        'sheher',
    ]
    list_filter = ['sheher']
    readonly_fields = ['avatar_preview_large', 'yaradildi']
    ordering = ['-yaradildi']
    list_per_page = 25

    def avatar_preview(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:36px;width:36px;border-radius:50%;object-fit:cover;border:1px solid #e2e8f0;"/>',
                obj.avatar.url
            )
        return format_html(
            '<div style="height:36px;width:36px;border-radius:50%;background:#e2e8f0;display:flex;align-items:center;justify-content:center;font-weight:700;color:#64748b;font-size:12px;">{}</div>',
            (obj.istifadeci.username[:1].upper() if obj.istifadeci else '?')
        )
    avatar_preview.short_description = 'Avatar'

    def avatar_preview_large(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="height:120px;width:120px;border-radius:12px;object-fit:cover;border:1px solid #cbd5e1;"/>',
                obj.avatar.url
            )
        return 'Avatar yüklənməyib'
    avatar_preview_large.short_description = 'Avatar'

    def istifadeci_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.istifadeci.pk])
        return format_html(
            '<a href="{}" class="font-bold text-slate-800 dark:text-slate-100 hover:text-primary-600">{}</a>',
            url, obj.istifadeci.username
        )
    istifadeci_link.short_description = 'İstifadəçi'

    def tam_ad(self, obj):
        ad_soyad = f"{obj.ad} {obj.soyad}".strip()
        return ad_soyad or '—'
    tam_ad.short_description = 'Ad Soyad'

    def balans_display(self, obj):
        return format_html('<span class="font-bold text-slate-900 dark:text-white">{} ₼</span>', obj.balans)
    balans_display.short_description = 'Balans'

    def elanlar_link(self, obj):
        count = obj.istifadeci.elanlar.count()
        url = reverse('admin:core_elan_changelist') + f'?istifadeci__id__exact={obj.istifadeci.pk}'
        return format_html(
            '<a href="{}" class="font-semibold text-primary-600 hover:underline">{} elan ↗</a>',
            url, count
        )
    elanlar_link.short_description = 'Elanları'

    def yaradildi_display(self, obj):
        return obj.yaradildi.strftime('%d.%m.%Y')
    yaradildi_display.short_description = 'Qeydiyyat'


# ==============================================================================
# Reklam Bannerləri
# ==============================================================================

@admin.register(ReklamBanner)
class ReklamBannerAdmin(ModelAdmin):
    list_display = [
        'movqe_badge',
        'bashliq',
        'shekil_baxish',
        'animasiya_effekti',
        'aktiv_badge',
        'bos_olduqda_gizlet_badge',
        'link_preview',
        'bitis_tarixi',
        'yenilendi',
    ]
    list_editable = []
    list_filter = ['movqe', 'aktiv', 'bos_olduqda_gizlet', 'animasiya_effekti']
    search_fields = ['bashliq', 'link']
    actions = ['aktivlesdir_action', 'deaktivlesdir_action']

    @display(
        description='Mövqe',
        label={
            'ust': 'primary',
            'sol': 'info',
            'sag': 'info',
            'orta': 'warning',
        }
    )
    def movqe_badge(self, obj):
        return obj.movqe, obj.get_movqe_display()

    @display(
        description='Aktiv',
        label={
            True: 'success',
            False: 'danger',
        }
    )
    def aktiv_badge(self, obj):
        return obj.aktiv, ('Aktiv' if obj.aktiv else 'Deaktiv')

    @display(
        description='Boşdursa Gizlət',
        label={
            True: 'info',
            False: 'base',
        }
    )
    def bos_olduqda_gizlet_badge(self, obj):
        return obj.bos_olduqda_gizlet, ('Bəli' if obj.bos_olduqda_gizlet else 'Xeyr')

    def shekil_baxish(self, obj):
        if obj.video:
            return format_html(
                '<video src="{}" style="height:44px;max-width:80px;border-radius:4px;object-fit:cover;" autoplay muted loop></video>',
                obj.video.url
            )
        if obj.video_url:
            return format_html('<span class="text-xs font-bold text-sky-600">Video Link</span>')
        if obj.shekil:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="height:44px;max-width:80px;border-radius:4px;object-fit:cover;"/></a>',
                obj.shekil.url, obj.shekil.url
            )
        if obj.html_kod:
            return format_html('<span class="text-xs font-bold text-emerald-600">HTML Kod</span>')
        return '—'
    shekil_baxish.short_description = 'Media'

    def link_preview(self, obj):
        if obj.link:
            return format_html(
                '<a href="{}" target="_blank" class="text-xs text-primary-600 truncate max-w-[120px] inline-block hover:underline">Keçid ↗</a>',
                obj.link
            )
        return '—'
    link_preview.short_description = 'Link'

    @action(description='✅ Seçilmiş bannerləri AKTİV et')
    def aktivlesdir_action(self, request, queryset):
        queryset.update(aktiv=True)
        self.message_user(request, "Bannerlər aktiv edildi.")

    @action(description='⏸️ Seçilmiş bannerləri DEAKTİV et')
    def deaktivlesdir_action(self, request, queryset):
        queryset.update(aktiv=False)
        self.message_user(request, "Bannerlər deaktiv edildi.")


# ==============================================================================
# Bank Məlumatları
# ==============================================================================

@admin.register(BankMelumat)
class BankMelumatAdmin(ModelAdmin):
    list_display = ['bank_adi', 'kart_nomresi', 'kart_sahibi', 'aktiv_badge']
    list_filter = ['aktiv']
    search_fields = ['bank_adi', 'kart_nomresi', 'kart_sahibi']

    @display(
        description='Status',
        label={
            True: 'success',
            False: 'danger',
        }
    )
    def aktiv_badge(self, obj):
        return obj.aktiv, ('Aktiv' if obj.aktiv else 'Deaktiv')


# ==============================================================================
# Problemlər (Bloq / FAQ Məqalələri)
# ==============================================================================

@admin.register(Problem)
class ProblemAdmin(ModelAdmin):
    list_display = ['bashliq', 'kategori', 'aktiv_badge', 'saytda_bax', 'yaradildi']
    list_filter = [
        'aktiv',
        ('kategori', RelatedDropdownFilter),
    ]
    prepopulated_fields = {'slug': ('bashliq',)}
    search_fields = ['bashliq', 'metn']
    ordering = ['-yaradildi']

    @display(
        description='Status',
        label={
            True: 'success',
            False: 'danger',
        }
    )
    def aktiv_badge(self, obj):
        return obj.aktiv, ('Aktiv' if obj.aktiv else 'Deaktiv')

    def saytda_bax(self, obj):
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" class="text-xs font-semibold text-primary-600 hover:underline">Saytda bax ↗</a>',
            url
        )
    saytda_bax.short_description = 'Keçid'


# ==============================================================================
# Mesajlar və Favoritlər
# ==============================================================================

@admin.register(Mesaj)
class MesajAdmin(ModelAdmin):
    list_display = ['gonderici_link', 'alici_link', 'elan_link', 'metn_qisa', 'oxundu_badge', 'yaradildi']
    list_filter = ['oxundu', 'yaradildi']
    search_fields = ['gonderici__username', 'alici__username', 'metn', 'elan__nomre']
    ordering = ['-yaradildi']
    list_per_page = 25

    def gonderici_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.gonderici.pk])
        return format_html('<a href="{}" class="font-medium hover:underline">{}</a>', url, obj.gonderici.username)
    gonderici_link.short_description = 'Göndərən'

    def alici_link(self, obj):
        url = reverse('admin:auth_user_change', args=[obj.alici.pk])
        return format_html('<a href="{}" class="font-medium hover:underline">{}</a>', url, obj.alici.username)
    alici_link.short_description = 'Alan'

    def elan_link(self, obj):
        if obj.elan:
            url = reverse('admin:core_elan_change', args=[obj.elan.pk])
            return format_html('<a href="{}" class="text-xs font-semibold text-primary-600 hover:underline">#{}</a>', url, obj.elan.nomre)
        return '—'
    elan_link.short_description = 'Elan'

    def metn_qisa(self, obj):
        m = obj.metn or ''
        return (m[:50] + '...') if len(m) > 50 else m
    metn_qisa.short_description = 'Mətn'

    @display(
        description='Oxunma',
        label={
            True: 'success',
            False: 'warning',
        }
    )
    def oxundu_badge(self, obj):
        return obj.oxundu, ('Oxunub' if obj.oxundu else 'Oxunmayıb')


@admin.register(Favorit)
class FavoritAdmin(ModelAdmin):
    list_display = ['istifadeci', 'elan', 'yaradildi']
    search_fields = ['istifadeci__username', 'elan__nomre', 'elan__bashliq']
    ordering = ['-yaradildi']
    list_per_page = 25


# ==============================================================================
# Daxili Sosial Giriş Modellərinin İdarəsi
# ==============================================================================

admin.site.unregister(UserSocialAuth)
admin.site.unregister(Nonce)
admin.site.unregister(Association)

@admin.register(UserSocialAuth)
class CustomSocialAuthAdmin(ModelAdmin):
    list_display = ['user', 'provider', 'uid']
    list_filter = ['provider']
    search_fields = ['user__username', 'uid']
    ordering = ['-id']
