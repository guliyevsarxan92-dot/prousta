from rest_framework import serializers
from django.contrib.auth.models import User
from .models import (
    Elan, ElanShekil, Kategori, Profil, Favorit, Mesaj,
    Odenis, BankMelumat, VipPaket, ReklamBanner
)


class ProfilSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profil
        fields = ['ad', 'soyad', 'telefon', 'sheher', 'avatar', 'balans']
        read_only_fields = ['balans']


class UserSerializer(serializers.ModelSerializer):
    profil = ProfilSerializer(read_only=True)
    has_password = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 'profil', 'has_password']

    def get_has_password(self, obj):
        return obj.has_usable_password()


class AltKategoriSerializer(serializers.ModelSerializer):
    elan_sayi = serializers.SerializerMethodField()

    class Meta:
        model = Kategori
        fields = ['id', 'ad', 'slug', 'ikon', 'elan_sayi']

    def get_elan_sayi(self, obj):
        return Elan.objects.filter(kategori=obj, status='aktiv').count()


class KategoriSerializer(serializers.ModelSerializer):
    alt_kateqoriyalar = AltKategoriSerializer(many=True, read_only=True)
    elan_sayi = serializers.SerializerMethodField()

    class Meta:
        model = Kategori
        fields = ['id', 'ad', 'slug', 'ikon', 'alt_kateqoriyalar', 'elan_sayi']

    def get_elan_sayi(self, obj):
        from django.db.models import Q
        return Elan.objects.filter(
            status='aktiv'
        ).filter(
            Q(kategori=obj) | Q(kategori__ust_kategori=obj)
        ).count()


class ElanShekilSerializer(serializers.ModelSerializer):
    shekil_url = serializers.SerializerMethodField()

    class Meta:
        model = ElanShekil
        fields = ['id', 'shekil_url', 'esas']

    def get_shekil_url(self, obj):
        if not obj.shekil:
            return None
        url = obj.shekil.url
        request = self.context.get('request')
        if request and not url.startswith(('http://', 'https://')):
            return request.build_absolute_uri(url)
        return url


class ElanListSerializer(serializers.ModelSerializer):
    esas_shekil = serializers.SerializerMethodField()
    kategori_ad = serializers.CharField(source='kategori.ad', read_only=True)
    kategori_slug = serializers.CharField(source='kategori.slug', read_only=True)
    is_favorit = serializers.SerializerMethodField()

    class Meta:
        model = Elan
        fields = [
            'id', 'nomre', 'bashliq', 'qiymet', 'status',
            'vip_status', 'sheher', 'telefon', 'baxish_sayi',
            'zeng_sayi', 'wp_sayi',
            'yaradildi', 'esas_shekil', 'kategori_ad', 'kategori_slug',
            'is_favorit'
        ]

    def get_esas_shekil(self, obj):
        request = self.context.get('request')
        shekiller = getattr(obj, '_prefetched_objects_cache', {}).get('shekillar')
        if shekiller is not None:
            shekil = next((s for s in shekiller if s.esas), shekiller[0] if shekiller else None)
        else:
            shekil = obj.shekillar.filter(esas=True).first() or obj.shekillar.first()

        if shekil and shekil.shekil:
            url = shekil.shekil.url
            if request and not url.startswith(('http://', 'https://')):
                return request.build_absolute_uri(url)
            return url
        return None

    def get_is_favorit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            user_favs = getattr(request, '_user_favorite_ids', None)
            if user_favs is not None:
                return obj.id in user_favs
            return Favorit.objects.filter(istifadeci=request.user, elan=obj).exists()
        return False


class ElanDetailSerializer(serializers.ModelSerializer):
    shekillar = ElanShekilSerializer(many=True, read_only=True)
    kategori_ad = serializers.CharField(source='kategori.ad', read_only=True)
    kategori_slug = serializers.CharField(source='kategori.slug', read_only=True)
    istifadeci_info = serializers.SerializerMethodField()
    is_favorit = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    class Meta:
        model = Elan
        fields = [
            'id', 'nomre', 'bashliq', 'acaqlama', 'qiymet',
            'status', 'vip_status', 'vip_bitis', 'sheher', 'telefon',
            'baxish_sayi', 'zeng_sayi', 'wp_sayi', 'yaradildi', 'yenilendi',
            'kategori', 'kategori_ad', 'kategori_slug', 'shekillar',
            'istifadeci_info', 'is_favorit', 'is_owner'
        ]

    def get_istifadeci_info(self, obj):
        user = obj.istifadeci
        profil = getattr(user, 'profil', None)
        request = self.context.get('request')
        avatar_url = None
        if profil and profil.avatar:
            url = profil.avatar.url
            if request and not url.startswith(('http://', 'https://')):
                avatar_url = request.build_absolute_uri(url)
            else:
                avatar_url = url

        ad_soyad = ""
        if profil and (profil.ad or profil.soyad):
            ad_soyad = f"{profil.ad} {profil.soyad}".strip()
        if not ad_soyad:
            ad_soyad = user.get_full_name() or user.username

        return {
            'id': user.id,
            'username': user.username,
            'ad_soyad': ad_soyad,
            'avatar': avatar_url,
            'telefon': profil.telefon if profil else (obj.telefon or ""),
            'yaradildi': user.date_joined,
        }

    def get_is_favorit(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return Favorit.objects.filter(istifadeci=request.user, elan=obj).exists()
        return False

    def get_is_owner(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.istifadeci_id == request.user.id
        return False


class MesajSerializer(serializers.ModelSerializer):
    gonderici_username = serializers.CharField(source='gonderici.username', read_only=True)
    gonderici_ad = serializers.SerializerMethodField()
    is_mine = serializers.SerializerMethodField()

    class Meta:
        model = Mesaj
        fields = [
            'id', 'gonderici', 'gonderici_username', 'gonderici_ad',
            'alici', 'elan', 'metn', 'oxundu', 'yaradildi', 'is_mine'
        ]
        read_only_fields = ['gonderici', 'oxundu', 'yaradildi']

    def get_gonderici_ad(self, obj):
        profil = getattr(obj.gonderici, 'profil', None)
        if profil and (profil.ad or profil.soyad):
            return f"{profil.ad} {profil.soyad}".strip()
        return obj.gonderici.get_full_name() or obj.gonderici.username

    def get_is_mine(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.gonderici_id == request.user.id
        return False


class VipPaketSerializer(serializers.ModelSerializer):
    ustunlukler = serializers.ReadOnlyField(source='ustunlukler_list')

    class Meta:
        model = VipPaket
        fields = ['id', 'nov', 'ad', 'qiymet', 'muddet_gun', 'ustunlukler', 'aktiv', 'siralama']


class BankMelumatSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankMelumat
        fields = ['id', 'bank_adi', 'kart_nomresi', 'kart_sahibi', 'aktiv']


class OdenisSerializer(serializers.ModelSerializer):
    elan_bashliq = serializers.CharField(source='elan.bashliq', read_only=True)
    nov_display = serializers.CharField(source='get_nov_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    qebz_url = serializers.SerializerMethodField()

    class Meta:
        model = Odenis
        fields = [
            'id', 'elan', 'elan_bashliq', 'nov', 'nov_display',
            'mebleg', 'status', 'status_display', 'qebz_url', 'qeyd', 'yaradildi'
        ]

    def get_qebz_url(self, obj):
        if not obj.qebz:
            return None
        url = obj.qebz.url
        request = self.context.get('request')
        if request and not url.startswith(('http://', 'https://')):
            return request.build_absolute_uri(url)
        return url


class ReklamBannerSerializer(serializers.ModelSerializer):
    shekil_url = serializers.SerializerMethodField()

    class Meta:
        model = ReklamBanner
        fields = ['id', 'movqe', 'bashliq', 'link', 'shekil_url', 'animasiya_effekti']

    def get_shekil_url(self, obj):
        if not obj.shekil:
            return None
        url = obj.shekil.url
        request = self.context.get('request')
        if request and not url.startswith(('http://', 'https://')):
            return request.build_absolute_uri(url)
        return url
