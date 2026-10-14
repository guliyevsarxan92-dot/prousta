from datetime import timedelta
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin, GroupAdmin as BaseGroupAdmin
from django.contrib.auth.models import User, Group
from django.db import models
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.admin.views.decorators import staff_member_required
from django.urls import path, reverse
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
    BannerKlik,
    VipPaket,
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


@staff_member_required
def admin_pending_notifications_api(request):
    """
    Admin panel üçün anlıq bildiriş API-si.
    Təsdiq gözləyən yeni elan və ödənişləri JSON olaraq qaytarır.
    """
    try:
        elan_gozlemede = Elan.objects.filter(status='gozlemede')
        elan_count = elan_gozlemede.count()
        latest_elan = elan_gozlemede.order_by('-id').first()
        elan_data = None
        if latest_elan:
            elan_data = {
                'id': latest_elan.id,
                'title': latest_elan.bashliq or 'Başlıqsız Elan',
                'user': latest_elan.istifadeci.username,
                'phone': latest_elan.telefon or '',
                'url': reverse('admin:core_elan_change', args=[latest_elan.id]),
            }

        odenis_gozlemede = Odenis.objects.filter(status='gozlemede')
        odenis_count = odenis_gozlemede.count()
        latest_odenis = odenis_gozlemede.order_by('-id').first()
        odenis_data = None
        if latest_odenis:
            odenis_data = {
                'id': latest_odenis.id,
                'amount': f"{latest_odenis.mebleg} AZN",
                'type': latest_odenis.get_nov_display(),
                'user': latest_odenis.istifadeci.username,
                'url': reverse('admin:core_odenis_change', args=[latest_odenis.id]),
            }

        return JsonResponse({
            'status': 'ok',
            'elan': {
                'count': elan_count,
                'latest': elan_data,
            },
            'odenis': {
                'count': odenis_count,
                'latest': odenis_data,
            }
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)



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
        total_banner_klik = ReklamBanner.objects.aggregate(s=models.Sum('klik_sayi'))['s'] or 0
        total_banner_baxis = ReklamBanner.objects.aggregate(s=models.Sum('baxis_sayi'))['s'] or 0
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
            'kpi_total_banner_klik': total_banner_klik,
            'kpi_total_banner_baxis': total_banner_baxis,
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


class ElanVipListFilter(admin.SimpleListFilter):
    title = 'VIP Statusu'
    parameter_name = 'vip'

    def lookups(self, request, model_admin):
        return (
            ('1', '⭐ VIP və Super VIP'),
            ('super_vip', '💎 Yalnız Super VIP'),
            ('vip', '⭐ Yalnız VIP'),
            ('normal', 'Normal'),
        )

    def queryset(self, request, queryset):
        if self.value() == '1':
            return queryset.filter(vip_status__in=['vip', 'super_vip'])
        if self.value() in ('super_vip', 'vip', 'normal'):
            return queryset.filter(vip_status=self.value())
        return queryset


@admin.register(Elan)
class ElanAdmin(ModelAdmin):
    change_list_template = "admin/core/elan/change_list.html"
    list_display = [
        'shekil_thumb',
        'nomre_link',
        'bashliq_display',
        'istifadeci_info',
        'kategori',
        'qiymet_display',
        'status_badge',
        'vip_badge',
        'statistika_display',
        'saytda_bax',
        'yaradildi_display',
    ]
    list_display_links = ['nomre_link', 'bashliq_display']
    list_filter = [
        ('status', ChoicesDropdownFilter),
        ElanVipListFilter,
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
        'zeng_sayi',
        'wp_sayi',
        'vip_siralama',
        'vip_yenilendi',
        'saytda_bax_btn',
    ]
    inlines = [ElanShekilInline]
    ordering = ['-vip_siralama', '-yaradildi']
    list_per_page = 25

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        say_gozlemede = Elan.objects.filter(status='gozlemede').count()
        say_aktiv = Elan.objects.filter(status='aktiv').count()
        say_vip = Elan.objects.filter(vip_status__in=['vip', 'super_vip']).count()
        say_muddeti_bitmis = Elan.objects.filter(status='muddeti_bitmis').count()
        say_deaktiv = Elan.objects.filter(status='deaktiv').count()
        say_hamisi = Elan.objects.count()

        cur_status = request.GET.get('status__exact', '')
        cur_vip = request.GET.get('vip', '')

        if cur_status == 'gozlemede':
            cur_tab = 'gozlemede'
        elif cur_status == 'aktiv':
            cur_tab = 'aktiv'
        elif cur_vip == '1':
            cur_tab = 'vip'
        elif cur_status == 'muddeti_bitmis':
            cur_tab = 'muddeti_bitmis'
        elif cur_status == 'deaktiv':
            cur_tab = 'deaktiv'
        else:
            cur_tab = 'hamisi'

        extra_context.update({
            'say_gozlemede': say_gozlemede,
            'say_aktiv': say_aktiv,
            'say_vip': say_vip,
            'say_muddeti_bitmis': say_muddeti_bitmis,
            'say_deaktiv': say_deaktiv,
            'say_hamisi': say_hamisi,
            'cur_tab': cur_tab,
        })
        return super().changelist_view(request, extra_context=extra_context)

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
                ('baxish_sayi', 'zeng_sayi', 'wp_sayi'),
                ('yaradildi', 'yenilendi'),
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
        'cixaris_action',
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

    @display(description='Statistika')
    def statistika_display(self, obj):
        return format_html(
            '<div style="font-size:11px;line-height:1.4" title="Baxış: {} | Zəng: {} | WhatsApp: {}">'
            '👁 <b>{}</b> <span class="text-slate-400">baxış</span><br>'
            '📞 <b>{}</b> <span class="text-slate-400">zəng</span> · '
            '💬 <b>{}</b> <span class="text-slate-400">wp</span>'
            '</div>',
            obj.baxish_sayi, obj.zeng_sayi, obj.wp_sayi,
            obj.baxish_sayi,
            obj.zeng_sayi,
            obj.wp_sayi,
        )

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

    @action(description='📤 Seçilmiş elanlardan Usta Nömrələrini Çıxar (Toplu Mesaj / CSV)')
    def cixaris_action(self, request, queryset):
        ids = ",".join(str(pk) for pk in queryset.values_list('pk', flat=True))
        url = reverse('admin:core_elan_cixaris') + f'?ids={ids}'
        return redirect(url)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('cixaris/', self.admin_site.admin_view(self.cixaris_view), name='core_elan_cixaris'),
        ]
        return custom_urls + urls

    def cixaris_view(self, request):
        import csv
        import re
        from django.http import HttpResponse

        def clean_az_phone(raw):
            if not raw:
                return None, None, None
            digits = re.sub(r'\D', '', str(raw))
            if not digits:
                return None, None, None
            if digits.startswith('994') and len(digits) == 12:
                return '0' + digits[3:], '+' + digits, digits
            if digits.startswith('0') and len(digits) == 10:
                return digits, '+994' + digits[1:], '994' + digits[1:]
            if len(digits) == 9 and digits[0] in ('1', '5', '7', '9'):
                return '0' + digits, '+994' + digits, '994' + digits
            if digits.startswith('994') and len(digits) >= 10:
                return '0' + digits[3:], '+' + digits, digits
            if digits.startswith('0') and len(digits) >= 9:
                return digits, '+994' + digits[1:], '994' + digits[1:]
            return '0' + digits, '+994' + digits, '994' + digits

        # URL Filters
        kat_id = request.GET.get('kategori', '').strip()
        sheher_filter = request.GET.get('sheher', '').strip()
        status_filter = request.GET.get('status', '').strip()
        q = request.GET.get('q', '').strip()
        ids_param = request.GET.get('ids', '').strip()
        is_export = request.GET.get('export', '') == 'csv'

        elan_qs = Elan.objects.select_related('istifadeci', 'istifadeci__profil', 'kategori')

        selected_ids = []
        if ids_param:
            try:
                selected_ids = [int(x) for x in ids_param.split(',') if x.strip().isdigit()]
                if selected_ids:
                    elan_qs = elan_qs.filter(pk__in=selected_ids)
            except Exception:
                pass

        if kat_id.isdigit():
            elan_qs = elan_qs.filter(models.Q(kategori_id=int(kat_id)) | models.Q(kategori__ust_kategori_id=int(kat_id)))

        if sheher_filter:
            elan_qs = elan_qs.filter(sheher__iexact=sheher_filter)

        if status_filter == 'aktiv':
            elan_qs = elan_qs.filter(status='aktiv')
        elif status_filter == 'vip':
            elan_qs = elan_qs.filter(vip_status__in=['vip', 'super_vip'])

        masters = {}

        for e in elan_qs:
            raw_phone = e.telefon or (hasattr(e.istifadeci, 'profil') and e.istifadeci.profil.telefon)
            local, intl, wa = clean_az_phone(raw_phone)
            if not local:
                continue

            if local not in masters:
                name = ''
                if hasattr(e.istifadeci, 'profil'):
                    p = e.istifadeci.profil
                    name = f'{p.ad} {p.soyad}'.strip()
                if not name:
                    name = e.istifadeci.get_full_name() or e.istifadeci.username

                masters[local] = {
                    'ad': name,
                    'username': e.istifadeci.username,
                    'user_id': e.istifadeci.id,
                    'local_phone': local,
                    'intl_phone': intl,
                    'wa_digits': wa,
                    'wa_link': f'https://wa.me/{wa}',
                    'categories': set(),
                    'cities': set(),
                    'elan_sayi': 0,
                    'has_active': False,
                    'has_vip': False,
                    'email': e.istifadeci.email or '',
                }

            m = masters[local]
            m['elan_sayi'] += 1
            if e.kategori:
                m['categories'].add(e.kategori.ad)
            if e.sheher:
                m['cities'].add(e.sheher)
            if e.status == 'aktiv':
                m['has_active'] = True
            if e.vip_status in ('vip', 'super_vip'):
                m['has_vip'] = True

        # If not filtering by specific elans or category, also include profiles with phone
        if not selected_ids and not kat_id:
            profil_qs = Profil.objects.exclude(telefon='').select_related('istifadeci')
            if sheher_filter:
                profil_qs = profil_qs.filter(sheher__iexact=sheher_filter)
            for p in profil_qs:
                local, intl, wa = clean_az_phone(p.telefon)
                if not local:
                    continue
                if local not in masters:
                    name = f'{p.ad} {p.soyad}'.strip() or p.istifadeci.get_full_name() or p.istifadeci.username
                    masters[local] = {
                        'ad': name,
                        'username': p.istifadeci.username,
                        'user_id': p.istifadeci.id,
                        'local_phone': local,
                        'intl_phone': intl,
                        'wa_digits': wa,
                        'wa_link': f'https://wa.me/{wa}',
                        'categories': set(),
                        'cities': {p.sheher} if p.sheher else set(),
                        'elan_sayi': 0,
                        'has_active': False,
                        'has_vip': False,
                        'email': p.istifadeci.email or '',
                    }

        # Search filter
        master_list = list(masters.values())
        if q:
            ql = q.lower()
            filtered = []
            for m in master_list:
                cat_str = " ".join(m['categories']).lower()
                city_str = " ".join(m['cities']).lower()
                if (ql in m['ad'].lower() or
                    ql in m['username'].lower() or
                    ql in m['local_phone'] or
                    ql in m['intl_phone'] or
                    ql in m['email'].lower() or
                    ql in cat_str or
                    ql in city_str):
                    filtered.append(m)
            master_list = filtered

        # Order by elan count desc, then name
        master_list.sort(key=lambda x: (-x['elan_sayi'], x['ad']))

        # CSV Export
        if is_export:
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            filename = f"prousta_ustalar_{timezone.now().strftime('%Y%m%d_%H%M')}.csv"
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            response.write('\ufeff')  # UTF-8 BOM for Microsoft Excel
            writer = csv.writer(response)
            writer.writerow([
                '№',
                'Usta / Ad Soyad',
                'İstifadəçi Adı',
                'Telefon (Yerli / SMS)',
                'Telefon (Beynəlxalq)',
                'WhatsApp Linki',
                'Xidmət Kateqoriyaları',
                'Şəhər',
                'Elan Sayı',
                'Aktiv Elanı Var?',
                'VIP Elanı Var?',
                'E-poçt'
            ])
            for i, m in enumerate(master_list, start=1):
                writer.writerow([
                    i,
                    m['ad'],
                    m['username'],
                    m['local_phone'],
                    m['intl_phone'],
                    m['wa_link'],
                    ", ".join(sorted(m['categories'])) if m['categories'] else '—',
                    ", ".join(sorted(m['cities'])) if m['cities'] else '—',
                    m['elan_sayi'],
                    'Bəli' if m['has_active'] else 'Xeyr',
                    'Bəli' if m['has_vip'] else 'Xeyr',
                    m['email']
                ])
            return response

        # Bulk copy formatted strings
        sms_vergul = ", ".join(m['local_phone'] for m in master_list if m['local_phone'])
        sms_setir = "\n".join(m['local_phone'] for m in master_list if m['local_phone'])
        intl_setir = "\n".join(m['intl_phone'] for m in master_list if m['intl_phone'])

        kateqoriyalar = Kategori.objects.all().order_by('ad')
        sheherler = sorted(list(set(Elan.objects.exclude(sheher='').values_list('sheher', flat=True).distinct())))

        total_masters = len(master_list)
        active_masters = sum(1 for m in master_list if m['has_active'])
        vip_masters = sum(1 for m in master_list if m['has_vip'])
        total_ads = sum(m['elan_sayi'] for m in master_list)

        context = {
            **self.admin_site.each_context(request),
            'title': 'Ustalar Bazası & Toplu Mesaj Çıxarışı',
            'master_list': master_list,
            'total_masters': total_masters,
            'active_masters': active_masters,
            'vip_masters': vip_masters,
            'total_ads': total_ads,
            'sms_vergul': sms_vergul,
            'sms_setir': sms_setir,
            'intl_setir': intl_setir,
            'kateqoriyalar': kateqoriyalar,
            'sheherler': sheherler,
            'kat_id': kat_id,
            'sheher_filter': sheher_filter,
            'status_filter': status_filter,
            'q': q,
            'ids_param': ids_param,
            'selected_ids_count': len(selected_ids),
        }
        return render(request, 'admin/ustalar_cixaris.html', context)


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
        with transaction.atomic():
            for odenis in queryset:
                if odenis.status != 'tesdiq_edildi':
                    odenis.status = 'tesdiq_edildi'
                    odenis.save()
                    count += 1
        self.message_user(request, f"{count} ödəniş uğurla təsdiqləndi.")

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
        'bashliq_qisa',
        'shekil_baxish',
        'klik_sayi_badge',
        'baxis_sayi_badge',
        'ctr_badge',
        'aktiv_badge',
        'link_preview',
        'hesabat_duymesi',
    ]
    list_editable = []
    list_filter = []
    search_fields = ['bashliq', 'link']
    actions = ['aktivlesdir_action', 'deaktivlesdir_action', 'statistikalari_sifirla']

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

    def klik_sayi_badge(self, obj):
        return format_html(
            '<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-extrabold bg-emerald-50 text-emerald-700 dark:bg-emerald-950/60 dark:text-emerald-400 border border-emerald-200 dark:border-emerald-800">'
            '👆 {}</span>',
            obj.klik_sayi
        )
    klik_sayi_badge.short_description = 'Kliklər'
    klik_sayi_badge.admin_order_field = 'klik_sayi'

    def baxis_sayi_badge(self, obj):
        return format_html(
            '<span class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-semibold bg-slate-100 text-slate-700 dark:bg-base-800 dark:text-base-300">'
            '👁️ {}</span>',
            obj.baxis_sayi
        )
    baxis_sayi_badge.short_description = 'Baxış'
    baxis_sayi_badge.admin_order_field = 'baxis_sayi'

    def ctr_badge(self, obj):
        val = obj.ctr
        cls = 'text-emerald-600 dark:text-emerald-400 font-extrabold' if val >= 1.0 else 'text-slate-500 font-medium'
        return format_html('<span class="text-xs {}">{}%</span>', cls, f"{val:.2f}")
    ctr_badge.short_description = 'CTR %'

    def hesabat_duymesi(self, obj):
        url = reverse('admin:reklambanner_hesabat', args=[obj.pk])
        return format_html(
            '<a href="{}" class="inline-flex items-center gap-1 px-2.5 py-1 rounded-lg bg-emerald-600 hover:bg-emerald-700 text-white text-xs font-bold shadow-xs transition-colors" style="background-color:#059669;color:#ffffff;">'
            '<span class="material-symbols-outlined text-sm">analytics</span>'
            'Hesabat</a>',
            url
        )
    hesabat_duymesi.short_description = 'Hesabat'

    def bashliq_qisa(self, obj):
        return obj.bashliq or format_html('<span class="text-slate-400 dark:text-base-500 italic">Başlıqsız</span>')
    bashliq_qisa.short_description = 'Başlıq'
    bashliq_qisa.admin_order_field = 'bashliq'

    def shekil_baxish(self, obj):
        if obj.video:
            return format_html(
                '<video src="{}" style="height:32px;max-width:54px;border-radius:4px;object-fit:cover;" autoplay muted loop></video>',
                obj.video.url
            )
        if obj.video_url:
            return format_html('<span class="text-xs font-bold text-sky-600">Video</span>')
        if obj.shekil:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="height:32px;max-width:54px;border-radius:4px;object-fit:cover;"/></a>',
                obj.shekil.url, obj.shekil.url
            )
        if obj.html_kod:
            return format_html('<span class="text-xs font-bold text-emerald-600">HTML</span>')
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

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('<int:banner_id>/hesabat/', self.admin_site.admin_view(self.hesabat_view), name='reklambanner_hesabat'),
        ]
        return custom_urls + urls

    def hesabat_view(self, request, banner_id):
        from django.shortcuts import get_object_or_404, render
        from django.http import HttpResponse
        from django.db.models.functions import TruncDate
        from django.db.models import Count
        import csv

        banner = get_object_or_404(ReklamBanner, pk=banner_id)
        now = timezone.now()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        last_30d = now - timedelta(days=30)

        klikler_qs = banner.klikler.all()

        if request.GET.get('export') == 'csv':
            response = HttpResponse(content_type='text/csv; charset=utf-8')
            response['Content-Disposition'] = f'attachment; filename="banner_{banner.id}_hesabat_{now.strftime("%Y%m%d")}.csv"'
            response.write('\ufeff'.encode('utf8'))
            writer = csv.writer(response)
            writer.writerow(['Banner', 'Mövqe', 'Tarix və Saat', 'Cihaz', 'IP Ünvanı', 'User-Agent', 'Referer'])
            for k in klikler_qs.order_by('-yaradildi')[:2000]:
                writer.writerow([
                    banner.bashliq or 'Başlıqsız',
                    banner.get_movqe_display(),
                    k.yaradildi.strftime('%d.%m.%Y %H:%M:%S'),
                    k.get_cihaz_display(),
                    k.ip_unvan or '',
                    k.user_agent,
                    k.referer or 'Birbaşa / Digər'
                ])
            return response

        total_klik = banner.klik_sayi
        total_baxis = banner.baxis_sayi
        ctr = banner.ctr

        klik_24h = klikler_qs.filter(yaradildi__gte=last_24h).count()
        klik_7d = klikler_qs.filter(yaradildi__gte=last_7d).count()
        klik_30d = klikler_qs.filter(yaradildi__gte=last_30d).count()

        mobil_sayi = klikler_qs.filter(cihaz='mobil').count()
        desktop_sayi = klikler_qs.filter(cihaz='desktop').count()
        planset_sayi = klikler_qs.filter(cihaz='planset').count()
        cemi_qeydli = mobil_sayi + desktop_sayi + planset_sayi or 1
        mobil_faiz = round((mobil_sayi / cemi_qeydli) * 100, 1)
        desktop_faiz = round((desktop_sayi / cemi_qeydli) * 100, 1)
        planset_faiz = round((planset_sayi / cemi_qeydli) * 100, 1)

        daily_stats = list(
            klikler_qs.filter(yaradildi__gte=now - timedelta(days=14))
            .annotate(gun=TruncDate('yaradildi'))
            .values('gun')
            .annotate(say=Count('id'))
            .order_by('-gun')
        )

        son_klikler = klikler_qs.order_by('-yaradildi')[:100]

        context = {
            **self.admin_site.each_context(request),
            'title': f'Reklam Hesabatı: {banner.bashliq or banner.get_movqe_display()}',
            'banner': banner,
            'total_klik': total_klik,
            'total_baxis': total_baxis,
            'ctr': ctr,
            'klik_24h': klik_24h,
            'klik_7d': klik_7d,
            'klik_30d': klik_30d,
            'mobil_sayi': mobil_sayi,
            'mobil_faiz': mobil_faiz,
            'desktop_sayi': desktop_sayi,
            'desktop_faiz': desktop_faiz,
            'planset_sayi': planset_sayi,
            'planset_faiz': planset_faiz,
            'daily_stats': daily_stats,
            'son_klikler': son_klikler,
            'now': now,
        }
        return render(request, 'admin/banner_hesabat.html', context)

    @action(description='✅ Seçilmiş bannerləri AKTİV et')
    def aktivlesdir_action(self, request, queryset):
        queryset.update(aktiv=True)
        self.message_user(request, "Bannerlər aktiv edildi.")

    @action(description='⏸️ Seçilmiş bannerləri DEAKTİV et')
    def deaktivlesdir_action(self, request, queryset):
        queryset.update(aktiv=False)
        self.message_user(request, "Bannerlər deaktiv edildi.")

    @action(description='🔄 Seçilmiş bannerlərin statistikalarını SIFIRLA')
    def statistikalari_sifirla(self, request, queryset):
        queryset.update(klik_sayi=0, baxis_sayi=0)
        for b in queryset:
            b.klikler.all().delete()
        self.message_user(request, "Seçilmiş bannerlərin klik və baxış statistikaları sıfırlandı.")


@admin.register(BannerKlik)
class BannerKlikAdmin(ModelAdmin):
    list_display = ['banner', 'cihaz_badge', 'ip_unvan', 'referer_qisa', 'yaradildi']
    list_filter = ['cihaz', 'banner', 'yaradildi']
    search_fields = ['ip_unvan', 'user_agent', 'referer', 'banner__bashliq']
    readonly_fields = ['banner', 'ip_unvan', 'cihaz', 'user_agent', 'referer', 'yaradildi']
    actions = ['export_csv']

    def has_add_permission(self, request):
        return False

    @display(
        description='Cihaz',
        label={
            'mobil': 'success',
            'desktop': 'info',
            'planset': 'warning',
            'diger': 'base',
        }
    )
    def cihaz_badge(self, obj):
        return obj.cihaz, obj.get_cihaz_display()

    def referer_qisa(self, obj):
        if obj.referer:
            return format_html(
                '<a href="{}" target="_blank" class="text-xs text-slate-500 dark:text-base-400 truncate max-w-[200px] inline-block hover:underline">{}</a>',
                obj.referer, obj.referer
            )
        return '—'
    referer_qisa.short_description = 'Mənbə (Referer)'

    @action(description='📥 Seçilmiş klikləri CSV formatında yüklə')
    def export_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        response = HttpResponse(content_type='text/csv; charset=utf-8')
        response['Content-Disposition'] = 'attachment; filename="banner_klik_qeydleri.csv"'
        response.write('\ufeff'.encode('utf8'))
        writer = csv.writer(response)
        writer.writerow(['Banner', 'Cihaz', 'IP Ünvanı', 'User-Agent', 'Referer', 'Tarix'])
        for k in queryset:
            writer.writerow([
                k.banner.bashliq or k.banner.get_movqe_display(),
                k.get_cihaz_display(),
                k.ip_unvan or '',
                k.user_agent,
                k.referer,
                k.yaradildi.strftime('%d.%m.%Y %H:%M:%S')
            ])
        return response


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


@admin.register(VipPaket)
class VipPaketAdmin(ModelAdmin):
    list_display = [
        'ad',
        'nov_badge',
        'qiymet_display',
        'muddet_display',
        'aktiv_badge',
        'siralama',
        'yenilendi_display',
    ]
    list_editable = ['siralama']
    list_filter = ['nov', 'aktiv']
    search_fields = ['ad', 'nov', 'ustunlukler']
    ordering = ['siralama', 'qiymet']

    fieldsets = (
        ('Paket Məlumatları', {
            'fields': (
                ('ad', 'nov'),
                ('qiymet', 'muddet_gun'),
                'ustunlukler',
            ),
            'description': 'Saytda istifadəçilərə təklif olunan VIP paketinin adı, qiyməti və aktivlik müddəti.',
        }),
        ('Status və Göstərilmə Sırası', {
            'fields': (
                ('aktiv', 'siralama'),
            ),
        }),
    )

    @display(description='Növ', label=True)
    def nov_badge(self, obj):
        color = 'warning' if obj.nov == 'vip' else 'success'
        return obj.get_nov_display(), color

    @display(description='Qiymət (AZN)')
    def qiymet_display(self, obj):
        return f"{obj.qiymet} ₼"

    @display(description='Müddət')
    def muddet_display(self, obj):
        return f"{obj.muddet_gun} gün"

    @display(description='Status', label=True)
    def aktiv_badge(self, obj):
        return ('Aktiv', 'success') if obj.aktiv else ('Deaktiv', 'danger')

    @display(description='Yeniləndi')
    def yenilendi_display(self, obj):
        return obj.yenilendi.strftime('%d.%m.%Y %H:%M') if obj.yenilendi else '—'


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
