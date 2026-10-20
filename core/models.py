import re
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


_AZ_MAP = str.maketrans({
    'ə': 'e', 'Ə': 'e',
    'ı': 'i', 'I': 'i', 'İ': 'i',
    'ö': 'o', 'Ö': 'o',
    'ü': 'u', 'Ü': 'u',
    'ç': 'c', 'Ç': 'c',
    'ş': 's', 'Ş': 's',
    'ğ': 'g', 'Ğ': 'g',
})


def slug_az(text: str, max_length: int = 50) -> str:
    """Azərbaycan dilində başlıqdan SEO-dost slug yaradır."""
    if not text:
        return ''
    text = text.translate(_AZ_MAP).lower()
    text = re.sub(r'[^a-z0-9]+', '-', text)
    text = text.strip('-')
    if len(text) > max_length:
        text = text[:max_length].rsplit('-', 1)[0] or text[:max_length]
    return text


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
        ('vip', 'VIP'),
        ('super_vip', 'Super VIP'),
    ]
    VIP_ORDER = {
        'super_vip': 1,
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
    vip_yenilendi = models.DateTimeField(null=True, blank=True, db_index=True)
    bitis_tarixi = models.DateTimeField(null=True, blank=True)
    sheher = models.CharField(max_length=100, default='Bakı')
    telefon = models.CharField(max_length=20, blank=True)
    baxish_sayi = models.PositiveIntegerField('Baxış Sayı', default=0)
    zeng_sayi = models.PositiveIntegerField('Zəng Klikləri', default=0)
    wp_sayi = models.PositiveIntegerField('WhatsApp Klikləri', default=0)
    ireli_cekildi = models.DateTimeField('İrəli Çəkildi', null=True, blank=True, db_index=True)
    ireli_cekilme_sayi = models.PositiveIntegerField('İrəli Çəkilmə Sayı', default=0)
    yaradildi = models.DateTimeField(auto_now_add=True)
    yenilendi = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.nomre:
            for _ in range(5):
                candidate = uuid.uuid4().hex[:8].upper()
                if not Elan.objects.filter(nomre=candidate).exists():
                    self.nomre = candidate
                    break
            else:
                self.nomre = uuid.uuid4().hex[:10].upper()
        now = timezone.now()
        if self.vip_status in ('vip', 'super_vip'):
            if not self.vip_bitis or self.vip_bitis <= now:
                days = 30 if self.vip_status == 'super_vip' else 10
                try:
                    p = VipPaket.objects.filter(nov=self.vip_status, aktiv=True).first()
                    if p:
                        days = p.muddet_gun
                except Exception:
                    pass
                self.vip_bitis = now + timedelta(days=days)
            if not self.vip_yenilendi:
                self.vip_yenilendi = now
            self.vip_siralama = self.VIP_ORDER.get(self.vip_status, 1)
        else:
            self.vip_status = 'normal'
            self.vip_siralama = 0
        super().save(*args, **kwargs)
        if not self.bitis_tarixi and self.status == 'aktiv':
            now_plus_30 = timezone.now() + timedelta(days=30)
            Elan.objects.filter(pk=self.pk).update(bitis_tarixi=now_plus_30)
            self.bitis_tarixi = now_plus_30

    def is_vip_aktiv(self):
        if self.vip_status == 'normal':
            return False
        if not self.vip_bitis or self.vip_bitis <= timezone.now():
            return False
        return True

    @property
    def slug(self) -> str:
        """Başlıqdan avtomatik yaranan SEO slug (maks. 60 simvol, -baki suffix ilə)."""
        base = slug_az(self.bashliq or '', max_length=50)
        if base:
            return f'{base}-baki'
        return 'elan-baki'

    def get_absolute_url(self) -> str:
        return f'/elan/{self.pk}-{self.slug}/'

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

    @property
    def card_url(self):
        """Ana səhifə və axtarış kartları üçün optimallaşdırılmış WebP URL (~15-25 KB)."""
        if not self.shekil:
            return ''
        try:
            from core.image_optimizer import get_card_image_url
            return get_card_image_url(self.shekil.url)
        except Exception:
            return getattr(self.shekil, 'url', '')

    @property
    def detail_url(self):
        """Elan daxili əsas şəkil üçün Full HD keyfiyyətli WebP URL (~60-90 KB)."""
        if not self.shekil:
            return ''
        try:
            from core.image_optimizer import get_detail_image_url
            return get_detail_image_url(self.shekil.url)
        except Exception:
            return getattr(self.shekil, 'url', '')

    @property
    def thumb_url(self):
        """Qalereya kiçik ikonları üçün WebP URL (~5-10 KB)."""
        if not self.shekil:
            return ''
        try:
            from core.image_optimizer import get_thumb_image_url
            return get_thumb_image_url(self.shekil.url)
        except Exception:
            return getattr(self.shekil, 'url', '')

    def save(self, *args, **kwargs):
        # Yeni şəkil yüklənərkən yaddaşda avtomatik sıxılma və ölçüləndirmə
        if self.shekil and hasattr(self.shekil, 'file') and not self.pk:
            try:
                from core.image_optimizer import compress_uploaded_image
                self.shekil = compress_uploaded_image(self.shekil)
            except Exception:
                pass
        super().save(*args, **kwargs)


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


class Problem(models.Model):
    bashliq = models.CharField(max_length=200)
    slug = models.SlugField(max_length=100, unique=True)
    metn = models.TextField(help_text='Problem haqqında ətraflı HTML mətn')
    kategori = models.ForeignKey(Kategori, on_delete=models.SET_NULL, null=True, blank=True, related_name='problemler')
    seo_title = models.CharField(max_length=200, blank=True)
    seo_description = models.CharField(max_length=300, blank=True)
    aktiv = models.BooleanField(default=True, db_index=True)
    yaradildi = models.DateTimeField(auto_now_add=True)
    yenilendi = models.DateTimeField(auto_now=True)

    def get_absolute_url(self):
        return f'/problemler/{self.slug}/'

    def __str__(self):
        return self.bashliq

    class Meta:
        ordering = ['-yaradildi']
        verbose_name = 'Problem'
        verbose_name_plural = 'Problemlər'


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
        ('ireli_cek', 'İrəli Çəkmə'),
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


class ReklamBanner(models.Model):
    MOVQELER = [
        ('ust', 'Üst'),
        ('sol', 'Sol Yan'),
        ('sag', 'Sağ Yan'),
        ('orta', 'Orta'),
    ]

    ANIMASIYA_CHOICES = [
        ('none', 'Standart (Statik / Normal)'),
        ('zoom', 'Zərif Yaxınlaşma (Smooth Zoom on Hover)'),
        ('glow', 'İşıqlı Parıltı (Glow / Parlaq animasiya)'),
        ('pulse', 'Nəbzlənmə (Pulse animasiya)'),
    ]

    movqe = models.CharField('Mövqe', max_length=20, choices=MOVQELER, unique=True)
    bashliq = models.CharField('Başlıq / Müştəri adı', max_length=150, blank=True)
    link = models.URLField('Keçid Linki (URL)', blank=True, help_text='Məsələn: https://example.com və ya https://wa.me/99450xxxxxxx')
    shekil = models.ImageField('Banner Şəkli / GIF', upload_to='bannerler/', blank=True, null=True, help_text='Şəkil və ya GIF animasiya (Üst: 1920x400, Yan: 160x600 və s.)')
    video = models.FileField('Video Faylı (MP4 / WebM)', upload_to='bannerler/videolar/', blank=True, null=True, help_text='Animasiyalı video banner üçün MP4 və ya WebM faylı (avtomatik və səssiz oxunur)')
    video_url = models.URLField('Video Linki (Birbaşa MP4 / WebM URL)', blank=True, help_text='Cloudinary və ya digər birbaşa video linki')
    html_kod = models.TextField('HTML / Animasiya / AdSense Kodu', blank=True, help_text='HTML5 Canvas, CSS animasiya, Lottie, SVG və ya script kodu')
    animasiya_effekti = models.CharField('Animasiya Effekti', max_length=20, choices=ANIMASIYA_CHOICES, default='zoom')
    aktiv = models.BooleanField('Aktivdir', default=True, db_index=True)
    bos_olduqda_gizlet = models.BooleanField(
        'Reklam yoxdursa banneri gizlət',
        default=False,
        help_text='İşarələnsə, bu mövqedə aktiv reklam (şəkil/video) olmadıqda banner saytda heç bir yer tutmayacaq və tam gizlənəcək'
    )
    klik_sayi = models.PositiveIntegerField('Klik Sayı', default=0, db_index=True, help_text='Bannerə edilən toplam keçid sayı')
    baxis_sayi = models.PositiveIntegerField('Baxış Sayı', default=0, help_text='Bannerin saytda nümayiş sayı')
    bitis_tarixi = models.DateTimeField('Bitmə tarixi', null=True, blank=True, help_text='Boş buraxsanız müddətsiz aktiv olar')
    yaradildi = models.DateTimeField(auto_now_add=True)
    yenilendi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Reklam Banneri'
        verbose_name_plural = 'Reklam Bannerləri'

    def __str__(self):
        return f"{self.get_movqe_display()} — {self.bashliq or 'Başlıqsız'}"

    @property
    def ctr(self):
        if self.baxis_sayi > 0:
            return round((self.klik_sayi / self.baxis_sayi) * 100, 2)
        return 0.0

    @property
    def ctr_formatted(self):
        return f"{self.ctr:.2f}%"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        try:
            from django.core.cache import cache
            cache.delete('reklam_bannerleri')
        except Exception:
            pass

    def delete(self, *args, **kwargs):
        super().delete(*args, **kwargs)
        try:
            from django.core.cache import cache
            cache.delete('reklam_bannerleri')
        except Exception:
            pass


class BannerKlik(models.Model):
    CIHAZ_CHOICES = [
        ('mobil', 'Mobil'),
        ('desktop', 'Desktop'),
        ('planset', 'Planşet'),
        ('diger', 'Digər'),
    ]

    banner = models.ForeignKey(
        ReklamBanner,
        on_delete=models.CASCADE,
        related_name='klikler',
        verbose_name='Banner'
    )
    ip_unvan = models.GenericIPAddressField('IP Ünvanı', null=True, blank=True)
    cihaz = models.CharField('Cihaz Növü', max_length=20, choices=CIHAZ_CHOICES, default='desktop')
    user_agent = models.CharField('Brauzer / User-Agent', max_length=500, blank=True)
    referer = models.URLField('Keçid Mənbəyi (Referer)', max_length=500, blank=True)
    yaradildi = models.DateTimeField('Klik Tarixi', auto_now_add=True, db_index=True)

    class Meta:
        verbose_name = 'Banner Kliki'
        verbose_name_plural = 'Banner Klikləri'
        ordering = ['-yaradildi']

    def __str__(self):
        return f"{self.banner.bashliq or self.banner.get_movqe_display()} — {self.yaradildi.strftime('%d.%m.%Y %H:%M')}"


class VipPaket(models.Model):
    PAKET_CHOICES = [
        ('vip', 'VIP'),
        ('super_vip', 'Super VIP'),
    ]

    nov = models.CharField('VIP Növü', max_length=20, choices=PAKET_CHOICES, unique=True)
    ad = models.CharField('Paket Başlığı', max_length=100)
    qiymet = models.DecimalField('Aylıq / Paket Qiyməti (AZN)', max_digits=10, decimal_places=2, default=Decimal('5.00'))
    muddet_gun = models.PositiveIntegerField('Aktivlik Müddəti (gün)', default=30, help_text='Məsələn: 30 gün (1 ay), 10 gün və s.')
    ustunlukler = models.TextField('Üstünlüklər (hər sətirdə bir maddə)', blank=True, help_text='Hər sətrə bir üstünlük yazın')
    aktiv = models.BooleanField('Aktivdir', default=True)
    siralama = models.PositiveSmallIntegerField('Sıralama', default=1)
    yenilendi = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'VIP Tarifi'
        verbose_name_plural = 'VIP Tarifləri və Qiymətlər'
        ordering = ['siralama', 'qiymet']

    def __str__(self):
        return f"{self.ad} ({self.get_nov_display()}) — {self.qiymet} ₼ / {self.muddet_gun} gün"

    @property
    def ustunlukler_list(self):
        if not self.ustunlukler:
            return []
        return [s.strip() for s in self.ustunlukler.splitlines() if s.strip()]

    @classmethod
    def get_paket(cls, nov):
        defaults = {
            'vip': {
                'ad': 'VIP Elan',
                'qiymet': Decimal('3.00'),
                'muddet_gun': 10,
                'siralama': 1,
                'ustunlukler': 'Bütün elanlar siyahısında və axtarışlarda ən öndə\nXüsusi qızılı nişan ilə fərqlənmə\nDaha çox baxış və zəng',
            },
            'super_vip': {
                'ad': 'Super VIP Elan',
                'qiymet': Decimal('8.00'),
                'muddet_gun': 30,
                'siralama': 2,
                'ustunlukler': 'Ana səhifədə və bütün kateqoriyalarda ən öndə\n30 gün (1 ay) fasiləsiz aktivlik\nƏn yüksək müştəri axını və zənglər',
            },
        }
        try:
            p = cls.objects.filter(nov=nov, aktiv=True).first()
            if p:
                return p
            p, _ = cls.objects.get_or_create(nov=nov, defaults=defaults.get(nov, {}))
            return p
        except Exception:
            d = defaults.get(nov, {'qiymet': Decimal('5.00'), 'muddet_gun': 30, 'ad': nov.upper()})
            return cls(nov=nov, **d)

    @classmethod
    def get_all_aktiv(cls):
        try:
            paketler = list(cls.objects.filter(aktiv=True).order_by('siralama'))
            if not paketler:
                for nov in ('vip', 'super_vip'):
                    cls.get_paket(nov)
                paketler = list(cls.objects.filter(aktiv=True).order_by('siralama'))
            return paketler
        except Exception:
            return []




class Shikayet(models.Model):
    """İstifadəçilərin elan və ya digər istifadəçi barədə şikayəti (Google Play UGC tələbi)."""
    SEBEB_CHOICES = [
        ('spam', 'Spam / reklam'),
        ('saxta', 'Saxta elan / fırıldaqçılıq'),
        ('uygunsuz', 'Uyğunsuz və ya təhqiramiz məzmun'),
        ('tehdid', 'Təhdid / təqib'),
        ('diger', 'Digər'),
    ]
    STATUS_CHOICES = [
        ('yeni', 'Yeni'),
        ('baxildi', 'Baxıldı'),
        ('hell_edildi', 'Həll edildi'),
        ('redd_edildi', 'Rədd edildi'),
    ]

    sikayet_eden = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='etdiyi_shikayetler')
    elan = models.ForeignKey(Elan, on_delete=models.SET_NULL, null=True, blank=True, related_name='shikayetler')
    istifadeci = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='haqqinda_shikayetler', verbose_name='Şikayət edilən istifadəçi'
    )
    sebeb = models.CharField('Səbəb', max_length=20, choices=SEBEB_CHOICES, default='diger')
    qeyd = models.TextField('Qeyd', blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='yeni', db_index=True)
    yaradildi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Şikayət'
        verbose_name_plural = 'Şikayətlər'
        ordering = ['-yaradildi']

    def __str__(self):
        hedef = f"Elan #{self.elan_id}" if self.elan_id else f"İstifadəçi #{self.istifadeci_id}"
        return f"{hedef} — {self.get_sebeb_display()}"


class Bloklama(models.Model):
    """İstifadəçinin digər istifadəçini bloklaması: elanları və mesajları gizlədilir."""
    bloklayan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='blokladiqlari')
    bloklanan = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bloklayanlar')
    yaradildi = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Bloklama'
        verbose_name_plural = 'Bloklamalar'
        unique_together = ('bloklayan', 'bloklanan')

    def __str__(self):
        return f"{self.bloklayan} ⛔ {self.bloklanan}"

    @classmethod
    def bloklanmis_idler(cls, user):
        """İstifadəçinin blokladığı və onu bloklayan istifadəçilərin ID-ləri."""
        if not user or not user.is_authenticated:
            return set()
        a = cls.objects.filter(bloklayan=user).values_list('bloklanan_id', flat=True)
        b = cls.objects.filter(bloklanan=user).values_list('bloklayan_id', flat=True)
        return set(a) | set(b)
