import re
from datetime import timedelta
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Max, Count, F
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from .models import (
    Elan, ElanShekil, Kategori, Profil, Favorit, Mesaj,
    Odenis, BankMelumat, VipPaket, ReklamBanner, Shikayet, Bloklama, _AZ_MAP
)
from .api_serializers import (
    UserSerializer, ProfilSerializer, KategoriSerializer,
    ElanListSerializer, ElanDetailSerializer, MesajSerializer,
    VipPaketSerializer, BankMelumatSerializer, OdenisSerializer,
    ReklamBannerSerializer
)
from .views import _aciqlama_qadaga_yoxla, apply_fair_rotation
from .watermark import filigran_yoxla
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from django.conf import settings
import secrets


# -----------------------------------------------------------------------------
# AUTH VIEWS
# -----------------------------------------------------------------------------

class LoginApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username', '').strip()
        password = request.data.get('password', '').strip()

        if not username_or_email or not password:
            return Response(
                {'error': 'İstifadəçi adı və ya email və şifrə daxil edilməlidir.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # Əgər email ilə daxil olursa, username-i tapırıq
        user = None
        if '@' in username_or_email:
            user_obj = User.objects.filter(email__iexact=username_or_email).first()
            if user_obj:
                user = authenticate(username=user_obj.username, password=password)
        else:
            user = authenticate(username=username_or_email, password=password)

        if not user:
            return Response(
                {'error': 'İstifadəçi adı və ya şifrə yanlışdır.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Uğurla daxil oldunuz.'
        })


class RegisterApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username', '').strip().lower()
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '').strip()
        ad = request.data.get('ad', '').strip()
        soyad = request.data.get('soyad', '').strip()
        telefon = request.data.get('telefon', '').strip()
        sheher = request.data.get('sheher', 'Bakı').strip()

        if not username or not password:
            return Response({'error': 'İstifadəçi adı və şifrə mütləqdir.'}, status=status.HTTP_400_BAD_REQUEST)

        if len(password) < 6:
            return Response({'error': 'Şifrə ən azı 6 simvol olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)

        if User.objects.filter(username=username).exists():
            return Response({'error': 'Bu istifadəçi adı artıq götürülüb.'}, status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email=email).exists():
            return Response({'error': 'Bu email artıq qeydiyyatdan keçib.'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                first_name=ad,
                last_name=soyad
            )
            profil, _ = Profil.objects.get_or_create(istifadeci=user)
            profil.ad = ad
            profil.soyad = soyad
            profil.telefon = telefon
            profil.sheher = sheher
            profil.save()

            token, _ = Token.objects.get_or_create(user=user)

        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Qeydiyyat uğurla tamamlandı.'
        }, status=status.HTTP_201_CREATED)


class GoogleLoginApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        id_token_str = request.data.get('id_token', '').strip()
        if not id_token_str:
            return Response({'error': 'id_token tələb olunur.'}, status=status.HTTP_400_BAD_REQUEST)

        client_id = getattr(settings, "GOOGLE_WEB_CLIENT_ID", "") or settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        try:
            info = google_id_token.verify_oauth2_token(
                id_token_str, google_requests.Request(), client_id
            )
        except Exception as e:
            return Response({'error': 'Google token etibarsızdır.', 'detail': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

        email = (info.get("email") or "").lower().strip()
        if not email or not info.get("email_verified", False):
            return Response({'error': 'Google email təsdiqlənməyib.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = User.objects.filter(email__iexact=email).first()
        if user is None:
            base = (email.split("@")[0] or f"user{secrets.token_hex(3)}")[:26]
            username = base
            suffix = 0
            while User.objects.filter(username=username).exists():
                suffix += 1
                username = f"{base}{suffix}"
            user = User.objects.create_user(
                username=username,
                email=email,
                first_name=(info.get("given_name") or "")[:30],
                last_name=(info.get("family_name") or "")[:150],
            )
            user.set_unusable_password()
            user.save()

            profil, _ = Profil.objects.get_or_create(istifadeci=user)
            profil.ad = user.first_name or ""
            profil.soyad = user.last_name or ""
            profil.save()

        token, _ = Token.objects.get_or_create(user=user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Google ilə uğurla daxil oldunuz.'
        })


class LogoutApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Uğurla çıxış edildi.'})


class DeleteAccountApiView(APIView):
    """Hesabın və bağlı bütün məlumatların (elanlar, mesajlar, favoritlər, profil) birdəfəlik silinməsi."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        user = request.user
        if user.is_staff or user.is_superuser:
            return Response(
                {'error': 'Admin hesabı tətbiqdən silinə bilməz.'},
                status=status.HTTP_403_FORBIDDEN
            )

        if user.has_usable_password():
            password = request.data.get('password', '')
            if not password or not user.check_password(password):
                return Response(
                    {'error': 'Şifrə yanlışdır.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        elif str(request.data.get('confirm', '')).strip().upper() != 'SIL':
            return Response(
                {'error': 'Təsdiq üçün "SIL" yazın.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        with transaction.atomic():
            # Şəkil fayllarını diskdən də silirik
            for shekil in ElanShekil.objects.filter(elan__istifadeci=user):
                if shekil.shekil:
                    shekil.shekil.delete(save=False)
            profil = getattr(user, 'profil', None)
            if profil and profil.avatar:
                profil.avatar.delete(save=False)
            user.delete()  # CASCADE: Token, Profil, Elan, Mesaj, Favorit, Bloklama

        return Response({'message': 'Hesabınız və bütün məlumatlarınız silindi.'})


class ProfileApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get(self, request):
        user_serializer = UserSerializer(request.user, context={'request': request})
        return Response(user_serializer.data)

    def patch(self, request):
        user = request.user
        profil, _ = Profil.objects.get_or_create(istifadeci=user)

        first_name = request.data.get('ad')
        last_name = request.data.get('soyad')
        telefon = request.data.get('telefon')
        sheher = request.data.get('sheher')
        avatar = request.FILES.get('avatar')

        if first_name is not None:
            user.first_name = first_name
            profil.ad = first_name
        if last_name is not None:
            user.last_name = last_name
            profil.soyad = last_name
        if telefon is not None:
            profil.telefon = telefon
        if sheher is not None:
            profil.sheher = sheher
        if avatar is not None:
            profil.avatar = avatar

        user.save()
        profil.save()

        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'user': user_serializer.data,
            'message': 'Profil məlumatları yeniləndi.'
        })


# -----------------------------------------------------------------------------
# CATEGORIES VIEW
# -----------------------------------------------------------------------------

class CategoriesApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
        serializer = KategoriSerializer(kateqoriyalar, many=True, context={'request': request})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# ELANLAR (ADS) VIEWS
# -----------------------------------------------------------------------------

class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class ElanlarListApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        q = request.GET.get('q', '').strip()
        kategori_slug = request.GET.get('kategori', '').strip()
        seher = request.GET.get('seher', '').strip()
        vip_only = request.GET.get('vip_only', '').lower() in ['true', '1']
        user_id = request.GET.get('user_id', '').strip()
        seed = request.GET.get('seed', 'mobile')

        qs = (
            Elan.objects.filter(status='aktiv')
            .select_related('kategori')
            .prefetch_related('shekillar')
        )

        if user_id and user_id.isdigit():
            qs = qs.filter(istifadeci_id=int(user_id))

        bloklanmis = Bloklama.bloklanmis_idler(request.user)
        if bloklanmis:
            qs = qs.exclude(istifadeci_id__in=bloklanmis)

        if q:
            # Azərbaycan hərfləri ilə həm əsli, həm transliterasiyalı axtarış (məs: kombi ustasi <-> kombi ustası)
            q_az = q.translate(_AZ_MAP)
            terms = {q, q_az}
            q_filter = Q()
            for term in terms:
                q_filter |= (
                    Q(bashliq__icontains=term) |
                    Q(acaqlama__icontains=term) |
                    Q(nomre__icontains=term) |
                    Q(kategori__ad__icontains=term) |
                    Q(kategori__ust_kategori__ad__icontains=term)
                )
            qs = qs.filter(q_filter)

        if kategori_slug:
            qs = qs.filter(
                Q(kategori__slug=kategori_slug) |
                Q(kategori__ust_kategori__slug=kategori_slug)
            )

        if seher and seher != 'Bütün Azərbaycan':
            qs = qs.filter(sheher__iexact=seher)

        if vip_only:
            qs = qs.filter(vip_status__in=['vip', 'super_vip'])

        qs = apply_fair_rotation(qs, seed)

        if request.user.is_authenticated:
            request._user_favorite_ids = set(
                Favorit.objects.filter(istifadeci=request.user).values_list('elan_id', flat=True)
            )

        paginator = StandardResultsSetPagination()
        page_results = paginator.paginate_queryset(qs, request)
        serializer = ElanListSerializer(page_results, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ElanDetailApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        elan = get_object_or_404(
            Elan.objects.select_related('kategori', 'istifadeci__profil').prefetch_related('shekillar'),
            pk=pk
        )

        # Baxış sayını artırırıq
        Elan.objects.filter(pk=pk).update(baxish_sayi=elan.baxish_sayi + 1)
        elan.baxish_sayi += 1

        serializer = ElanDetailSerializer(elan, context={'request': request})
        return Response(serializer.data)


class ElanCreateApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        bashliq = request.data.get('bashliq', '').strip()
        acaqlama = request.data.get('acaqlama', '').strip()
        qiymet_raw = request.data.get('qiymet', '').strip()
        kategori_id = request.data.get('kategori')
        sheher = request.data.get('sheher', 'Bakı').strip()
        telefon = request.data.get('telefon', '').strip()

        if not bashliq or len(bashliq) < 5:
            return Response({'error': 'Başlıq ən azı 5 simvol olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)

        if not acaqlama or len(acaqlama) < 15:
            return Response({'error': 'Açıqlama ən azı 15 simvol olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)

        qadaga = _aciqlama_qadaga_yoxla(acaqlama)
        if qadaga:
            return Response({'error': qadaga}, status=status.HTTP_400_BAD_REQUEST)

        qiymet = None
        if qiymet_raw:
            try:
                qiymet = Decimal(qiymet_raw)
                if qiymet < 0:
                    return Response({'error': 'Qiymət mənfi ola bilməz.'}, status=status.HTTP_400_BAD_REQUEST)
            except Exception:
                return Response({'error': 'Qiymət formatı yanlışdır.'}, status=status.HTTP_400_BAD_REQUEST)

        # Telefon nömrəsi yoxlanışı (9 rəqəm və ya standart)
        tel_digits = re.sub(r'\D', '', telefon)
        if tel_digits.startswith('994') and len(tel_digits) == 12:
            tel_digits = tel_digits[3:]
        elif tel_digits.startswith('0') and len(tel_digits) == 10:
            tel_digits = tel_digits[1:]

        if len(tel_digits) != 9:
            return Response({'error': 'Telefon nömrəsi 9 rəqəmdən ibarət olmalıdır (Məs: 50 123 45 67).'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            kategori = Kategori.objects.get(pk=kategori_id)
        except (Kategori.DoesNotExist, ValueError):
            return Response({'error': 'Kateqoriya tapılmadı.'}, status=status.HTTP_400_BAD_REQUEST)

        # Eyni kateqoriyada aktiv elan yoxlanışı
        aktiv_elanlar = Elan.objects.filter(istifadeci=request.user, status__in=['aktiv', 'gozlemede'])
        if aktiv_elanlar.filter(kategori=kategori).exists():
            return Response({'error': 'Bu kateqoriyada artıq aktiv elanınız var!'}, status=status.HTTP_400_BAD_REQUEST)

        # Pulsuz elan limiti yoxlanışı
        PULSUZ_LIMIT = 4
        if aktiv_elanlar.count() >= PULSUZ_LIMIT:
            profil, _ = Profil.objects.get_or_create(istifadeci=request.user)
            if profil.balans < Decimal('1.00'):
                return Response({'error': f'Pulsuz elan limitiniz ({PULSUZ_LIMIT}) bitib. Zəhmət olmasa balansınızı artırın.'}, status=status.HTTP_400_BAD_REQUEST)

        shekillar = request.FILES.getlist('shekillar') or request.FILES.getlist('images')
        if not shekillar:
            return Response({'error': 'Ən azı 1 şəkil yükləməlisiniz.'}, status=status.HTTP_400_BAD_REQUEST)
        if len(shekillar) > 5:
            return Response({'error': 'Maksimum 5 şəkil yükləyə bilərsiniz.'}, status=status.HTTP_400_BAD_REQUEST)

        for s in shekillar:
            if s.size > 5 * 1024 * 1024:
                return Response({'error': f'{s.name} ölçüsü 5MB-dan böyük ola bilməz.'}, status=status.HTTP_400_BAD_REQUEST)
            var_filigran, xeta = filigran_yoxla(s)
            if var_filigran:
                return Response({'error': f'"{s.name}" şəklində filiqran/kənar loqo aşkar edildi: {xeta}'}, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            if aktiv_elanlar.count() >= PULSUZ_LIMIT:
                profil = Profil.objects.select_for_update().get(istifadeci=request.user)
                profil.balans -= Decimal('1.00')
                profil.save(update_fields=['balans'])

            elan = Elan.objects.create(
                istifadeci=request.user,
                kategori=kategori,
                bashliq=bashliq,
                acaqlama=acaqlama,
                qiymet=qiymet,
                sheher=sheher,
                telefon=f"0{tel_digits}",
                status='aktiv',
                bitis_tarixi=timezone.now() + timezone.timedelta(days=30)
            )

            for i, shk in enumerate(shekillar):
                ElanShekil.objects.create(
                    elan=elan,
                    shekil=shk,
                    esas=(i == 0)
                )

        serializer = ElanDetailSerializer(elan, context={'request': request})
        return Response({
            'elan': serializer.data,
            'message': 'Elanınız uğurla dərc edildi.'
        }, status=status.HTTP_201_CREATED)


class ElanUpdateApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)

        bashliq = request.data.get('bashliq')
        acaqlama = request.data.get('acaqlama')
        qiymet_raw = request.data.get('qiymet')
        sheher = request.data.get('sheher')
        telefon = request.data.get('telefon')
        kategori_id = request.data.get('kategori') or request.data.get('kategori_id')

        if bashliq:
            elan.bashliq = bashliq.strip()
        if acaqlama:
            qadaga = _aciqlama_qadaga_yoxla(acaqlama)
            if qadaga:
                return Response({'error': qadaga}, status=status.HTTP_400_BAD_REQUEST)
            elan.acaqlama = acaqlama.strip()
        if qiymet_raw is not None:
            try:
                elan.qiymet = Decimal(qiymet_raw) if str(qiymet_raw).strip() != '' else None
            except Exception:
                return Response({'error': 'Qiymət formatı yanlışdır.'}, status=status.HTTP_400_BAD_REQUEST)
        if sheher:
            elan.sheher = sheher.strip()
        if telefon:
            elan.telefon = telefon.strip()
        if kategori_id:
            try:
                kategori = Kategori.objects.filter(pk=int(kategori_id)).first()
                if kategori:
                    elan.kategori = kategori
            except Exception:
                pass

        # Mövcud silinəcək şəkillər
        silinecek_idler = request.data.getlist('silinecek_shekiller') if hasattr(request.data, 'getlist') else request.data.get('silinecek_shekiller', [])
        if silinecek_idler:
            for s_id in silinecek_idler:
                try:
                    shk = ElanShekil.objects.filter(id=int(s_id), elan=elan).first()
                    if shk:
                        if shk.shekil:
                            shk.shekil.delete(save=False)
                        shk.delete()
                except Exception:
                    pass

        # Yeni əlavə olunan şəkillər
        yeni_shekillar = request.FILES.getlist('shekillar') if hasattr(request.FILES, 'getlist') else []
        if yeni_shekillar:
            has_esas = ElanShekil.objects.filter(elan=elan, esas=True).exists()
            for i, shk in enumerate(yeni_shekillar):
                ElanShekil.objects.create(
                    elan=elan,
                    shekil=shk,
                    esas=(not has_esas and i == 0)
                )

        # Əgər əsas şəkil qalmayıbsa, birincini əsas edirik
        if not ElanShekil.objects.filter(elan=elan, esas=True).exists():
            first_shk = ElanShekil.objects.filter(elan=elan).first()
            if first_shk:
                first_shk.esas = True
                first_shk.save(update_fields=['esas'])

        elan.save()
        serializer = ElanDetailSerializer(elan, context={'request': request})
        return Response({'elan': serializer.data, 'message': 'Elan yeniləndi.'})


class ElanDeleteApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
        elan.delete()
        return Response({'message': 'Elan silindi.'})


class ElanClickApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk, nov):
        elan = get_object_or_404(Elan, pk=pk)
        if nov == 'zeng':
            Elan.objects.filter(pk=pk).update(zeng_sayi=elan.zeng_sayi + 1)
        elif nov == 'wp':
            Elan.objects.filter(pk=pk).update(wp_sayi=elan.wp_sayi + 1)
        return Response({'success': True})


class MyElanlarApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        status_filter = request.GET.get('status')
        qs = Elan.objects.filter(istifadeci=request.user).select_related('kategori').prefetch_related('shekillar')
        if status_filter:
            qs = qs.filter(status=status_filter)
        serializer = ElanListSerializer(qs.order_by('-yaradildi'), many=True, context={'request': request})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# FAVORITES VIEWS
# -----------------------------------------------------------------------------

class FavoritesListApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fav_elan_ids = Favorit.objects.filter(istifadeci=request.user).values_list('elan_id', flat=True)
        elanlar = Elan.objects.filter(id__in=fav_elan_ids).select_related('kategori').prefetch_related('shekillar')
        serializer = ElanListSerializer(elanlar, many=True, context={'request': request})
        return Response(serializer.data)


class FavoriteToggleApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk)
        fav = Favorit.objects.filter(istifadeci=request.user, elan=elan).first()
        if fav:
            fav.delete()
            is_favorit = False
            msg = 'Seçilmişlərdən çıxarıldı.'
        else:
            Favorit.objects.create(istifadeci=request.user, elan=elan)
            is_favorit = True
            msg = 'Seçilmişlərə əlavə olundu.'

        return Response({'is_favorit': is_favorit, 'message': msg})


# -----------------------------------------------------------------------------
# MESSAGES VIEWS
# -----------------------------------------------------------------------------

class ConversationsApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        # İstifadəçinin bütün mesajlaşdığı şəxslər
        mesajlar = Mesaj.objects.filter(Q(gonderici=user) | Q(alici=user)).order_by('-yaradildi')
        other_user_ids = set()
        conversations = []
        bloklanmis = Bloklama.bloklanmis_idler(user)

        for m in mesajlar:
            other_user = m.alici if m.gonderici == user else m.gonderici
            if other_user.id in bloklanmis:
                continue
            if other_user.id not in other_user_ids:
                other_user_ids.add(other_user.id)
                unread_count = Mesaj.objects.filter(gonderici=other_user, alici=user, oxundu=False).count()
                profil = getattr(other_user, 'profil', None)
                ad_soyad = ""
                if profil and (profil.ad or profil.soyad):
                    ad_soyad = f"{profil.ad} {profil.soyad}".strip()
                if not ad_soyad:
                    ad_soyad = other_user.get_full_name() or other_user.username

                avatar_url = None
                if profil and profil.avatar:
                    url = profil.avatar.url
                    avatar_url = request.build_absolute_uri(url) if not url.startswith('http') else url

                conversations.append({
                    'user_id': other_user.id,
                    'username': other_user.username,
                    'ad_soyad': ad_soyad,
                    'avatar': avatar_url,
                    'last_message': m.metn,
                    'last_message_time': m.yaradildi,
                    'unread_count': unread_count,
                    'elan_id': m.elan_id,
                })

        return Response(conversations)


class ChatMessagesApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, other_user_id):
        other_user = get_object_or_404(User, pk=other_user_id)
        # Mesajları oxunmuş kimi qeyd edirik
        Mesaj.objects.filter(gonderici=other_user, alici=request.user, oxundu=False).update(oxundu=True)

        mesajlar = Mesaj.objects.filter(
            (Q(gonderici=request.user) & Q(alici=other_user)) |
            (Q(gonderici=other_user) & Q(alici=request.user))
        ).order_by('yaradildi')

        serializer = MesajSerializer(mesajlar, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, other_user_id):
        other_user = get_object_or_404(User, pk=other_user_id)
        metn = request.data.get('metn', '').strip()
        elan_id = request.data.get('elan_id')

        if not metn:
            return Response({'error': 'Mesaj mətni boş ola bilməz.'}, status=status.HTTP_400_BAD_REQUEST)

        if other_user.id in Bloklama.bloklanmis_idler(request.user):
            return Response(
                {'error': 'Bu istifadəçi ilə mesajlaşma mümkün deyil (bloklanıb).'},
                status=status.HTTP_403_FORBIDDEN
            )

        elan = Elan.objects.filter(pk=elan_id).first() if elan_id else None

        mesaj = Mesaj.objects.create(
            gonderici=request.user,
            alici=other_user,
            elan=elan,
            metn=metn
        )

        serializer = MesajSerializer(mesaj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)


# -----------------------------------------------------------------------------
# REPORT & BLOCK (Google Play UGC tələbi)
# -----------------------------------------------------------------------------

class ReportApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        elan_id = request.data.get('elan_id')
        user_id = request.data.get('user_id')
        sebeb = request.data.get('sebeb', 'diger')
        qeyd = (request.data.get('qeyd') or '').strip()[:1000]

        if sebeb not in dict(Shikayet.SEBEB_CHOICES):
            sebeb = 'diger'

        elan = Elan.objects.filter(pk=elan_id).first() if elan_id else None
        hedef_user = User.objects.filter(pk=user_id).first() if user_id else None
        if elan and not hedef_user:
            hedef_user = elan.istifadeci

        if not elan and not hedef_user:
            return Response({'error': 'Şikayət obyekti tapılmadı.'}, status=status.HTTP_400_BAD_REQUEST)
        if hedef_user and hedef_user.id == request.user.id:
            return Response({'error': 'Özünüzdən şikayət edə bilməzsiniz.'}, status=status.HTTP_400_BAD_REQUEST)

        Shikayet.objects.create(
            sikayet_eden=request.user,
            elan=elan,
            istifadeci=hedef_user,
            sebeb=sebeb,
            qeyd=qeyd,
        )
        return Response(
            {'message': 'Şikayətiniz qəbul edildi. Moderatorlar 24 saat ərzində baxacaq.'},
            status=status.HTTP_201_CREATED
        )


class BlockToggleApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, user_id):
        hedef = get_object_or_404(User, pk=user_id)
        if hedef.id == request.user.id:
            return Response({'error': 'Özünüzü bloklaya bilməzsiniz.'}, status=status.HTTP_400_BAD_REQUEST)

        obj, created = Bloklama.objects.get_or_create(bloklayan=request.user, bloklanan=hedef)
        if not created:
            obj.delete()
            return Response({'blocked': False, 'message': 'İstifadəçi blokdan çıxarıldı.'})
        return Response({'blocked': True, 'message': 'İstifadəçi bloklandı. Onun elanları və mesajları sizə görünməyəcək.'})


class BlockedUsersApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        data = []
        for b in Bloklama.objects.filter(bloklayan=request.user).select_related('bloklanan__profil').order_by('-yaradildi'):
            u = b.bloklanan
            profil = getattr(u, 'profil', None)
            ad = f"{profil.ad} {profil.soyad}".strip() if profil else ''
            data.append({
                'user_id': u.id,
                'username': u.username,
                'ad_soyad': ad or u.get_full_name() or u.username,
            })
        return Response(data)


# -----------------------------------------------------------------------------
# VIP & PAYMENTS VIEWS
# -----------------------------------------------------------------------------

class VipPackagesApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        paketler = VipPaket.get_all_aktiv()
        serializer = VipPaketSerializer(paketler, many=True)
        return Response(serializer.data)


class ElanActivateVipApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
        profil, _ = Profil.objects.get_or_create(istifadeci=request.user)
        nov = request.data.get('nov', 'vip')

        if nov not in ('vip', 'super_vip'):
            return Response(
                {'error': 'Yanlış VİP növü seçilib.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        paket = VipPaket.get_paket(nov)
        qiymet = paket.qiymet
        gun = paket.muddet_gun
        now = timezone.now()
        # Əgər elan artıq aktiv VIP-dirsə, vaxtı bitmədən təkrar VIP edilə bilməz
        if elan.is_vip_aktiv() and elan.vip_bitis and elan.vip_bitis > now:
            if elan.vip_status == nov or elan.vip_status == 'super_vip':
                bitis_str = elan.vip_bitis.strftime("%d.%m.%Y")
                label = "Super VIP" if elan.vip_status == 'super_vip' else "VIP"
                return Response(
                    {'error': f'Bu elan artıq {label} statusundadır ({bitis_str}-dək aktivdir). Müddəti bitmədən yenidən {nov.upper()} edilə bilməz.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

        with transaction.atomic():
            updated = Profil.objects.filter(
                pk=profil.pk, balans__gte=qiymet
            ).update(balans=F('balans') - qiymet)
            if not updated:
                return Response(
                    {
                        'error': f'Balansınız kifayət deyil! Lazım olan: {qiymet} AZN (Cari balans: {profil.balans} AZN)',
                        'insufficient_balance': True,
                        'required': float(qiymet),
                        'current_balance': float(profil.balans),
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            if elan.is_vip_aktiv() and elan.vip_bitis and elan.vip_bitis > now:
                yeni_bitis = elan.vip_bitis + timedelta(days=gun)
            else:
                yeni_bitis = now + timedelta(days=gun)

            elan.vip_status = nov
            elan.vip_bitis = yeni_bitis
            elan.vip_yenilendi = now
            elan.vip_siralama = 1
            elan.save()

            Odenis.objects.create(
                istifadeci=request.user,
                elan=elan,
                nov=nov,
                mebleg=qiymet,
                status='tesdiq_edildi'
            )

        profil.refresh_from_db()
        return Response({
            'message': f'Elanınız "{paket.ad}" edildi! Bitiş tarixi: {yeni_bitis.strftime("%d.%m.%Y")}.',
            'vip_status': elan.vip_status,
            'vip_bitis': yeni_bitis,
            'balans': float(profil.balans),
        })


class ElanIreliCekApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk)
        if elan.istifadeci != request.user and not request.user.is_superuser:
            return Response({'error': 'Bu elanı idarə etmək icazəniz yoxdur.'}, status=status.HTTP_403_FORBIDDEN)
        if elan.status != 'aktiv':
            return Response({'error': 'Yalnız aktiv elanları irəli çəkmək mümkündür.'}, status=status.HTTP_400_BAD_REQUEST)

        IRELI_CEK_QIYMET = Decimal('1.00')
        profil, _ = Profil.objects.get_or_create(istifadeci=request.user)

        if profil.balans < IRELI_CEK_QIYMET:
            return Response({
                'error': f'Balansınız kifayət etmir. Cari balansınız: {profil.balans:.2f} AZN. Elanı irəli çəkmək üçün 1 AZN balans artırın.',
                'insufficient_balance': True,
                'required': 1.00,
                'current_balance': float(profil.balans),
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            updated = Profil.objects.filter(pk=profil.pk, balans__gte=IRELI_CEK_QIYMET).update(
                balans=F('balans') - IRELI_CEK_QIYMET
            )
            if not updated:
                return Response({'error': 'Balansınız kifayət etmir.'}, status=status.HTTP_400_BAD_REQUEST)

            now = timezone.now()
            Elan.objects.filter(pk=elan.pk).update(
                ireli_cekildi=now,
                ireli_cekilme_sayi=F('ireli_cekilme_sayi') + 1
            )
            Odenis.objects.create(
                istifadeci=request.user,
                elan=elan,
                nov='ireli_cek',
                mebleg=IRELI_CEK_QIYMET,
                status='tesdiq_edildi',
                qeyd=f'#{elan.nomre} nömrəli elan mobil app-dan irəli çəkildi (1 AZN)'
            )
            profil.refresh_from_db(fields=['balans'])

        return Response({
            'success': True,
            'message': f'“{elan.bashliq}” elanı uğurla ən ön sıraya çəkildi!',
            'balans': float(profil.balans),
            'elan_id': elan.pk
        })


class BankInfoApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        banklar = BankMelumat.objects.filter(aktiv=True)
        serializer = BankMelumatSerializer(banklar, many=True)
        return Response(serializer.data)


class PaymentCreateApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        nov = request.data.get('nov', 'balans')
        mebleg_raw = request.data.get('mebleg', '0')
        elan_id = request.data.get('elan_id')
        qebz = request.FILES.get('qebz')
        qeyd = request.data.get('qeyd', '').strip()

        try:
            mebleg = Decimal(mebleg_raw)
            if mebleg <= 0:
                return Response({'error': 'Məbləğ sıfırdan böyük olmalıdır.'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception:
            return Response({'error': 'Məbləğ formatı yanlışdır.'}, status=status.HTTP_400_BAD_REQUEST)

        if not qebz:
            return Response({'error': 'Zəhmət olmasa ödəniş qəbzinin şəklini yükləyin.'}, status=status.HTTP_400_BAD_REQUEST)

        elan = Elan.objects.filter(pk=elan_id, istifadeci=request.user).first() if elan_id else None

        odenis = Odenis.objects.create(
            istifadeci=request.user,
            elan=elan,
            nov=nov,
            mebleg=mebleg,
            qebz=qebz,
            qeyd=qeyd,
            status='gozlemede'
        )

        serializer = OdenisSerializer(odenis, context={'request': request})
        return Response({
            'odenis': serializer.data,
            'message': 'Ödəniş qəbziniz qəbul edildi və yoxlanışdadır. Qısa müddətdə təsdiqlənəcək.'
        }, status=status.HTTP_201_CREATED)


class MyPaymentsApiView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        odenisler = Odenis.objects.filter(istifadeci=request.user).order_by('-yaradildi')
        serializer = OdenisSerializer(odenisler, many=True, context={'request': request})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# BANNERS VIEW
# -----------------------------------------------------------------------------

class BannersApiView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        banners = ReklamBanner.objects.filter(aktiv=True)
        serializer = ReklamBannerSerializer(banners, many=True, context={'request': request})
        return Response(serializer.data)
