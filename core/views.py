from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.db.models import Q, F, Case, When, IntegerField
from django.db import transaction
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponse, JsonResponse
from django.views.decorators.http import require_POST
import random
import secrets
import re
from datetime import timedelta
from decimal import Decimal
from django.core.paginator import Paginator
from .models import Elan, Kategori, ElanShekil, Profil, Favorit, Mesaj, Odenis, BankMelumat, Problem

def _aciqlama_qadaga_yoxla(metn):
    """Açıqlamada telefon nömrəsi və ya sayt adı varsa xəta mesajı qaytarır."""
    normalized = re.sub(r'[\s\-\(\)\.]+', '', metn)
    if re.search(r'\d{7,}', normalized):
        return 'Açıqlamada telefon nömrəsi və ya əlaqə nömrəsi yazmaq qadağandır!'
    url_pattern = re.compile(
        r'(https?://|www\.|\b[\w\-]+\.(com|az|net|org|ru|info|biz|co|io|me|tv|edu|gov|az\.com))\b',
        re.IGNORECASE
    )
    if url_pattern.search(metn):
        return 'Açıqlamada sayt adı və ya link yazmaq qadağandır!'
    return None


def _update_elan_status():
    # NOTE: With default LocMemCache and multiple Gunicorn workers, each worker
    # has its own cache, so this may run more often than every 300s across workers.
    # This is acceptable because the underlying UPDATE queries are idempotent.
    # For true single-execution, switch to Redis or database-based caching.
    if not cache.get('elan_status_update'):
        cache.set('elan_status_update', True, 300)
        Elan.objects.filter(status='aktiv', bitis_tarixi__lt=timezone.now()).update(status='muddeti_bitmis')
        Elan.objects.filter(vip_status__in=['vip', 'super_vip'], vip_bitis__lt=timezone.now()).update(vip_status='normal')

def index(request):
    _update_elan_status()
    vip_list = list(Elan.objects.filter(status='aktiv', vip_status__in=['vip','super_vip']).prefetch_related('shekillar'))
    random.shuffle(vip_list)
    vip_elanlar = vip_list
    elanlar = Elan.objects.filter(status='aktiv', vip_status='normal').order_by('-yaradildi').prefetch_related('shekillar')[:12]
    kateqoriyalar = list(
        Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    )
    # Hər əsas kateqoriya üçün son 6 aktiv elan (öz və alt kateqoriyalarından)
    # kategori kartı açıldıqda alt sırada göstərilir.
    for kat in kateqoriyalar:
        kat.son_elanlar = list(
            Elan.objects.filter(status='aktiv').filter(
                Q(kategori=kat) | Q(kategori__ust_kategori=kat)
            ).prefetch_related('shekillar').order_by('-vip_siralama', '-yaradildi')[:6]
        )
    return render(request, 'index.html', {
        'elanlar': elanlar,
        'vip_elanlar': vip_elanlar,
        'kateqoriyalar': kateqoriyalar
    })

def elan_siyahi(request):
    """
    /elanlar/ — əsas xidmət seçimi səhifəsi.
    - Heç bir parametrsiz: əsas səhifədəki kimi açılan kateqoriya kartları göstərilir
    - ?q=<axtaris>: axtarış nəticələri düz siyahı şəklində
    - ?kategori=<slug> (köhnə URL-lər): /xidmet/<slug>/ ünvanına 301 yönləndirmə
    """
    _update_elan_status()

    # Köhnə URL-ləri yeni xidmət səhifəsinə 301 redirect et (SEO backward compat)
    kategori_slug = request.GET.get('kategori', '').strip()
    if kategori_slug:
        return redirect('xidmet_detail', slug=kategori_slug, permanent=True)

    kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    axtaris = request.GET.get('q', '').strip()

    elanlar = Elan.objects.filter(status='aktiv').prefetch_related('shekillar').order_by('-vip_siralama', '-yaradildi')
    if axtaris:
        elanlar = elanlar.filter(
            Q(bashliq__icontains=axtaris) | Q(acaqlama__icontains=axtaris) | Q(nomre__icontains=axtaris)
        )
    paginator = Paginator(elanlar, 20)
    elanlar_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'elan_siyahi.html', {
        'elanlar': elanlar_page,
        'kateqoriyalar': kateqoriyalar,
        'axtaris': axtaris,
    })


def xidmet_detail(request, slug):
    """
    /xidmet/<slug>/ — xidmət üzrə elanlar səhifəsi (SEO-friendly URL).
    Həm əsas, həm alt kateqoriyalar üçün işləyir.
    """
    _update_elan_status()
    aktiv_kategori = get_object_or_404(Kategori, slug=slug)

    elanlar = Elan.objects.filter(status='aktiv').filter(
        Q(kategori__slug=slug) | Q(kategori__ust_kategori__slug=slug)
    ).prefetch_related('shekillar').order_by('-vip_siralama', '-yaradildi')

    axtaris = request.GET.get('q', '').strip()
    if axtaris:
        elanlar = elanlar.filter(
            Q(bashliq__icontains=axtaris) | Q(acaqlama__icontains=axtaris) | Q(nomre__icontains=axtaris)
        )

    kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    paginator = Paginator(elanlar, 20)
    elanlar_page = paginator.get_page(request.GET.get('page', 1))

    return render(request, 'xidmet_detail.html', {
        'elanlar': elanlar_page,
        'kateqoriyalar': kateqoriyalar,
        'aktiv_kategori': aktiv_kategori,
        'axtaris': axtaris,
        'elan_var': elanlar.exists(),
    })

def elan_detail(request, pk, slug=None):
    elan = get_object_or_404(Elan, pk=pk)
    # Slug mövcud deyilsə (köhnə /elan/<id>/) və ya səhvdirsə → 301 canonical
    if slug != elan.slug:
        return redirect(elan.get_absolute_url(), permanent=True)
    is_owner = request.user.is_authenticated and request.user == elan.istifadeci
    viewed_key = f'viewed_elan_{pk}'
    if not is_owner and not request.session.get(viewed_key):
        Elan.objects.filter(pk=pk).update(baxish_sayi=F('baxish_sayi') + 1)
        request.session[viewed_key] = True
    elan.refresh_from_db()
    favorit = False
    if request.user.is_authenticated:
        favorit = Favorit.objects.filter(istifadeci=request.user, elan=elan).exists()
    return render(request, 'elan_detail.html', {'elan': elan, 'favorit': favorit})

@login_required
def elan_yarat(request):
    kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    if request.method == 'POST':
        form_data = {
            'bashliq': request.POST.get('bashliq', ''),
            'acaqlama': request.POST.get('acaqlama', ''),
            'qiymet': request.POST.get('qiymet', ''),
            'sheher': request.POST.get('sheher', ''),
            'telefon': request.POST.get('telefon', ''),
            'kategori': request.POST.get('kategori', ''),
        }
        ctx = {'kateqoriyalar': kateqoriyalar, 'form_data': form_data}
        bashliq = request.POST.get('bashliq', '').strip()
        acaqlama = request.POST.get('acaqlama', '').strip()
        if not bashliq:
            messages.error(request, 'Başlıq boş ola bilməz!')
            return render(request, 'elan_yarat.html', ctx)
        if not acaqlama:
            messages.error(request, 'Açıqlama boş ola bilməz!')
            return render(request, 'elan_yarat.html', ctx)
        qadaga_xeta = _aciqlama_qadaga_yoxla(acaqlama)
        if qadaga_xeta:
            messages.error(request, qadaga_xeta)
            return render(request, 'elan_yarat.html', ctx)
        qiymet_raw = request.POST.get('qiymet')
        if qiymet_raw:
            try:
                if float(qiymet_raw) < 0:
                    messages.error(request, 'Qiymət mənfi ola bilməz!')
                    return render(request, 'elan_yarat.html', ctx)
            except (TypeError, ValueError):
                messages.error(request, 'Qiymət düzgün deyil!')
                return render(request, 'elan_yarat.html', ctx)
        telefon_son = request.POST.get('telefon', '')
        if not re.match(r'^\d{9}$', telefon_son):
            messages.error(request, 'Telefon nömrəsi 9 rəqəmdən ibarət olmalıdır!')
            return render(request, 'elan_yarat.html', ctx)
        shekillar = request.FILES.getlist('shekillar')
        if len(shekillar) > 5:
            messages.error(request, 'Maksimum 5 şəkil yüklənə bilər!')
            return render(request, 'elan_yarat.html', ctx)
        for shekil in shekillar:
            if shekil.size > 5 * 1024 * 1024:
                messages.error(request, 'Hər şəkil 5MB-dan böyük ola bilməz!')
                return render(request, 'elan_yarat.html', ctx)
            if not shekil.content_type.startswith('image/'):
                messages.error(request, 'Yalnız şəkil faylları yüklənə bilər!')
                return render(request, 'elan_yarat.html', ctx)
        try:
            kategori = Kategori.objects.get(pk=request.POST.get('kategori'))
        except Kategori.DoesNotExist:
            messages.error(request, 'Seçilmiş kateqoriya tapılmadı!')
            return render(request, 'elan_yarat.html', ctx)
        aktiv_elanlar = Elan.objects.filter(
            istifadeci=request.user,
            status__in=['aktiv', 'gozlemede']
        )
        if aktiv_elanlar.filter(kategori=kategori).exists():
            messages.error(request, 'Bu kateqoriyada artıq elanınız var! Eyni kateqoriyada ikinci elan yerləşdirmək olmaz.')
            return render(request, 'elan_yarat.html', ctx)
        PULSUZ_LIMIT = 4
        elan_sayi = aktiv_elanlar.count()
        if elan_sayi >= PULSUZ_LIMIT:
            profil = request.user.profil
            if profil.balans < Decimal('1.00'):
                messages.error(request, f'Pulsuz elan limitiniz ({PULSUZ_LIMIT}) bitib. Əlavə elan üçün balansınızda ən azı 1 AZN olmalıdır.')
                return render(request, 'elan_yarat.html', ctx)
        with transaction.atomic():
            if elan_sayi >= PULSUZ_LIMIT:
                profil = Profil.objects.select_for_update().get(istifadeci=request.user)
                if profil.balans < Decimal('1.00'):
                    messages.error(request, f'Pulsuz elan limitiniz ({PULSUZ_LIMIT}) bitib. Balansınız kifayət deyil.')
                    return render(request, 'elan_yarat.html', ctx)
                profil.balans -= Decimal('1.00')
                profil.save(update_fields=['balans'])
            elan = Elan.objects.create(
                istifadeci=request.user,
                kategori=kategori,
                bashliq=bashliq,
                acaqlama=acaqlama,
                qiymet=qiymet_raw or None,
                sheher=request.POST.get('sheher', 'Bakı'),
                telefon='+994' + telefon_son,
                status='gozlemede'
            )
            for i, shekil in enumerate(shekillar):
                ElanShekil.objects.create(elan=elan, shekil=shekil, esas=(i==0))
        messages.success(request, 'Elanınız moderasiyaya göndərildi!')
        return redirect('profil')
    return render(request, 'elan_yarat.html', {'kateqoriyalar': kateqoriyalar})

@login_required
def elan_duzelis(request, pk):
    elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
    if request.method == 'POST':
        telefon_son = request.POST.get('telefon', '')
        if not re.match(r'^\d{9}$', telefon_son):
            messages.error(request, 'Telefon nömrəsi 9 rəqəmdən ibarət olmalıdır!')
            return render(request, 'elan_duzelis.html', {'elan': elan, 'kateqoriyalar': kateqoriyalar})
        acaqlama_yeni = request.POST.get('acaqlama', '').strip()
        qadaga_xeta = _aciqlama_qadaga_yoxla(acaqlama_yeni)
        if qadaga_xeta:
            messages.error(request, qadaga_xeta)
            return render(request, 'elan_duzelis.html', {'elan': elan, 'kateqoriyalar': kateqoriyalar})
        shekillar = request.FILES.getlist('shekillar')
        for shekil in shekillar:
            if shekil.size > 5 * 1024 * 1024:
                messages.error(request, 'Hər şəkil 5MB-dan böyük ola bilməz!')
                return render(request, 'elan_duzelis.html', {'elan': elan, 'kateqoriyalar': kateqoriyalar})
            if not shekil.content_type.startswith('image/'):
                messages.error(request, 'Yalnız şəkil faylları yüklənə bilər!')
                return render(request, 'elan_duzelis.html', {'elan': elan, 'kateqoriyalar': kateqoriyalar})
        elan.bashliq = request.POST.get('bashliq')
        elan.acaqlama = acaqlama_yeni
        elan.qiymet = request.POST.get('qiymet') or None
        elan.sheher = request.POST.get('sheher', 'Bakı')
        elan.telefon = '+994' + telefon_son
        try:
            elan.kategori = Kategori.objects.get(pk=request.POST.get('kategori'))
        except Kategori.DoesNotExist:
            messages.error(request, 'Seçilmiş kateqoriya tapılmadı!')
            return render(request, 'elan_duzelis.html', {'elan': elan, 'kateqoriyalar': kateqoriyalar})
        elan.save()
        for i, shekil in enumerate(shekillar):
            ElanShekil.objects.create(elan=elan, shekil=shekil, esas=False)
        messages.success(request, 'Elan yeniləndi!')
        return redirect('profil')
    return render(request, 'elan_duzelis.html', {'elan': elan, 'kateqoriyalar': kateqoriyalar})

@login_required
@require_POST
def shekil_sil(request, pk):
    shekil = get_object_or_404(ElanShekil, pk=pk, elan__istifadeci=request.user)
    elan = shekil.elan
    was_esas = shekil.esas
    if shekil.shekil:
        shekil.shekil.delete(save=False)
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
    for shekil_obj in elan.shekillar.all():
        if shekil_obj.shekil:
            shekil_obj.shekil.delete(save=False)
    elan.delete()
    messages.success(request, 'Elan silindi!')
    return redirect('profil')

@login_required
@require_POST
def elan_aktivlesdir(request, pk):
    elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    elan.status = 'gozlemede'
    elan.bitis_tarixi = timezone.now() + timedelta(days=30)
    elan.save()
    messages.success(request, 'Elan yenidən moderasiyaya göndərildi!')
    return redirect('profil')

def qeydiyyat(request):
    if request.method == 'POST':
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')).split(',')[0].strip()
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
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Bu email artıq qeydiyyatdan keçib!')
            return render(request, 'qeydiyyat.html')
        if len(password) < 8 or len(password) > 14:
            messages.error(request, 'Şifrə minimum 8, maksimum 14 simvol olmalıdır!')
            return render(request, 'qeydiyyat.html')
        if not any(c.isupper() for c in password):
            messages.error(request, 'Şifrədə ən az 1 böyük hərf olmalıdır!')
            return render(request, 'qeydiyyat.html')
        if not any(c.isdigit() for c in password):
            messages.error(request, 'Şifrədə ən az 1 rəqəm olmalıdır!')
            return render(request, 'qeydiyyat.html')
        if password != password2:
            messages.error(request, 'Şifrələr uyğun gəlmir!')
            return render(request, 'qeydiyyat.html')

        user = User.objects.create_user(username=username, email=email, password=password)
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
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')).split(',')[0].strip()
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
        ip = request.META.get('HTTP_X_FORWARDED_FOR', request.META.get('REMOTE_ADDR', 'unknown')).split(',')[0].strip()
        attempts = cache.get(f'sifre_reset:{ip}', 0)
        if attempts >= 3:
            messages.error(request, 'Şifrə sıfırlama cəhdi çox tez-tez edilir. 10 dəqiqə sonra yenidən cəhd edin.')
            return render(request, 'sifre_unutdum.html')
        cache.set(f'sifre_reset:{ip}', attempts + 1, 600)
        email = request.POST.get('email', '').strip()
        try:
            user = User.objects.get(email=email)
            yeni_sifre = secrets.token_urlsafe(8)[:10]
            try:
                send_mail(
                    'Prousta.az — Yeni Şifrəniz',
                    f'Salam {user.username},\n\nYeni şifrəniz: {yeni_sifre}\n\nDaxil olduqdan sonra şifrənizi dəyişin.',
                    'noreply@prousta.az',
                    [email],
                    fail_silently=False,
                )
            except Exception:
                messages.error(request, 'Email göndərilə bilmədi. Zəhmət olmasa sonra yenidən cəhd edin.')
                return render(request, 'sifre_unutdum.html')
            user.set_password(yeni_sifre)
            user.save()
            messages.success(request, 'Yeni şifrə emailinizə göndərildi!')
        except User.DoesNotExist:
            messages.error(request, 'Bu email ilə qeydiyyat tapılmadı!')
    return render(request, 'sifre_unutdum.html')

@login_required
def profil(request):
    elanlar = Elan.objects.filter(istifadeci=request.user).prefetch_related('shekillar')
    favoritler = Favorit.objects.filter(istifadeci=request.user).prefetch_related('elan__shekillar')
    oxunmamis = Mesaj.objects.filter(alici=request.user, oxundu=False).count()
    muddeti_bitmis = elanlar.filter(status='muddeti_bitmis')
    return render(request, 'profil.html', {
        'elanlar': elanlar,
        'favoritler': favoritler,
        'oxunmamis': oxunmamis,
        'muddeti_bitmis': muddeti_bitmis,
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

        if yeni_email and yeni_email != user.email:
            if User.objects.filter(email=yeni_email).exclude(pk=user.pk).exists():
                messages.error(request, 'Bu email artıq istifadə olunur!')
                return redirect('profil_duzelis')

        if kohne_sifre:
            if not user.check_password(kohne_sifre):
                messages.error(request, 'Köhnə şifrə yanlışdır!')
                return redirect('profil_duzelis')
            if len(yeni_sifre) < 8 or len(yeni_sifre) > 14:
                messages.error(request, 'Yeni şifrə 8-14 simvol olmalıdır!')
                return redirect('profil_duzelis')
            if not any(c.isupper() for c in yeni_sifre):
                messages.error(request, 'Şifrədə ən az 1 böyük hərf olmalıdır!')
                return redirect('profil_duzelis')
            if not any(c.isdigit() for c in yeni_sifre):
                messages.error(request, 'Şifrədə ən az 1 rəqəm olmalıdır!')
                return redirect('profil_duzelis')
            if yeni_sifre != yeni_sifre2:
                messages.error(request, 'Yeni şifrələr uyğun gəlmir!')
                return redirect('profil_duzelis')

        if yeni_email and yeni_email != user.email:
            user.email = yeni_email

        profil = user.profil
        profil.telefon = yeni_telefon
        profil.sheher = yeni_sheher
        profil.save()
        user.first_name = yeni_ad
        user.last_name = yeni_soyad
        user.save()

        if kohne_sifre:
            user.set_password(yeni_sifre)
            user.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Şifrə dəyişdirildi!')

        messages.success(request, 'Məlumatlar yeniləndi!')
        return redirect('profil')
    return render(request, 'profil_duzelis.html')

@login_required
def profil_foto(request):
    if request.method == 'POST' and request.FILES.get('avatar'):
        avatar = request.FILES['avatar']
        if avatar.size > 5 * 1024 * 1024:
            messages.error(request, 'Şəkil 5MB-dan böyük ola bilməz!')
            return redirect('profil')
        if not avatar.content_type.startswith('image/'):
            messages.error(request, 'Yalnız şəkil faylı yüklənə bilər!')
            return redirect('profil')
        profil = request.user.profil
        profil.avatar = avatar
        profil.save()
        messages.success(request, 'Profil foto yeniləndi!')
    return redirect('profil')

def istifadeci_profil(request, pk):
    istifadeci = get_object_or_404(User, pk=pk)
    elanlar = Elan.objects.filter(istifadeci=istifadeci, status='aktiv')
    return render(request, 'istifadeci_profil.html', {
        'sahib': istifadeci,
        'elanlar': elanlar
    })

@login_required
@require_POST
def favorit_toggle(request, pk):
    elan = get_object_or_404(Elan, pk=pk)
    fav, yaradildi = Favorit.objects.get_or_create(istifadeci=request.user, elan=elan)
    if not yaradildi:
        fav.delete()
    return redirect(elan.get_absolute_url())

@login_required
def mesajlar(request):
    qelen = Mesaj.objects.filter(alici=request.user).order_by('-yaradildi')
    gonderilenler = Mesaj.objects.filter(gonderici=request.user).order_by('-yaradildi')
    return render(request, 'mesajlar.html', {
        'qelen': qelen,
        'gonderilenler': gonderilenler,
        'qelen_say': qelen.count(),
        'gonderilenler_say': gonderilenler.count(),
    })

@login_required
def mesaj_oxu(request, pk):
    mesaj = get_object_or_404(Mesaj, pk=pk)
    if mesaj.alici != request.user and mesaj.gonderici != request.user:
        return redirect('mesajlar')
    if mesaj.alici == request.user and not mesaj.oxundu:
        mesaj.oxundu = True
        mesaj.save()
    return render(request, 'mesaj_oxu.html', {'mesaj': mesaj})

@login_required
def mesaj_yeni(request, elan_pk):
    elan = get_object_or_404(Elan, pk=elan_pk)
    if request.user == elan.istifadeci:
        messages.error(request, 'Özünüzə mesaj göndərə bilməzsiniz!')
        return redirect(elan.get_absolute_url())
    if request.method == 'POST':
        metn = request.POST.get('metn', '').strip()
        if metn:
            Mesaj.objects.create(gonderici=request.user, alici=elan.istifadeci, elan=elan, metn=metn)
            messages.success(request, 'Mesajınız göndərildi!')
            return redirect(elan.get_absolute_url())
    return render(request, 'mesaj_yeni.html', {'elan': elan})

@login_required
def vip_et(request, pk):
    elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    profil = request.user.profil
    if request.method == 'POST':
        nov = request.POST.get('nov')
        if nov not in ('vip', 'super_vip'):
            messages.error(request, 'Yanlış VIP növü!')
            return redirect('profil')
        qiymet = 3 if nov == 'vip' else 8
        gun = 10 if nov == 'vip' else 30
        with transaction.atomic():
            updated = Profil.objects.filter(
                pk=profil.pk, balans__gte=qiymet
            ).update(balans=F('balans') - qiymet)
            if not updated:
                messages.error(request, f'Balansınız kifayət deyil! Lazım olan: {qiymet} ₼')
                return redirect('profil')
            elan.vip_status = nov
            elan.vip_bitis = timezone.now() + timedelta(days=gun)
            elan.save()
            Odenis.objects.create(istifadeci=request.user, elan=elan, nov=nov, mebleg=qiymet, status='tesdiq_edildi')
        messages.success(request, f'Elanınız VIP edildi! {gun} gün aktivdir.')
        return redirect('profil')
    return render(request, 'vip.html', {'elan': elan, 'profil': profil})

@login_required
def odenis(request):
    bank = BankMelumat.objects.filter(aktiv=True).first()
    ctx = {'bank': bank}
    if request.method == 'POST':
        qebz = request.FILES.get('qebz')
        if not qebz:
            messages.error(request, 'Zəhmət olmasa köçürmə qəbzini yükləyin!')
            return render(request, 'odenis.html', ctx)
        if qebz.size > 5 * 1024 * 1024:
            messages.error(request, 'Qəbz faylı 5MB-dan böyük ola bilməz!')
            return render(request, 'odenis.html', ctx)
        allowed_types = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'application/pdf']
        if qebz.content_type not in allowed_types:
            messages.error(request, 'Yalnız şəkil (JPEG, PNG, GIF, WebP) və ya PDF faylı yüklənə bilər!')
            return render(request, 'odenis.html', ctx)
        mebleg = request.POST.get('mebleg')
        try:
            mebleg_float = float(mebleg)
            if mebleg_float <= 0 or mebleg_float > 500:
                raise ValueError
        except (TypeError, ValueError):
            messages.error(request, 'Məbləğ 1 ilə 500 ₼ arasında olmalıdır!')
            return render(request, 'odenis.html', ctx)
        Odenis.objects.create(istifadeci=request.user, nov='balans', mebleg=mebleg_float, qebz=qebz, status='gozlemede')
        messages.success(request, 'Sorğunuz göndərildi! Tezliklə balansınız artırılacaq.')
        return redirect('profil')
    return render(request, 'odenis.html', ctx)

@login_required
@require_POST
def odenis_tesdiq(request, pk):
    if not request.user.is_superuser:
        return redirect('index')
    with transaction.atomic():
        od = get_object_or_404(Odenis, pk=pk)
        od.status = 'tesdiq_edildi'
        od.save()
    messages.success(request, 'Ödəniş təsdiqləndi!')
    return redirect('/admin/')

def gizlilik(request):
    return render(request, 'gizlilik.html')

def istifade_sertleri(request):
    return render(request, 'istifade_sertleri.html')

def haqqimizda(request):
    return render(request, 'haqqimizda.html')

@login_required
def profil_foto_crop(request):
    return render(request, 'profil_foto_crop.html')

def problemler_siyahi(request):
    problemler = Problem.objects.filter(aktiv=True)
    kateqoriyalar = Kategori.objects.filter(
        ust_kategori__isnull=False,
        problemler__aktiv=True
    ).distinct()
    secilmis = request.GET.get('kategori')
    if secilmis:
        problemler = problemler.filter(kategori__slug=secilmis)
    return render(request, 'problemler_siyahi.html', {
        'problemler': problemler,
        'kateqoriyalar': kateqoriyalar,
        'secilmis': secilmis,
    })


def problem_detail(request, slug):
    problem = get_object_or_404(Problem, slug=slug, aktiv=True)
    elanlar = Elan.objects.filter(
        status='aktiv',
        kategori=problem.kategori
    ).order_by('-vip_siralama', '-yaradildi')[:6] if problem.kategori else []
    oxsar = Problem.objects.filter(
        aktiv=True,
        kategori=problem.kategori
    ).exclude(pk=problem.pk)[:4] if problem.kategori else []
    return render(request, 'problem_detail.html', {
        'problem': problem,
        'elanlar': elanlar,
        'oxsar': oxsar,
    })


def robots_txt(request):
    content = """User-agent: *
Allow: /static/
Allow: /media/
Allow: /
Disallow: /admin/
Disallow: /profil/
Disallow: /mesajlar/
Disallow: /mesaj/
Disallow: /odenis/
Disallow: /favorit/
Disallow: /elan/yeni/
Disallow: /elan/duzelis/
Disallow: /elan/sil/
Disallow: /elan/aktivlesdir/
Disallow: /vip/
Disallow: /cixis/
Disallow: /sifre-unutdum/
Disallow: /giris/
Disallow: /qeydiyyat/

User-agent: Yandex
Allow: /static/
Allow: /media/
Allow: /
Disallow: /admin/
Disallow: /profil/
Disallow: /mesajlar/
Disallow: /mesaj/
Disallow: /odenis/
Disallow: /favorit/
Disallow: /elan/yeni/
Disallow: /elan/duzelis/
Disallow: /elan/sil/

Sitemap: https://prousta.az/sitemap.xml"""
    return HttpResponse(content, content_type='text/plain')
