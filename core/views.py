from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from .models import Elan, Kategori, ElanShekil, Profil, Favorit
from django.db.models import Q

def index(request):
    elanlar = Elan.objects.filter(status='aktiv')[:12]
    kateqoriyalar = Kategori.objects.all()
    return render(request, 'index.html', {
        'elanlar': elanlar,
        'kateqoriyalar': kateqoriyalar
    })

def elan_siyahi(request):
    elanlar = Elan.objects.filter(status='aktiv')
    axtaris = request.GET.get('q', '')
    kategori = request.GET.get('kategori', '')
    if axtaris:
        elanlar = elanlar.filter(
            Q(bashliq__icontains=axtaris) | Q(acaqlama__icontains=axtaris)
        )
    if kategori:
        elanlar = elanlar.filter(kategori__slug=kategori)
    kateqoriyalar = Kategori.objects.all()
    return render(request, 'elan_siyahi.html', {
        'elanlar': elanlar,
        'kateqoriyalar': kateqoriyalar,
        'axtaris': axtaris
    })

def elan_detail(request, pk):
    elan = get_object_or_404(Elan, pk=pk, status='aktiv')
    elan.baxish_sayi += 1
    elan.save()
    favorit = False
    if request.user.is_authenticated:
        favorit = Favorit.objects.filter(istifadeci=request.user, elan=elan).exists()
    return render(request, 'elan_detail.html', {
        'elan': elan,
        'favorit': favorit
    })

@login_required
def elan_yarat(request):
    kateqoriyalar = Kategori.objects.all()
    if request.method == 'POST':
        elan = Elan.objects.create(
            istifadeci=request.user,
            kategori=Kategori.objects.get(pk=request.POST.get('kategori')),
            bashliq=request.POST.get('bashliq'),
            acaqlama=request.POST.get('acaqlama'),
            qiymet=request.POST.get('qiymet') or None,
            veziyyet=request.POST.get('veziyyet'),
            sheher=request.POST.get('sheher', 'Bakı'),
            status='gozlemede'
        )
        telefon = request.POST.get('telefon', '')
        if telefon:
            from .models import ElanTelefon
            ElanTelefon.objects.create(elan=elan, nomre='+994' + telefon)
        shekillar = request.FILES.getlist('shekillar')
        for i, shekil in enumerate(shekillar):
            ElanShekil.objects.create(
                elan=elan,
                shekil=shekil,
                əsas=(i == 0)
            )
        messages.success(request, 'Elanınız moderasiyaya göndərildi!')
        return redirect('profil')
    return render(request, 'elan_yarat.html', {'kateqoriyalar': kateqoriyalar})

@login_required
def elan_sil(request, pk):
    elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
    elan.delete()
    messages.success(request, 'Elan silindi!')
    return redirect('profil')

def qeydiyyat(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        password2 = request.POST.get('password2')
        if password != password2:
            messages.error(request, 'Şifrələr uyğun gəlmir!')
            return render(request, 'qeydiyyat.html')
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Bu istifadəçi adı artıq mövcuddur!')
            return render(request, 'qeydiyyat.html')
        user = User.objects.create_user(username=username, email=email, password=password)
        Profil.objects.create(istifadeci=user)
        login(request, user)
        messages.success(request, 'Xoş gəldiniz!')
        return redirect('index')
    return render(request, 'qeydiyyat.html')

def giris(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('index')
        messages.error(request, 'İstifadəçi adı və ya şifrə yanlışdır!')
    return render(request, 'giris.html')

def cixis(request):
    logout(request)
    return redirect('index')

@login_required
def profil(request):
    elanlar = Elan.objects.filter(istifadeci=request.user)
    favoritler = Favorit.objects.filter(istifadeci=request.user)
    return render(request, 'profil.html', {
        'elanlar': elanlar,
        'favoritler': favoritler
    })

@login_required
def favorit_toggle(request, pk):
    elan = get_object_or_404(Elan, pk=pk)
    fav, yaradildi = Favorit.objects.get_or_create(istifadeci=request.user, elan=elan)
    if not yaradildi:
        fav.delete()
    return redirect('elan_detail', pk=pk)
