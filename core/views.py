from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F, TextField, Value, Min, Max, Sum
from django.db.models.functions import MD5, Cast, Concat
from django.db import connection, transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse, Http404, HttpResponseRedirect
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt
import random
import secrets
import re
from urllib.parse import urlsplit
from datetime import timedelta
from decimal import Decimal
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import (
    Elan, Kategori, ElanShekil, Profil, Favorit, Mesaj, Odenis, BankMelumat,
    Problem, VipPaket, ReklamBanner, BannerKlik, Bloklama, SilinmisElan
)
from .seo import indexable_kategori_ids
from .seo_locations import areas_expression, in_location, location_counts
from .search import search_listings
from .watermark import filigran_yoxla
from .rotation import apply_fair_rotation
from .validation import image_upload, listing_values, money, phone, text
from .listings import create_listing, update_listing, visible_listings, check_access, check_messaging, check_duplicate, reactivate_listing, is_public, replacement_url
from .payments import buy_vip, bump_listing
from .birbank import birbank_gateway
from django.core.exceptions import ValidationError, PermissionDenied
from django.contrib.auth.password_validation import validate_password
from .locations import BAKI_RAYONLARI, LOKASIYALAR, POPULAR_LOKASIYALAR, get_lokasiya, grouped_lokasiyalar

from .content import description_error as _aciqlama_qadaga_yoxla


BOT_PATTERNS = re.compile(
    r'(bot|crawl|spider|slurp|facebookexternalhit|meta-externalagent|bytespider|googlebot|'
    r'bingbot|yandex|duckduckbot|baiduspider|twitterbot|linkedinbot|embedly|quora|'
    r'pinterest|ahrefs|semrush|petalbot|curl|wget|python-requests|urllib|scrapy|postman|'
    r'headlesschrome|phantomjs|chatgpt|claudebot|gptbot)',
    re.IGNORECASE
)

def _is_bot(request) -> bool:
    ua = request.META.get('HTTP_USER_AGENT', '')
    if not ua or BOT_PATTERNS.search(ua):
        return True
    return False

def _get_client_ip(request):
    return request.META.get('REMOTE_ADDR')


# Birbank ödəniş səhifəsinə yalnız rəsmi Kapital Bank domenlərinə yönləndirməyə icazə verilir.
_BIRBANK_HOSTS = {'checkout.kapitalbank.az', 'precheckout.kapitalbank.az',
                  'pg.kapitalbank.az', 'e-commerce.kapitalbank.az', 'txpg.kapitalbank.az',
                  'tstpg.kapitalbank.az'}


def _update_elan_status():
    if not cache.get('elan_status_update'):
        cache.set('elan_status_update', True, 60)
        now = timezone.now()
        Elan.objects.filter(status='aktiv', bitis_tarixi__lt=now).update(status='muddeti_bitmis')
        Elan.objects.filter(
            vip_status__in=['vip', 'super_vip']
        ).filter(
            Q(vip_bitis__lte=now) | Q(vip_bitis__isnull=True)
        ).update(vip_status='normal', vip_siralama=0)
        Elan.objects.filter(vip_status='normal', vip_siralama__gt=0).update(vip_siralama=0)
        Elan.objects.filter(vip_status__in=['vip', 'super_vip']).exclude(vip_siralama=1).update(vip_siralama=1)


def get_or_create_listing_seed(request, session_key='elan_seed'):
    """
    Ədalətli rotasiya üçün seed təyin edir:
    - URL-dəki ?seed= prioriteti var (səhifələmə və AJAX üçün ardıcıllığı qoruyur).
    - Səhifələmə (page > 1) və ya AJAX sorğusunda mövcud sessiya seed-i saxlanılır.
    - Səhifə 1-in təzə açılışında və ya yenilənməsində (F5) yeni təsadüfi seed generasiya olunur,
      beləliklə daimi eyni elanlar üstdə qalmır, bütün elanlar bərabər göstərim şansı qazanır.
    """
    if _is_bot(request):
        return 'crawler'

    param_seed = request.GET.get('seed', '').strip()
    if param_seed and re.match(r'^[a-zA-Z0-9_\-]+$', param_seed):
        if hasattr(request, 'session'):
            request.session[session_key] = param_seed
        return param_seed

    is_paging = bool(request.GET.get('page') and request.GET.get('page') != '1')
    is_ajax = bool(request.GET.get('ajax') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest')

    if is_paging or is_ajax:
        if hasattr(request, 'session'):
            existing = request.session.get(session_key)
            if existing:
                return existing

    new_seed = secrets.token_hex(4)
    if hasattr(request, 'session'):
        request.session[session_key] = new_seed
    return new_seed




def strict_page(paginator, number):
    try:
        return paginator.page(number)
    except (EmptyPage, PageNotAnInteger):
        raise Http404('Səhifə tapılmadı.')


def index(request, lang='az'):
    _update_elan_status()
    is_ru = (lang == 'ru')
    seed = get_or_create_listing_seed(request, session_key='home_elan_seed')

    # Bütün aktiv elanlar: Super VIP və VIP ən öndə, sonra normal elanlar (ədalətli rotasiya ilə)
    elanlar_qs = (
        visible_listings(request.user)
        .select_related('kategori', 'istifadeci__profil')
        .prefetch_related('shekillar')
    )
    elanlar_qs = apply_fair_rotation(elanlar_qs, seed)

    paginator = Paginator(elanlar_qs, 20)
    page_number = request.GET.get('page', 1)
    elanlar = strict_page(paginator, page_number)

    # AJAX: sonsuz sürüşdürmə (infinite scroll) və ya "Daha çox göstər" üçün
    if request.GET.get('ajax') == '1' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        from django.template.loader import render_to_string
        cards_html = render_to_string('partials/elan_cards_list.html', {'elanlar': elanlar, 'user': getattr(request, 'user', None), 'is_ru': is_ru}, request=request)
        return JsonResponse({
            'html': cards_html,
            'has_next': elanlar.has_next(),
            'next_page': elanlar.next_page_number() if elanlar.has_next() else None,
            'current_page': elanlar.number,
            'num_pages': elanlar.paginator.num_pages,
            'total_count': elanlar.paginator.count,
        })

    page_range = list(paginator.get_elided_page_range(elanlar.number, on_each_side=2, on_ends=1))

    # Kateqoriyalar bloku üçün
    kateqoriyalar = list(
        Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    )

    from .homepage import presentation_context
    from .ru_content import HOME_CATEGORIES_RU
    pres = presentation_context(list(elanlar)[:6])
    if is_ru:
        pres['home_categories'] = HOME_CATEGORIES_RU
    template_name = 'ru/index.html' if is_ru else 'index.html'
    return render(request, template_name, {
        'is_ru': is_ru,
        'elanlar': elanlar,
        'page_range': page_range,
        'kateqoriyalar': kateqoriyalar,
        'next_page_number': elanlar.next_page_number() if elanlar.has_next() else '',
        'elan_seed': seed,
        **pres,
    })


def elan_siyahi(request, lang='az'):
    """
    /elanlar/ və /ru/elanlar/ — əsas xidmət seçimi səhifəsi.
    """
    _update_elan_status()
    is_ru = (lang == 'ru')

    # Köhnə URL-ləri yeni xidmət səhifəsinə 301 redirect et (SEO backward compat)
    kategori_slug = request.GET.get('kategori', '').strip()
    if kategori_slug:
        target_name = 'ru_xidmet_detail' if is_ru else 'xidmet_detail'
        return redirect(target_name, slug=kategori_slug, permanent=True)

    seed = get_or_create_listing_seed(request, session_key='siyahi_elan_seed')
    kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    axtaris = request.GET.get('q', '').strip()

    elanlar = (
        visible_listings(request.user)
        .select_related('kategori', 'istifadeci__profil')
        .prefetch_related('shekillar')
    )
    elanlar = search_listings(elanlar, axtaris)
    elanlar = apply_fair_rotation(elanlar, seed)

    paginator = Paginator(elanlar, 20)
    elanlar_page = strict_page(paginator, request.GET.get('page', 1))
    page_range = list(paginator.get_elided_page_range(elanlar_page.number, on_each_side=2, on_ends=1))
    template_name = 'ru/elan_siyahi.html' if is_ru else 'elan_siyahi.html'

    return render(request, template_name, {
        'is_ru': is_ru,
        'elanlar': elanlar_page,
        'page_range': page_range,
        'kateqoriyalar': kateqoriyalar,
        'axtaris': axtaris,
        'elan_seed': seed,
    })


def xidmet_detail(request, slug, lokasiya=None, lang='az'):
    """
    /xidmet/<slug>/, /xidmet/<slug>/<lokasiya>/ və onların /ru/ qarşılıqları.
    """
    _update_elan_status()
    is_ru = (lang == 'ru')
    from .service_pages import pages, topic_response
    from .ru_content import location_ru
    topic = pages().get(slug)
    if topic and topic['category'] != slug:
        if lokasiya:
            raise Http404('Bu xidmət üçün ayrıca rayon səhifəsi yoxdur.')
        return topic_response(request, topic, is_ru=is_ru)
    aktiv_kategori = get_object_or_404(Kategori, slug=slug)

    lokasiya_melumat = None
    if lokasiya:
        lokasiya_melumat = location_ru(lokasiya) if is_ru else get_lokasiya(lokasiya)
        if not lokasiya_melumat:
            raise Http404("Lokasiya tapılmadı")

    seed_key = f'kat_elan_seed_{slug}_{lokasiya}' if lokasiya else f'kat_elan_seed_{slug}'
    seed = get_or_create_listing_seed(request, session_key=seed_key)

    elanlar = (
        visible_listings(request.user)
        .filter(Q(kategori__slug=slug) | Q(kategori__ust_kategori__slug=slug))
        .select_related('kategori', 'istifadeci__profil')
        .prefetch_related('shekillar')
    )

    axtaris = request.GET.get('q', '').strip()
    elanlar = search_listings(elanlar, axtaris, lokasiya or '')
    elanlar = apply_fair_rotation(elanlar, seed)
    counts = location_counts(elanlar)
    local_count = counts.get(lokasiya, 0) if lokasiya else 0

    kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    paginator = Paginator(elanlar, 20)
    page_num = request.GET.get('page', 1)
    elanlar_page = strict_page(paginator, page_num)
    page_range = list(paginator.get_elided_page_range(elanlar_page.number, on_each_side=2, on_ends=1))

    # SEO: daxili linkləmə — eyni qrupdan digər xidmətlər və əlaqəli bələdçilər
    indexable_ids = indexable_kategori_ids()
    from .service_content import get_content
    brief = get_content(aktiv_kategori)
    related_slugs = brief['related'] if brief else []
    curated_related = list(
        Kategori.objects.filter(slug__in=related_slugs)
        .exclude(pk=aktiv_kategori.pk)
    )
    curated_related.sort(key=lambda category: related_slugs.index(category.slug))
    curated_related = [category for category in curated_related if category.pk in indexable_ids]
    if aktiv_kategori.ust_kategori_id:
        siblings = [
            k for k in Kategori.objects.filter(ust_kategori_id=aktiv_kategori.ust_kategori_id)
            .exclude(pk=aktiv_kategori.pk).order_by('pk')
            if k.pk in indexable_ids
        ]
    else:
        siblings = [
            k for k in Kategori.objects.filter(ust_kategori__isnull=True)
            .exclude(pk=aktiv_kategori.pk).order_by('pk')
            if k.pk in indexable_ids
        ]
    oxsar_kateqoriyalar = (curated_related + [k for k in siblings if k not in curated_related])[:8]
    problemler = Problem.objects.filter(aktiv=True).filter(
        Q(kategori=aktiv_kategori) | Q(kategori__ust_kategori=aktiv_kategori)
    )[:6]
    qiymet_aralig = elanlar.order_by().aggregate(min_q=Min('qiymet'), max_q=Max('qiymet'))
    from .service_pages import guide_for_category, page_context, provider_coverage_q, BAKU_AREAS
    guide = guide_for_category(aktiv_kategori) if not lokasiya else None
    service_context = page_context(guide, request.user, is_ru=is_ru) if guide else {}
    has_declared_coverage = False
    if lokasiya:
        has_declared_coverage = bool(
            (lokasiya in BAKU_AREAS and elanlar.filter(provider_coverage_q()).exists())
            or elanlar.alias(_cov_areas=areas_expression()).filter(_cov_areas__contains=f',{lokasiya},').exists()
        )
    all_locations = [
        dict(location_ru(key) if is_ru else LOKASIYALAR[key], count=value)
        for key, value in counts.items()
    ]
    popular_locations = [
        (location_ru(k) if is_ru else LOKASIYALAR[k])
        for k in POPULAR_LOKASIYALAR if k in LOKASIYALAR
    ]
    template_name = 'ru/xidmet_detail.html' if is_ru else 'xidmet_detail.html'

    return render(request, template_name, {
        **service_context,
        'is_ru': is_ru,
        'elanlar': elanlar_page,
        'page_range': page_range,
        'kateqoriyalar': kateqoriyalar,
        'aktiv_kategori': aktiv_kategori,
        'lokasiya': lokasiya,
        'lokasiya_melumat': lokasiya_melumat,
        'local_listing_count': local_count,
        'has_declared_coverage': has_declared_coverage,
        'local_listings': list(in_location(elanlar, lokasiya)[:4]) if lokasiya and local_count else [],
        'butun_lokasiyalar': all_locations,
        'populyar_lokasiyalar': popular_locations,
        'axtaris': axtaris,
        'elan_var': elanlar_page.paginator.count > 0,
        'kat_indexable': aktiv_kategori.pk in indexable_ids and (not lokasiya or local_count > 0),
        'oxsar_kateqoriyalar': oxsar_kateqoriyalar,
        'problemler': problemler,
        'min_qiymet': qiymet_aralig['min_q'],
        'max_qiymet': qiymet_aralig['max_q'],
        'elan_seed': seed,
    })

def elan_detail(request, pk, slug=None):
    elan = Elan.objects.select_related('kategori', 'kategori__ust_kategori', 'istifadeci__profil').prefetch_related('shekillar').filter(pk=pk).first()
    if elan is None:
        # Silinmiş elan: köhnə linki uyğun yeni səhifəyə 301 ilə ötürürük,
        # izi olmayan köhnə ID-lər üçün 410 Gone (Google onları tez çıxarır).
        iz = SilinmisElan.objects.select_related('kategori__ust_kategori').filter(elan_id=pk).first()
        if iz:
            return redirect(replacement_url(iz.istifadeci_id, iz.kategori), permanent=True)
        return render(request, '404.html', status=410)
    user = request.user
    is_privileged = user.is_authenticated and (user.pk == elan.istifadeci_id or user.has_perm('core.view_elan'))
    if not is_privileged and not is_public(elan):
        # Müddəti bitmiş / deaktiv elan: noindex 404 əvəzinə yeni elana / xidmət səhifəsinə yönləndir.
        # Gözləmədə olan elan tezliklə aktivləşə bilər — ona görə müvəqqəti (302) yönləndirmə.
        return redirect(replacement_url(elan.istifadeci_id, elan.kategori, exclude_pk=elan.pk),
                        permanent=elan.status != 'gozlemede')
    check_access(elan, request.user)
    # Slug mövcud deyilsə (köhnə /elan/<id>/) və ya səhvdirsə → 301 canonical
    if slug != elan.slug:
        return redirect(elan.get_absolute_url(), permanent=True)
    is_owner = request.user.is_authenticated and request.user == elan.istifadeci
    if not is_owner and not _is_bot(request):
        ip = _get_client_ip(request)
        cache_key = f'viewed_elan_ip_{pk}_{ip}'
        viewed_key = f'viewed_elan_{pk}'
        if not request.session.get(viewed_key) and not cache.get(cache_key):
            Elan.objects.filter(pk=pk).update(baxish_sayi=F('baxish_sayi') + 1)
            elan.baxish_sayi += 1
            request.session[viewed_key] = True
            cache.set(cache_key, 1, 3600 * 6)
    favorit = False
    if request.user.is_authenticated:
        favorit = Favorit.objects.filter(istifadeci=request.user, elan=elan).exists()

    oxsar_elanlar = []
    if elan.kategori:
        oxsar_qs = (
            Elan.objects.filter(status='aktiv', kategori=elan.kategori)
            .exclude(pk=elan.pk)
            .select_related('kategori')
            .prefetch_related('shekillar')[:6]
        )
        oxsar_elanlar = list(oxsar_qs)
        if len(oxsar_elanlar) < 4 and elan.kategori.ust_kategori:
            elave = list(
                Elan.objects.filter(status='aktiv', kategori__ust_kategori=elan.kategori.ust_kategori)
                .exclude(pk=elan.pk)
                .exclude(pk__in=[e.pk for e in oxsar_elanlar])
                .select_related('kategori')
                .prefetch_related('shekillar')[:6 - len(oxsar_elanlar)]
            )
            oxsar_elanlar.extend(elave)

    return render(request, 'elan_detail.html', {
        'elan': elan,
        'favorit': favorit,
        'oxsar_elanlar': oxsar_elanlar,
        'is_inactive': elan.status != 'aktiv',
    })

@login_required
def elan_yarat(request):
    categories = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    selected = [s for s in request.POST.getlist('xidmet_erazileri') if s in LOKASIYALAR] if request.method == 'POST' else []
    ctx = {
        'kateqoriyalar': categories,
        'form_data': request.POST,
        'lokasiya_qruplari': grouped_lokasiyalar(),
        'baki_rayonlari': BAKI_RAYONLARI,
        'secilmis_eraziler': selected,
    }
    if request.method == 'POST':
        try:
            create_listing(request.user, request.POST, request.FILES.getlist('shekillar'))
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
        else:
            messages.success(request, 'Elan uğurla yerləşdirildi!')
            return redirect('profil')
    return render(request, 'elan_yarat.html', ctx)


@login_required
def elan_duzelis(request, pk):
    ad = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    selected = ([s for s in request.POST.getlist('xidmet_erazileri') if s in LOKASIYALAR]
                if request.method == 'POST' else ad.erazi_sluglari)
    ctx = {
        'elan': ad,
        'kateqoriyalar': Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar'),
        'lokasiya_qruplari': grouped_lokasiyalar(),
        'baki_rayonlari': BAKI_RAYONLARI,
        'secilmis_eraziler': selected,
    }
    if request.method == 'POST':
        try:
            update_listing(request.user, pk, request.POST, request.FILES.getlist('shekillar'))
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
        else:
            messages.success(request, 'Elan yeniləndi!')
            return redirect('profil')
    return render(request, 'elan_duzelis.html', ctx)


@login_required
@require_POST
def shekil_sil(request, pk):
    shekil = get_object_or_404(ElanShekil, pk=pk, elan__istifadeci=request.user)
    elan = shekil.elan
    was_esas = shekil.esas
    shekil.delete()
    if was_esas:
        next_shekil = elan.shekillar.first()
        if next_shekil:
            next_shekil.esas = True
            next_shekil.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    messages.success(request, 'Şəkil silindi!')
    return redirect('elan_duzelis', pk=elan.pk)


@login_required
@require_POST
def shekil_esas(request, pk):
    shekil = get_object_or_404(ElanShekil, pk=pk, elan__istifadeci=request.user)
    elan = shekil.elan
    elan.shekillar.update(esas=False)
    shekil.esas = True
    shekil.save()
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'ok': True})
    messages.success(request, 'Əsas şəkil dəyişdirildi!')
    return redirect('elan_duzelis', pk=elan.pk)


@login_required
def elan_sil(request, pk):
    if request.method != 'POST':
        return redirect('profil')
    elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    elan.delete()
    messages.success(request, 'Elan silindi!')
    return redirect('profil')

@login_required
@require_POST
def elan_aktivlesdir(request, pk):
    try:
        get_object_or_404(Elan, pk=pk, istifadeci=request.user)
        reactivate_listing(request.user, pk)
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
    else:
        messages.success(request, 'Elan moderasiyaya göndərildi.')
    return redirect('profil')


def qeydiyyat(request):
    if request.method == 'POST':
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        if cache.get(f'register_limit:{ip}'):
            messages.error(request, 'Qeydiyyat sorğusu çox tez-tez edilir. Bir az gözləyin.')
            return render(request, 'qeydiyyat.html')
        ad = request.POST.get('ad', '').strip()
        soyad = request.POST.get('soyad', '').strip()
        username = request.POST.get('username', '').strip()
        email = request.POST.get('email', '').strip()
        password = request.POST.get('password', '')
        password2 = request.POST.get('password2', '')

        if not ad or not soyad:
            messages.error(request, 'Ad və soyad mütləqdir!')
            return render(request, 'qeydiyyat.html')
        if len(username) < 8:
            messages.error(request, 'İstifadəçi adı minimum 8 simvol olmalıdır!')
            return render(request, 'qeydiyyat.html')
        if not username.isalnum():
            messages.error(request, 'İstifadəçi adı yalnız hərf və rəqəmdən ibarət olmalıdır!')
            return render(request, 'qeydiyyat.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu istifadəçi adı artıq mövcuddur!')
            return render(request, 'qeydiyyat.html')
        if not re.match(r'^[^@\s]+@[^@\s]+\.[^@\s]+$', email):
            messages.error(request, 'Düzgün email ünvanı daxil edin!')
            return render(request, 'qeydiyyat.html')
        if User.objects.filter(email__iexact=email).exists():
            messages.error(request, 'Bu email artıq qeydiyyatdan keçib!')
            return render(request, 'qeydiyyat.html')
        if len(password) > 128:
            messages.error(request, "Şifrə maksimum 128 simvol ola bilər.")
            return redirect('qeydiyyat')
        if password != password2:
            messages.error(request, 'Şifrələr uyğun gəlmir!')
            return render(request, 'qeydiyyat.html')

        try:
            candidate = User(username=username, email=email, first_name=ad, last_name=soyad)
            candidate.full_clean(exclude=['password'])
            validate_password(password, candidate)
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
            return render(request, 'qeydiyyat.html')
        user = User.objects.create_user(username=username, email=email.lower(), password=password)
        user.first_name = ad
        user.last_name = soyad
        user.save()
        Profil.objects.filter(istifadeci=user).update(ad=ad, soyad=soyad)
        cache.set(f'register_limit:{ip}', True, 3600)
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')
        messages.success(request, 'Xoş gəldiniz!')
        return redirect('index')
    return render(request, 'qeydiyyat.html')

def giris(request):
    if request.method == 'POST':
        ip = request.META.get('REMOTE_ADDR', 'unknown')
        attempts = cache.get(f'login_attempt:{ip}', 0)
        if attempts >= 5:
            messages.error(request, 'Çox sayda uğursuz cəhd. 5 dəqiqə sonra yenidən cəhd edin.')
            return render(request, 'giris.html')
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user:
            cache.delete(f'login_attempt:{ip}')
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('index')
        cache.set(f'login_attempt:{ip}', attempts + 1, 300)
        messages.error(request, 'İstifadəçi adı və ya şifrə yanlışdır!')
    return render(request, 'giris.html')

@require_POST
def cixis(request):
    logout(request)
    return redirect('index')

def sifre_unutdum(request):
    if request.method == 'POST':
        from django.contrib.auth.forms import PasswordResetForm
        import logging
        ip = _get_client_ip(request)
        key = f'sifre_reset:{ip}'
        attempts = cache.get(key, 0)
        if attempts >= 3:
            return render(request, 'sifre_unutdum.html', status=429)
        cache.set(key, attempts + 1, 600)
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            try:
                form.save(request=request, use_https=not settings.DEBUG,
                          email_template_name='registration/password_reset_email.txt',
                          subject_template_name='registration/password_reset_subject.txt',
                          from_email=settings.DEFAULT_FROM_EMAIL)
            except Exception:
                logging.getLogger('core').exception('Password reset delivery failed')
        messages.success(request, 'Hesab mövcuddursa, şifrə bərpa keçidi emailinizə göndəriləcək.')
        return redirect('sifre_unutdum')
    return render(request, 'sifre_unutdum.html')

@csrf_exempt
def elan_klik_artir(request, pk, nov):
    """Telefon zəngi və WhatsApp kliklərini asinxron qeydə alır."""
    if _is_bot(request):
        return JsonResponse({'status': 'ignored_bot'})

    if request.method in ('POST', 'GET'):
        ip = _get_client_ip(request)
        cache_key = f"elan_click_{nov}_{pk}_{ip}"
        if not cache.get(cache_key):
            cache.set(cache_key, 1, 1800)
            if nov == 'zeng':
                Elan.objects.filter(pk=pk).update(zeng_sayi=F('zeng_sayi') + 1)
            elif nov in ('wp', 'whatsapp'):
                Elan.objects.filter(pk=pk).update(wp_sayi=F('wp_sayi') + 1)
        return JsonResponse({'status': 'ok'})
    return JsonResponse({'status': 'invalid'}, status=400)


@login_required
def profil(request):
    profil, _ = Profil.objects.get_or_create(istifadeci=request.user)
    all_ads = Elan.objects.filter(istifadeci=request.user).select_related('kategori', 'istifadeci__profil').prefetch_related('shekillar').order_by('-yaradildi', '-pk')
    expired = Q(status='muddeti_bitmis') | Q(status='aktiv', bitis_tarixi__lte=timezone.now())
    elanlar = strict_page(Paginator(all_ads.exclude(expired), 30), request.GET.get('ads_page', 1))
    muddeti_bitmis = strict_page(Paginator(all_ads.filter(expired), 30), request.GET.get('expired_page', 1))
    favorites = Favorit.objects.filter(istifadeci=request.user, elan__in=visible_listings(request.user)).select_related(
        'elan__kategori', 'elan__istifadeci__profil').prefetch_related('elan__shekillar').order_by('-pk')
    favoritler = strict_page(Paginator(favorites, 30), request.GET.get('favorites_page', 1))
    oxunmamis = Mesaj.objects.filter(alici=request.user, oxundu=False).count()
    totals = all_ads.aggregate(views=Sum('baxish_sayi'), calls=Sum('zeng_sayi'), whatsapp=Sum('wp_sayi'))
    paketler = VipPaket.get_all_aktiv()
    vip_paket = next((p for p in paketler if p.nov == 'vip'), None)
    super_vip_paket = next((p for p in paketler if p.nov == 'super_vip'), None)
    return render(request, 'profil.html', {
        'profil': profil,
        'elanlar': elanlar,
        'favoritler': favoritler,
        'oxunmamis': oxunmamis,
        'muddeti_bitmis': muddeti_bitmis,
        'cemi_baxish': totals['views'] or 0,
        'cemi_zeng': totals['calls'] or 0,
        'cemi_wp': totals['whatsapp'] or 0,
        'paketler': paketler,
        'vip_paket': vip_paket,
        'super_vip_paket': super_vip_paket,
    })

@login_required
def profil_duzelis(request):
    if request.method == 'POST':
        user = request.user
        yeni_ad = request.POST.get('ad', '').strip()
        yeni_soyad = request.POST.get('soyad', '').strip()
        yeni_email = request.POST.get('email', '').strip()
        yeni_telefon = request.POST.get('telefon', '').strip()
        yeni_sheher = request.POST.get('sheher', '').strip()
        kohne_sifre = request.POST.get('kohne_sifre', '')
        yeni_sifre = request.POST.get('yeni_sifre', '')
        yeni_sifre2 = request.POST.get('yeni_sifre2', '')

        try:
            yeni_ad = text(yeni_ad, 'Ad', 50, minimum=0)
            yeni_soyad = text(yeni_soyad, 'Soyad', 50, minimum=0)
            yeni_telefon = phone(yeni_telefon, optional=True)
            yeni_sheher = text(yeni_sheher, 'Şəhər', 100, minimum=0)
            if yeni_email:
                from django.core.validators import validate_email
                validate_email(yeni_email)
                yeni_email = yeni_email.lower()
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
            return redirect('profil_duzelis')

        if yeni_email and yeni_email != user.email:
            if User.objects.filter(email__iexact=yeni_email).exclude(pk=user.pk).exists():
                messages.error(request, 'Bu email artıq istifadə olunur!')
                return redirect('profil_duzelis')

        if kohne_sifre:
            if not user.check_password(kohne_sifre):
                messages.error(request, 'Köhnə şifrə yanlışdır!')
                return redirect('profil_duzelis')
            if len(yeni_sifre) > 128:
                messages.error(request, "Şifrə maksimum 128 simvol ola bilər.")
                return redirect('profil_duzelis')
            if yeni_sifre != yeni_sifre2:
                messages.error(request, 'Yeni şifrələr uyğun gəlmir!')
                return redirect('profil_duzelis')

        if yeni_email and yeni_email != user.email:
            user.email = yeni_email

        profil, _ = Profil.objects.get_or_create(istifadeci=user)
        profil.ad = yeni_ad
        profil.soyad = yeni_soyad
        profil.telefon = yeni_telefon
        profil.sheher = yeni_sheher
        profil.save()
        user.first_name = yeni_ad
        user.last_name = yeni_soyad
        user.save()

        if kohne_sifre:
            try:
                validate_password(yeni_sifre, user)
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
                return redirect('profil_duzelis')
            user.set_password(yeni_sifre)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Şifrə dəyişdirildi!')

        messages.success(request, 'Məlumatlar yeniləndi!')
        return redirect('profil')
    return render(request, 'profil_duzelis.html')

@login_required
@require_POST
def hesab_sil(request):
    """İstifadəçinin öz hesabını və bağlı bütün məlumatlarını birdəfəlik silməsi."""
    user = request.user
    if user.is_staff or user.is_superuser:
        messages.error(request, 'Admin hesabı silinə bilməz.')
        return redirect('profil')

    if user.has_usable_password():
        password = request.POST.get('password', '')
        if not password or not user.check_password(password):
            messages.error(request, 'Daxil edilən şifrə yanlışdır.')
            return redirect('profil')
    else:
        confirm = str(request.POST.get('confirm', '')).strip().upper()
        if confirm != 'SIL':
            messages.error(request, 'Təsdiq üçün "SIL" yazmalısınız.')
            return redirect('profil')

    logout(request)
    with transaction.atomic():
        user.delete()
    messages.success(request, 'Hesabınız və bütün məlumatlarınız uğurla silindi.')
    return redirect('index')

@login_required
def profil_foto(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar = request.FILES['avatar']
        if avatar.size > 10 * 1024 * 1024:
            messages.error(request, 'Şəkil 10MB-dan böyük ola bilməz!')
            return redirect('profil')
        ctype = (avatar.content_type or '').lower()
        if not (ctype.startswith('image/') or ctype == 'application/octet-stream'):
            messages.error(request, 'Yalnız şəkil faylı yüklənə bilər!')
            return redirect('profil')
        try:
            profil, _ = Profil.objects.get_or_create(istifadeci=request.user)
            profil.avatar = image_upload(avatar)
            profil.save()
            messages.success(request, 'Profil foto yeniləndi!')
        except Exception:
            import logging, traceback
            logging.getLogger('django').error(
                'profil_foto upload failed user=%s size=%s type=%s\n%s',
                request.user.pk, avatar.size, ctype, traceback.format_exc()
            )
            messages.error(request, 'Şəkil yüklənmədi. Başqa şəkil seçib yenidən cəhd edin.')
    return redirect('profil')

def istifadeci_profil(request, pk):
    istifadeci = get_object_or_404(User.objects.select_related('profil'), pk=pk)
    listings = visible_listings(request.user).filter(istifadeci=istifadeci).select_related('kategori', 'istifadeci__profil').prefetch_related('shekillar').order_by('-yaradildi', '-pk')
    elanlar = strict_page(Paginator(listings, 30), request.GET.get('page', 1))
    return render(request, 'istifadeci_profil.html', {
        'sahib': istifadeci,
        'elanlar': elanlar
    })

@login_required
@require_POST
def favorit_toggle(request, pk):
    elan = get_object_or_404(Elan, pk=pk)
    check_access(elan, request.user)
    fav, yaradildi = Favorit.objects.get_or_create(istifadeci=request.user, elan=elan)
    if not yaradildi:
        fav.delete()
    return redirect(elan.get_absolute_url())

@login_required
def mesajlar(request):
    blocked = Bloklama.bloklanmis_idler(request.user)
    incoming = Mesaj.objects.filter(alici=request.user).exclude(gonderici_id__in=blocked).select_related('gonderici__profil', 'elan').order_by('-pk')
    outgoing = Mesaj.objects.filter(gonderici=request.user).exclude(alici_id__in=blocked).select_related('alici__profil', 'elan').order_by('-pk')
    received = strict_page(Paginator(incoming, 30), request.GET.get('in_page', 1))
    sent = strict_page(Paginator(outgoing, 30), request.GET.get('out_page', 1))
    return render(request, 'mesajlar.html', {'qelen': received, 'gonderilenler': sent,
        'qelen_say': received.paginator.count, 'gonderilenler_say': sent.paginator.count})

@login_required
def mesaj_oxu(request, pk):
    mesaj = get_object_or_404(Mesaj, pk=pk)
    if mesaj.alici != request.user and mesaj.gonderici != request.user:
        return redirect('mesajlar')
    other_id = mesaj.gonderici_id if mesaj.alici_id == request.user.pk else mesaj.alici_id
    check_messaging(request.user, other_id)
    if mesaj.alici == request.user and not mesaj.oxundu:
        mesaj.oxundu = True
        mesaj.save()
    return render(request, 'mesaj_oxu.html', {'mesaj': mesaj})

@login_required
def mesaj_cavab(request, pk):
    original = get_object_or_404(Mesaj.objects.select_related('elan'), pk=pk)
    if request.user.pk not in (original.alici_id, original.gonderici_id):
        raise PermissionDenied
    receiver_id = original.gonderici_id if original.alici_id == request.user.pk else original.alici_id
    check_messaging(request.user, receiver_id)
    receiver = get_object_or_404(User, pk=receiver_id, is_active=True)
    if request.method == 'POST':
        try:
            body = text(request.POST.get('metn', ''), 'Mesaj', 5000)
        except ValidationError as exc:
            messages.error(request, ' '.join(exc.messages))
        else:
            Mesaj.objects.create(gonderici=request.user, alici=receiver, elan=original.elan, metn=body)
            messages.success(request, 'Cavab göndərildi.')
            return redirect('mesajlar')
    return render(request, 'mesaj_yeni.html', {'elan': original.elan, 'receiver': receiver})


@login_required
def mesaj_yeni(request, elan_pk):
    elan = get_object_or_404(Elan, pk=elan_pk)
    check_access(elan, request.user)
    check_messaging(request.user, elan.istifadeci_id)
    if request.method == 'POST':
        metn = request.POST.get('metn', '').strip()
        if len(metn) > 5000:
            messages.error(request, 'Mesaj maksimum 5000 simvol ola bilər.')
        elif metn:
            Mesaj.objects.create(gonderici=request.user, alici=elan.istifadeci, elan=elan, metn=metn)
            messages.success(request, 'Mesajınız göndərildi!')
            return redirect(elan.get_absolute_url())
    return render(request, 'mesaj_yeni.html', {'elan': elan})

@login_required
def vip_et(request, pk):
    elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    profil = request.user.profil
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    if request.method == 'POST':
        try:
            data = request.POST
            if request.content_type == 'application/json':
                import json
                data = json.loads(request.body)
                if not isinstance(data, dict):
                    raise ValidationError('Sorğu düzgün deyil.')
            elan, profil, paket = buy_vip(request.user, pk, data.get('nov'))
        except (ValidationError, ValueError) as exc:
            error = ' '.join(exc.messages) if isinstance(exc, ValidationError) else 'Sorğu düzgün deyil.'
            if is_ajax:
                return JsonResponse({'success': False, 'message': error}, status=400)
            messages.error(request, error)
        else:
            if is_ajax:
                return JsonResponse({'success': True, 'message': 'VIP aktivləşdirildi.', 'yeni_balans': str(profil.balans)})
            messages.success(request, 'VIP aktivləşdirildi.')
        return redirect('profil')
    return render(request, 'vip.html', {'elan': elan, 'profil': profil, 'paketler': VipPaket.get_all_aktiv()})


@login_required
@require_POST
def elan_ireli_cek(request, pk):
    get_object_or_404(Elan, pk=pk)
    is_ajax = request.headers.get('x-requested-with') == 'XMLHttpRequest' or request.content_type == 'application/json'
    try:
        elan, profil = bump_listing(request.user, pk)
    except ValidationError as exc:
        error = ' '.join(exc.messages)
        if is_ajax:
            return JsonResponse({'success': False, 'message': error}, status=400)
        messages.error(request, error)
    else:
        if is_ajax:
            return JsonResponse({'success': True, 'message': 'Elan irəli çəkildi.',
                                 'yeni_balans': str(profil.balans), 'elan_pk': elan.pk})
        messages.success(request, 'Elan irəli çəkildi.')
    return redirect('profil')


@login_required
def odenis(request):
    ctx = {
        'bank': BankMelumat.objects.filter(aktiv=True).first(),
        'birbank_env': getattr(settings, 'BIRBANK_ENV', 'test'),
        'birbank_ready': birbank_gateway.is_configured,
    }
    if request.method == 'POST':
        metod = request.POST.get('metod', 'qebz').strip().lower()
        if metod == 'birbank':
            if not getattr(settings, 'BIRBANK_ENABLED', False) and not birbank_gateway.is_configured:
                messages.info(request, 'Birbank ilə onlayn ödəniş tezliklə istifadəyə veriləcək. Zəhmət olmasa bank köçürməsi ilə ödəniş edin.')
                return redirect('odenis')

            try:
                amount = money(request.POST.get('mebleg'), minimum=Decimal('1.00'), maximum=Decimal('500.00'))
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
                return render(request, 'odenis.html', ctx)

            odenis_obj = Odenis.objects.create(
                istifadeci=request.user,
                nov='balans',
                mebleg=amount,
                metod='birbank',
                status='gozlemede',
                qeyd='Birbank onlayn ödəniş'
            )
            success_url = request.build_absolute_uri(reverse('birbank_ugurlu')) + f"?odenis_id={odenis_obj.pk}"
            fail_url = request.build_absolute_uri(reverse('birbank_ugursuz')) + f"?odenis_id={odenis_obj.pk}"

            res = birbank_gateway.create_order(
                odenis_id=odenis_obj.pk,
                amount=amount,
                description=f"Prousta balans #{odenis_obj.pk} ({request.user.username})",
                success_url=success_url,
                fail_url=fail_url,
            )
            if res.get('success'):
                odenis_obj.xarici_id = res.get('order_id')
                odenis_obj.save(update_fields=['xarici_id'])
                redirect_url = res.get('redirect_url') or ''
                if not (redirect_url.startswith('/') and not redirect_url.startswith('//')) and \
                        urlsplit(redirect_url).hostname not in _BIRBANK_HOSTS:
                    odenis_obj.status = 'legv_edildi'
                    odenis_obj.save(update_fields=['status'])
                    messages.error(request, 'Ödəniş səhifəsi təsdiqlənmədi.')
                    return render(request, 'odenis.html', ctx)
                return redirect(redirect_url)
            else:
                odenis_obj.status = 'legv_edildi'
                odenis_obj.qeyd = res.get('error', 'Gateway xətası')[:500]
                odenis_obj.save(update_fields=['status', 'qeyd'])
                messages.error(request, res.get('error') or 'Onlayn ödəniş hazırda əlçatan deyil.')
                return render(request, 'odenis.html', ctx)

        elif metod == 'qebz':
            try:
                amount = money(request.POST.get('mebleg'), minimum=Decimal('0.01'), maximum=Decimal('500.00'))
                receipt = image_upload(request.FILES.get('qebz'))
                Odenis.objects.create(
                    istifadeci=request.user,
                    nov='balans',
                    mebleg=amount,
                    metod='qebz',
                    qebz=receipt,
                    status='gozlemede'
                )
            except ValidationError as exc:
                messages.error(request, ' '.join(exc.messages))
            else:
                messages.success(request, 'Sorğunuz yoxlanışa göndərildi.')
                return redirect('profil')
        else:
            messages.error(request, 'Yanlış ödəniş metodu seçilib.')

    return render(request, 'odenis.html', ctx)


def _birbank_payment_matches(odenis_obj, res):
    """Bankın təsdiqlədiyi məbləğ və valyuta bizim qeydimizlə tam uyğun olmalıdır."""
    if not res.get('verified'):
        return False
    if res.get('is_simulated'):
        return birbank_gateway.simulator_allowed
    try:
        paid = Decimal(str(res.get('amount'))).quantize(Decimal('0.01'))
    except Exception:
        return False
    currency = str(res.get('currency') or 'AZN').upper()
    return paid == odenis_obj.mebleg and currency in ('AZN', '944')


def _birbank_confirm(odenis_obj, res):
    with transaction.atomic():
        locked = Odenis.objects.select_for_update().get(pk=odenis_obj.pk)
        if locked.status == 'gozlemede' and locked.metod == 'birbank':
            locked.status = 'tesdiq_edildi'
            locked.xarici_status = str(res.get('status', 'FullyPaid'))[:50]
            locked.save()
        return locked


@login_required
def birbank_ugurlu(request):
    odenis_id = request.GET.get('odenis_id')
    if not str(odenis_id or '').isdigit():
        raise Http404
    odenis_obj = get_object_or_404(Odenis, pk=odenis_id, istifadeci=request.user, metod='birbank')

    res = birbank_gateway.check_order_status(odenis_obj.xarici_id)
    if _birbank_payment_matches(odenis_obj, res):
        odenis_obj = _birbank_confirm(odenis_obj, res)
        profil = request.user.profil
        profil.refresh_from_db()
        return render(request, 'odenis_netice.html', {
            'success': odenis_obj.status == 'tesdiq_edildi',
            'odenis': odenis_obj,
            'mebleg': odenis_obj.mebleg,
            'balans': profil.balans,
            'xeta': 'Ödəniş statusu yenilənə bilmədi.',
        })
    return redirect(reverse('birbank_ugursuz') + f"?odenis_id={odenis_obj.pk}")


@login_required
def birbank_ugursuz(request):
    odenis_id = request.GET.get('odenis_id')
    if not str(odenis_id or '').isdigit():
        raise Http404
    odenis_obj = get_object_or_404(Odenis, pk=odenis_id, istifadeci=request.user, metod='birbank')
    reason = 'Ödəniş ləğv edildi və ya bank tərəfindən təsdiqlənmədi.'
    if odenis_obj.status == 'gozlemede':
        # Ləğv etməzdən əvvəl bankdan yoxlayırıq: real ödəniş edilibsə, balansı itirməsin.
        is_simulated = str(odenis_obj.xarici_id or '').startswith('SIM-')
        res = {} if is_simulated else birbank_gateway.check_order_status(odenis_obj.xarici_id)
        if not is_simulated and _birbank_payment_matches(odenis_obj, res):
            _birbank_confirm(odenis_obj, res)
            return redirect(reverse('birbank_ugurlu') + f"?odenis_id={odenis_obj.pk}")
        with transaction.atomic():
            locked = Odenis.objects.select_for_update().get(pk=odenis_obj.pk)
            if locked.status == 'gozlemede':
                locked.status = 'legv_edildi'
                locked.xarici_status = str(res.get('status') or 'Declined')[:50]
                locked.save(update_fields=['status', 'xarici_status'])
            odenis_obj = locked
    return render(request, 'odenis_netice.html', {
        'success': False,
        'odenis': odenis_obj,
        'mebleg': odenis_obj.mebleg,
        'xeta': reason,
    })


@login_required
def birbank_simulator(request):
    """Yalnız lokal DEBUG mühitində Birbank ödəniş səhifəsinin simulyasiyası."""
    if not birbank_gateway.simulator_allowed:
        raise Http404
    odenis_id = request.GET.get('odenis_id')
    if not str(odenis_id or '').isdigit():
        raise Http404
    odenis_obj = get_object_or_404(Odenis, pk=odenis_id, istifadeci=request.user, metod='birbank')
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'approve':
            return redirect(reverse('birbank_ugurlu') + f"?odenis_id={odenis_obj.pk}")
        else:
            return redirect(reverse('birbank_ugursuz') + f"?odenis_id={odenis_obj.pk}")

    return render(request, 'birbank_simulator.html', {
        'odenis': odenis_obj,
        'amount': odenis_obj.mebleg,
        'user': request.user,
    })


@csrf_exempt
def birbank_callback(request):
    order_id = request.GET.get('ID') or request.POST.get('id')
    if order_id:
        order_id = str(order_id)[:120]
        odenis_obj = Odenis.objects.filter(xarici_id=order_id, metod='birbank').first()
        if odenis_obj and odenis_obj.status == 'gozlemede':
            # Callback parametrlərinə etibar edilmir: status yalnız bankın API-si ilə yoxlanılır.
            res = birbank_gateway.check_order_status(order_id)
            if _birbank_payment_matches(odenis_obj, res):
                _birbank_confirm(odenis_obj, res)
    return HttpResponse('OK', content_type='text/plain')


@login_required
@require_POST
def odenis_tesdiq(request, pk):
    if not request.user.has_perm('core.change_odenis'):
        raise PermissionDenied
    od = get_object_or_404(Odenis, pk=pk)
    try:
        od.status = 'tesdiq_edildi'
        od.save()
    except ValidationError as exc:
        messages.error(request, ' '.join(exc.messages))
    else:
        messages.success(request, 'Ödəniş təsdiqləndi!')
    return redirect('/admin/')


def gizlilik(request):
    return render(request, 'gizlilik.html')

def istifade_sertleri(request):
    return render(request, 'istifade_sertleri.html')

def haqqimizda(request, lang='az'):
    is_ru = (lang == 'ru')
    return render(request, 'ru/haqqimizda.html' if is_ru else 'haqqimizda.html', {'is_ru': is_ru})

def mobil_app(request):
    return render(request, 'mobil_app.html')

@login_required
def profil_foto_crop(request):
    return render(request, 'profil_foto_crop.html')

def problemler_siyahi(request):
    problemler = Problem.objects.filter(aktiv=True).select_related('kategori')
    kateqoriyalar = (
        Kategori.objects.filter(problemler__aktiv=True)
        .distinct()
        .order_by('ad')
    )
    secilmis = (request.GET.get('kategori') or request.GET.get('k') or '').strip()
    if secilmis:
        problemler = problemler.filter(kategori__slug=secilmis)

    axtaris = request.GET.get('q', '').strip()
    if axtaris:
        problemler = problemler.filter(
            Q(bashliq__icontains=axtaris) | Q(metn__icontains=axtaris) | Q(seo_title__icontains=axtaris)
        )

    problemler = problemler.order_by('-yaradildi')
    total_count = problemler.count()

    paginator = Paginator(problemler, 18)
    page_num = request.GET.get('page', 1)
    problemler_page = strict_page(paginator, page_num)
    page_range = list(paginator.get_elided_page_range(problemler_page.number, on_each_side=2, on_ends=1))

    return render(request, 'problemler_siyahi.html', {
        'problemler': problemler_page,
        'kateqoriyalar': kateqoriyalar,
        'secilmis': secilmis,
        'axtaris': axtaris,
        'page_range': page_range,
        'total_count': total_count,
    })


def problem_detail(request, slug):
    _update_elan_status()
    problem = get_object_or_404(Problem.objects.select_related('kategori'), slug=slug, aktiv=True)
    if problem.kategori:
        elanlar_qs = (
            visible_listings(request.user).filter(kategori=problem.kategori)
            .select_related('kategori', 'istifadeci__profil')
            .prefetch_related('shekillar')
        )
        article_seed = f'article_{problem.slug}' if _is_bot(request) else secrets.token_hex(4)
        elanlar = list(apply_fair_rotation(elanlar_qs, article_seed)[:6])
    else:
        elanlar = []
    oxsar = Problem.objects.filter(
        aktiv=True,
        kategori=problem.kategori
    ).exclude(pk=problem.pk)[:4] if problem.kategori else []
    from .seo_articles import article_context
    return render(request, 'problem_detail.html', {
        'problem': problem,
        'elanlar': elanlar,
        'oxsar': oxsar,
        **article_context(problem),
    })


def robots_txt(request):
    from .seo_discovery import robots_response
    return robots_response(request)


def llms_txt(request):
    from .seo_discovery import llms_response
    return llms_response(request)


def _detect_device(user_agent: str) -> str:
    ua = (user_agent or '').lower()
    if 'ipad' in ua or 'tablet' in ua:
        return 'planset'
    if any(m in ua for m in ['mobile', 'android', 'iphone', 'ipod', 'opera mini', 'blackberry']):
        return 'mobil'
    return 'desktop'


def banner_klik(request, banner_id):
    """
    Banner kliklərini izləyir, statistikada qeydə alır və
    müştərinin keçid linkinə yönləndirir.
    """
    banner = get_object_or_404(ReklamBanner, id=banner_id)
    # Açıq yönləndirmə (open redirect) qarşısı: yalnız admin tərəfindən təyin edilmiş http(s) link.
    target_url = (banner.link or '').strip()
    if urlsplit(target_url).scheme not in ('http', 'https'):
        target_url = '/'

    if _is_bot(request):
        return HttpResponseRedirect(target_url)

    ip = _get_client_ip(request)
    ua = request.META.get('HTTP_USER_AGENT', '')
    referer = request.META.get('HTTP_REFERER', '')
    cihaz = _detect_device(ua)

    # 2 saniyəlik anti-spam (eyni IP-dən ardıcıl klikləri qarşılamaq)
    cache_key = f"b_click_spam_{banner_id}_{ip}"
    if not cache.get(cache_key):
        cache.set(cache_key, 1, 2)
        ReklamBanner.objects.filter(id=banner_id).update(klik_sayi=F('klik_sayi') + 1)
        try:
            BannerKlik.objects.create(
                banner=banner,
                ip_unvan=ip,
                cihaz=cihaz,
                user_agent=ua[:500],
                referer=referer[:500]
            )
        except Exception:
            pass

    if request.headers.get('x-requested-with') == 'XMLHttpRequest' or 'application/json' in request.headers.get('accept', ''):
        return JsonResponse({'status': 'ok', 'url': target_url})

    return HttpResponseRedirect(target_url)


def banner_baxis(request, banner_id):
    """
    Bannerin saytda nümayiş sayını (impressions) asinxron olaraq artırır.
    """
    if _is_bot(request):
        return JsonResponse({'status': 'ignored_bot'})

    ip = _get_client_ip(request)
    cache_key = f"b_view_spam_{banner_id}_{ip}"
    if not cache.get(cache_key):
        cache.set(cache_key, 1, 60)
        ReklamBanner.objects.filter(id=banner_id).update(baxis_sayi=F('baxis_sayi') + 1)

    return JsonResponse({'status': 'ok'})

