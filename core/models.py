import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

class Kategori(models.Model):
    ad = models.CharField(max_length=100)
    ikon = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(unique=True)
    ust_kategori = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='alt_kateqoriyalar')
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    seo_metn = models.TextField(blank=True, help_text='Kateqoriya səhifəsinin altında göstəriləcək SEO üçün HTML mətn')

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name_plural = "Kateqoriyalar"


class Elan(models.Model):
    STATUS = [
        ('aktiv', 'Aktiv'),
        ('gozlemede', 'Gözləmədə'),
        ('deaktiv', 'Deaktiv'),
        ('muddeti_bitmis', 'Müddəti Bitmiş'),
    ]
    VIP_STATUS = [
        ('normal', 'Normal'),
        ('vip', 'VIP — 10 gün'),
        ('super_vip', 'Super VIP — 30 gün'),
    ]
    VIP_ORDER = {
        'super_vip': 2,
        'vip': 1,
        'normal': 0,
    }

    nomre = models.CharField(max_length=10, unique=True, blank=True)
    istifadeci = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elanlar')
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True)
    bashliq = models.CharField(max_length=200)
    acaqlama = models.TextField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS, default='gozlemede', db_index=True)
    vip_status = models.CharField(max_length=20, choices=VIP_STATUS, default='normal', db_index=True)
    vip_siralama = models.PositiveSmallIntegerField(default=0, db_index=True)
    vip_bitis = models.DateTimeField(null=True, blank=True)
    bitis_tarixi = models.DateTimeField(null=True, blank=True)
    sheher = models.CharField(max_length=100, default='Bakı')
    telefon = models.CharField(max_length=20, blank=True)
    baxish_sayi = models.PositiveIntegerField(default=0)
    yaradildi = models.DateTimeField(auto_now_add=True)
    yenilendi = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.nomre:
            self.nomre = uuid.uuid4().hex[:8].upper()
        self.vip_siralama = self.VIP_ORDER.get(self.vip_status, 0)
        super().save(*args, **kwargs)
        if not self.bitis_tarixi and self.status == 'aktiv':
            Elan.objects.filter(pk=self.pk).update(
                bitis_tarixi=timezone.now() + timedelta(days=30)
            )

    def is_vip_aktiv(self):
        if self.vip_status == 'normal':
            return False
        if self.vip_bitis and self.vip_bitis < timezone.now():
            return False
        return True

    def __str__(self):
        return f"#{self.nomre} {self.bashliq}"

    class Meta:
        ordering = ['-vip_siralama', '-yaradildi']
        verbose_name_plural = "Elanlar"


class ElanShekil(models.Model):
    elan = models.ForeignKey(Elan, on_delete=models.CASCADE, related_name='shekillar')
    shekil = models.ImageField(upload_to='elanlar/')
    esas = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.elan.bashliq} - şəkil"


class Profil(models.Model):
    istifadeci = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    ad = models.CharField(max_length=50, blank=True)
    soyad = models.CharField(max_length=50, blank=True)
    telefon = models.CharField(max_length=20, blank=True)
    sheher = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatarlar/', blank=True, null=True)
    balans = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    yaradildi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.istifadeci.username


class Favorit(models.Model):
    istifadeci = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritler')
    elan = models.ForeignKey(Elan, on_delete=models.CASCADE, related_name='favoritler')
    yaradildi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('istifadeci', 'elan')


class Mesaj(models.Model):
    gonderici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gonderilen_mesajlar')
    alici = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alinan_mesajlar')
    elan = models.ForeignKey(Elan, on_delete=models.CASCADE, related_name='mesajlar', null=True, blank=True)
    metn = models.TextField()
    oxundu = models.BooleanField(default=False, db_index=True)
    yaradildi = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['yaradildi']

    def __str__(self):
        return f"{self.gonderici} → {self.alici}"


class BankMelumat(models.Model):
    bank_adi = models.CharField(max_length=100, default='ABB Bank')
    kart_nomresi = models.CharField(max_length=50, blank=True)
    kart_sahibi = models.CharField(max_length=100, default='Prousta MMC')
    aktiv = models.BooleanField(default=True)

    def __str__(self):
        return f'{self.bank_adi} — {self.kart_nomresi}'

    class Meta:
        verbose_name = 'Bank Məlumatı'
        verbose_name_plural = 'Bank Məlumatları'


class Odenis(models.Model):
    STATUS = [
        ('gozlemede', 'Gözləmədə'),
        ('tesdiq_edildi', 'Təsdiq edildi'),
        ('legv_edildi', 'Ləğv edildi'),
    ]
    NOV = [
        ('vip', 'VIP Elan'),
        ('super_vip', 'Super VIP Elan'),
        ('balans', 'Balans Artırma'),
    ]

    istifadeci = models.ForeignKey(User, on_delete=models.CASCADE, related_name='odenisler')
    elan = models.ForeignKey(Elan, on_delete=models.SET_NULL, null=True, blank=True)
    nov = models.CharField(max_length=20, choices=NOV)
    mebleg = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS, default='gozlemede')
    qebz = models.ImageField(upload_to='qebzler/', null=True, blank=True)
    qeyd = models.TextField(blank=True)
    yaradildi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.istifadeci} - {self.nov} - {self.mebleg}₼"

    class Meta:
        verbose_name_plural = "Ödənişlər"
