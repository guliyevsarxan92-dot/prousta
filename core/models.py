from django.db import models
from django.contrib.auth.models import User

class Kategori(models.Model):
    ad = models.CharField(max_length=100)
    ikon = models.CharField(max_length=50, blank=True)
    slug = models.SlugField(unique=True)

    def __str__(self):
        return self.ad

    class Meta:
        verbose_name_plural = "Kateqoriyalar"


class Elan(models.Model):
    VEZIYYET = [
        ('yeni', 'Yeni'),
        ('ishlenmish', 'İşlənmiş'),
    ]
    STATUS = [
        ('aktiv', 'Aktiv'),
        ('gozlemede', 'Gözləmədə'),
        ('deaktiv', 'Deaktiv'),
    ]

    istifadeci = models.ForeignKey(User, on_delete=models.CASCADE, related_name='elanlar')
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True)
    bashliq = models.CharField(max_length=200)
    acaqlama = models.TextField()
    qiymet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    veziyyet = models.CharField(max_length=20, choices=VEZIYYET, default='yeni')
    status = models.CharField(max_length=20, choices=STATUS, default='gozlemede')
    sheher = models.CharField(max_length=100, default='Bakı')
    baxish_sayi = models.PositiveIntegerField(default=0)
    yaradildi = models.DateTimeField(auto_now_add=True)
    yenilendi = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.bashliq

    class Meta:
        ordering = ['-yaradildi']
        verbose_name_plural = "Elanlar"


class ElanShekil(models.Model):
    elan = models.ForeignKey(Elan, on_delete=models.CASCADE, related_name='shekillar')
    shekil = models.ImageField(upload_to='elanlar/')
    əsas = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.elan.bashliq} - şəkil"


class Profil(models.Model):
    istifadeci = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profil')
    telefon = models.CharField(max_length=20, blank=True)
    sheher = models.CharField(max_length=100, blank=True)
    avatar = models.ImageField(upload_to='avatarlar/', blank=True, null=True)
    yaradildi = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.istifadeci.username


class Favorit(models.Model):
    istifadeci = models.ForeignKey(User, on_delete=models.CASCADE, related_name='favoritler')
    elan = models.ForeignKey(Elan, on_delete=models.CASCADE, related_name='favoritler')
    yaradildi = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('istifadeci', 'elan')

    def __str__(self):
        return f"{self.istifadeci.username} → {self.elan.bashliq}"


class ElanTelefon(models.Model):
    elan = models.OneToOneField(Elan, on_delete=models.CASCADE, related_name='telefon')
    nomre = models.CharField(max_length=20)

    def __str__(self):
        return self.nomre
