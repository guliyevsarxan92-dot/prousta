import re
from datetime import timedelta
from decimal import Decimal
from django.shortcuts import get_object_or_404
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.db import transaction
from django.db.models import Q, Max, Count, F, Case, When, IntegerField, Subquery
from django.utils import timezone
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework.authtoken.models import Token
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.pagination import PageNumberPagination

from .models import (
    Elan, ElanShekil, Kategori, Profil, Favorit, Mesaj,
    Odenis, BankMelumat, VipPaket, ReklamBanner, Shikayet, Bloklama
)
from .api_serializers import (
    UserSerializer, ProfilSerializer, KategoriSerializer,
    ElanListSerializer, ElanDetailSerializer, MesajSerializer,
    VipPaketSerializer, BankMelumatSerializer, OdenisSerializer,
    ReklamBannerSerializer
)
from .rotation import apply_fair_rotation
from .content import description_error as _aciqlama_qadaga_yoxla
from .search import search_listings
from .watermark import filigran_yoxla
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token as google_id_token
from django.conf import settings
import secrets
from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
from django.core.validators import validate_email
from .validation import image_upload, money, phone, text
from .listings import create_listing, update_listing, visible_listings, check_access, check_messaging
from .payments import buy_vip, bump_listing
from .authentication import issue_token
from .identity import google_user
from .throttles import AuthThrottle


class ValidatedAPIView(APIView):
    def initial(self, request, *args, **kwargs):
        super().initial(request, *args, **kwargs)
        if request.method not in ('GET', 'HEAD', 'OPTIONS'):
            data = request.data
            if not hasattr(data, 'items'):
                raise ValidationError('Sorğu JSON obyekt və ya forma olmalıdır.')
            text_fields = {'username', 'email', 'password', 'ad', 'soyad', 'telefon', 'sheher',
                           'bashliq', 'acaqlama', 'metn', 'qeyd', 'nov', 'id_token', 'sebeb', 'confirm'}
            for key, value in data.items():
                if key in text_fields and (not isinstance(value, str) or len(value) > 10000):
                    raise ValidationError(f'{key}: düzgün mətn daxil edin.')
                if key in {'elan_id', 'user_id', 'kategori', 'kategori_id'} and value not in (None, ''):
                    if not str(value).isascii() or not str(value).isdigit() or len(str(value)) > 18:
                        raise ValidationError(f'{key}: düzgün identifikator daxil edin.')
        if request.method == 'GET' and request.user.is_authenticated:
            request._user_favorite_ids = set(Favorit.objects.filter(istifadeci=request.user).values_list('elan_id', flat=True))



# -----------------------------------------------------------------------------
# AUTH VIEWS
# -----------------------------------------------------------------------------

class LoginApiView(ValidatedAPIView):
    authentication_classes = []
    throttle_classes = [AuthThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username_or_email = request.data.get('username', '').strip()
        password = request.data.get('password', '')

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

        token = issue_token(user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Uğurla daxil oldunuz.'
        })


class RegisterApiView(ValidatedAPIView):
    authentication_classes = []
    throttle_classes = [AuthThrottle]
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = text(request.data.get('username', '').lower(), 'İstifadəçi adı', 150, minimum=8)
        if not username.isalnum():
            raise ValidationError('İstifadəçi adı yalnız hərf və rəqəmdən ibarət olmalıdır.')
        email = request.data.get('email', '').strip().lower()
        password = request.data.get('password', '')
        ad = request.data.get('ad', '').strip()
        soyad = request.data.get('soyad', '').strip()
        telefon = request.data.get('telefon', '').strip()
        sheher = request.data.get('sheher', 'Bakı').strip()

        if not username or not password:
            return Response({'error': 'İstifadəçi adı və şifrə mütləqdir.'}, status=status.HTTP_400_BAD_REQUEST)

        candidate = User(username=username, email=email, first_name=ad, last_name=soyad)
        candidate.full_clean(exclude=['password'])
        validate_password(password, candidate)
        validate_email(email)
        if username.startswith(('prousta_', 'google_')):
            raise ValidationError('Bu istifadəçi adı rezerv edilib.')
        text(ad, 'Ad', 50, minimum=0)
        text(soyad, 'Soyad', 50, minimum=0)
        telefon = phone(telefon, optional=True)
        text(sheher, 'Şəhər', 100)

        if User.objects.filter(username__iexact=username).exists():
            return Response({'error': 'Bu istifadəçi adı artıq götürülüb.'}, status=status.HTTP_400_BAD_REQUEST)

        if email and User.objects.filter(email__iexact=email).exists():
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
            profil.telefon = phone(telefon, optional=True)
            profil.sheher = text(sheher, 'Şəhər', 100)
            profil.save()

            token = issue_token(user)

        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Qeydiyyat uğurla tamamlandı.'
        }, status=status.HTTP_201_CREATED)


class GoogleLoginApiView(ValidatedAPIView):
    authentication_classes = []
    throttle_classes = [AuthThrottle]
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
            return Response({'error': 'Google token etibarsızdır.'}, status=status.HTTP_401_UNAUTHORIZED)

        user = google_user(info)

        token = issue_token(user)
        user_serializer = UserSerializer(user, context={'request': request})
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Google ilə uğurla daxil oldunuz.'
        })


class LogoutApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        Token.objects.filter(user=request.user).delete()
        return Response({'message': 'Uğurla çıxış edildi.'})


class DeleteAccountApiView(ValidatedAPIView):
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
            user.delete()  # CASCADE: Token, Profil, Elan, Mesaj, Favorit, Bloklama

        return Response({'message': 'Hesabınız və bütün məlumatlarınız silindi.'})


class ProfileApiView(ValidatedAPIView):
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
            first_name = text(first_name, 'Ad', 50, minimum=0)
            user.first_name = first_name
            profil.ad = first_name
        if last_name is not None:
            last_name = text(last_name, 'Soyad', 50, minimum=0)
            user.last_name = last_name
            profil.soyad = last_name
        if telefon is not None:
            profil.telefon = phone(telefon, optional=True)
        if sheher is not None:
            profil.sheher = text(sheher, 'Şəhər', 100)
        if avatar is not None:
            profil.avatar = image_upload(avatar)

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

class CategoriesApiView(ValidatedAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        kateqoriyalar = Kategori.objects.filter(ust_kategori=None).prefetch_related('alt_kateqoriyalar')
        counts = dict(visible_listings(request.user).order_by().values('kategori_id').annotate(
            total=Count('pk')).values_list('kategori_id', 'total'))
        parents = dict(Kategori.objects.values_list('pk', 'ust_kategori_id'))
        totals = counts.copy()
        for category_id, count in counts.items():
            parent = parents.get(category_id)
            if parent:
                totals[parent] = totals.get(parent, 0) + count
        serializer = KategoriSerializer(kateqoriyalar, many=True, context={'request': request, 'category_counts': totals})
        return Response(serializer.data)


# -----------------------------------------------------------------------------
# ELANLAR (ADS) VIEWS
# -----------------------------------------------------------------------------

def serialize_page(queryset, request, serializer_class):
    if 'page' not in request.GET and 'page_size' not in request.GET:
        # Preserve deployed v1 clients' array contract, with a hard resource cap.
        response = Response(serializer_class(queryset[:1000], many=True, context={'request': request}).data)
        response['X-Result-Limit'] = '1000'
        response['Link'] = f'<{request.path}?page=1&page_size=50>; rel="first"'
        return response
    paginator = StandardResultsSetPagination()
    page = paginator.paginate_queryset(queryset, request)
    return paginator.get_paginated_response(serializer_class(page, many=True, context={'request': request}).data)


class StandardResultsSetPagination(PageNumberPagination):
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 50


class ElanlarListApiView(ValidatedAPIView):
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

        if kategori_slug:
            qs = qs.filter(
                Q(kategori__slug=kategori_slug) |
                Q(kategori__ust_kategori__slug=kategori_slug)
            )

        qs = search_listings(qs, q, seher)

        if vip_only:
            qs = qs.filter(vip_status__in=['vip', 'super_vip'], vip_bitis__gt=timezone.now())

        qs = apply_fair_rotation(qs, seed)

        if request.user.is_authenticated:
            request._user_favorite_ids = set(
                Favorit.objects.filter(istifadeci=request.user).values_list('elan_id', flat=True)
            )

        paginator = StandardResultsSetPagination()
        page_results = paginator.paginate_queryset(qs, request)
        serializer = ElanListSerializer(page_results, many=True, context={'request': request})
        return paginator.get_paginated_response(serializer.data)


class ElanDetailApiView(ValidatedAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request, pk):
        elan = get_object_or_404(
            Elan.objects.select_related('kategori', 'istifadeci__profil').prefetch_related('shekillar'),
            pk=pk
        )

        check_access(elan, request.user)
        # Baxış sayını artırırıq
        Elan.objects.filter(pk=pk).update(baxish_sayi=F('baxish_sayi') + 1)
        elan.baxish_sayi += 1

        serializer = ElanDetailSerializer(elan, context={'request': request})
        return Response(serializer.data)


class ElanCreateApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        elan = create_listing(request.user, request.data,
                              request.FILES.getlist('shekillar') or request.FILES.getlist('images'))

        serializer = ElanDetailSerializer(elan, context={'request': request})
        return Response({
            'elan': serializer.data,
            'message': 'Elanınız uğurla dərc edildi.'
        }, status=status.HTTP_201_CREATED)


class ElanUpdateApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def patch(self, request, pk):
        get_object_or_404(Elan, pk=pk, istifadeci=request.user)
        raw_ids = request.data.get('silinecek_shekiller', [])
        if hasattr(request.data, 'getlist'):
            raw_ids = request.data.getlist('silinecek_shekiller')
            if len(raw_ids) == 1 and raw_ids[0].startswith('['):
                raw_ids = raw_ids[0]
        elan = update_listing(request.user, pk, request.data, request.FILES.getlist('shekillar'), raw_ids)
        serializer = ElanDetailSerializer(elan, context={'request': request})
        return Response({'elan': serializer.data, 'message': 'Elan yeniləndi.'})


class ElanDeleteApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk, istifadeci=request.user)
        elan.delete()
        return Response({'message': 'Elan silindi.'})


class ElanClickApiView(ValidatedAPIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request, pk, nov):
        elan = get_object_or_404(Elan, pk=pk)
        check_access(elan, request.user)
        if nov == 'zeng':
            Elan.objects.filter(pk=pk).update(zeng_sayi=F('zeng_sayi') + 1)
        elif nov == 'wp':
            Elan.objects.filter(pk=pk).update(wp_sayi=F('wp_sayi') + 1)
        return Response({'success': True})


class MyElanlarApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        status_filter = request.GET.get('status')
        qs = Elan.objects.filter(istifadeci=request.user).select_related('kategori').prefetch_related('shekillar')
        if status_filter:
            qs = qs.filter(status=status_filter)
        return serialize_page(qs.order_by('-pk'), request, ElanListSerializer)


# -----------------------------------------------------------------------------
# FAVORITES VIEWS
# -----------------------------------------------------------------------------

class FavoritesListApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        fav_elan_ids = Favorit.objects.filter(istifadeci=request.user).values_list('elan_id', flat=True)
        elanlar = visible_listings(request.user).filter(id__in=fav_elan_ids).select_related('kategori').prefetch_related('shekillar')
        return serialize_page(elanlar.order_by('-pk'), request, ElanListSerializer)


class FavoriteToggleApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        elan = get_object_or_404(Elan, pk=pk)
        check_access(elan, request.user)
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

class ConversationsApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        blocked = Bloklama.bloklanmis_idler(user)
        base = Mesaj.objects.filter(Q(gonderici=user) | Q(alici=user)).exclude(
            Q(gonderici_id__in=blocked) | Q(alici_id__in=blocked))
        latest = base.order_by().annotate(other=Case(
            When(gonderici=user, then=F('alici_id')), default=F('gonderici_id'),
            output_field=IntegerField())).values('other').annotate(last=Max('id')).values('last')
        mesajlar = Mesaj.objects.filter(pk__in=Subquery(latest)).select_related(
            'gonderici__profil', 'alici__profil').order_by('-pk')
        before = request.GET.get('before_id')
        if before:
            try:
                mesajlar = mesajlar.filter(pk__lt=int(before))
            except ValueError:
                raise ValidationError('Yanlış cursor.')
        unread = dict(Mesaj.objects.filter(alici=user, oxundu=False).order_by().values(
            'gonderici_id').annotate(total=Count('pk')).values_list('gonderici_id', 'total'))
        other_user_ids = set()
        conversations = []
        bloklanmis = blocked
        mesajlar = mesajlar[:100]

        for m in mesajlar:
            other_user = m.alici if m.gonderici == user else m.gonderici
            if other_user.id in bloklanmis:
                continue
            if other_user.id not in other_user_ids:
                other_user_ids.add(other_user.id)
                unread_count = unread.get(other_user.pk, 0)
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
                    'last_message_id': m.pk,
                    'last_message_time': m.yaradildi,
                    'unread_count': unread_count,
                    'elan_id': m.elan_id,
                })

        return Response(conversations)


class ChatMessagesApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, other_user_id):
        other_user = get_object_or_404(User, pk=other_user_id, is_active=True)
        check_messaging(request.user, other_user.pk)
        # Mesajları oxunmuş kimi qeyd edirik
        Mesaj.objects.filter(gonderici=other_user, alici=request.user, oxundu=False).update(oxundu=True)

        mesajlar = Mesaj.objects.filter(
            (Q(gonderici=request.user) & Q(alici=other_user)) |
            (Q(gonderici=other_user) & Q(alici=request.user))
        ).select_related('gonderici__profil').order_by('-pk')
        after = request.GET.get('after_id')
        before = request.GET.get('before_id')
        if after and before:
            raise ValidationError('Yalnız bir cursor göndərin.')
        try:
            if after:
                mesajlar = mesajlar.filter(pk__gt=int(after)).order_by('pk')
            elif before:
                mesajlar = mesajlar.filter(pk__lt=int(before))
        except ValueError:
            raise ValidationError('Yanlış cursor.')
        results = list(mesajlar[:100])
        if not after:
            results.reverse()
        mesajlar = results

        serializer = MesajSerializer(mesajlar, many=True, context={'request': request})
        return Response(serializer.data)

    def post(self, request, other_user_id):
        other_user = get_object_or_404(User, pk=other_user_id, is_active=True)
        check_messaging(request.user, other_user.pk)
        metn = text(request.data.get('metn', ''), 'Mesaj', 5000)
        elan_id = request.data.get('elan_id')

        if not metn:
            return Response({'error': 'Mesaj mətni boş ola bilməz.'}, status=status.HTTP_400_BAD_REQUEST)

        if other_user.id in Bloklama.bloklanmis_idler(request.user):
            return Response(
                {'error': 'Bu istifadəçi ilə mesajlaşma mümkün deyil (bloklanıb).'},
                status=status.HTTP_403_FORBIDDEN
            )

        elan = get_object_or_404(visible_listings(request.user), pk=elan_id) if elan_id else None
        if elan and elan.istifadeci_id not in (request.user.pk, other_user.pk):
            raise ValidationError('Elan söhbət iştirakçılarına aid deyil.')

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

class ReportApiView(ValidatedAPIView):
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


class BlockToggleApiView(ValidatedAPIView):
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


class BlockedUsersApiView(ValidatedAPIView):
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

class VipPackagesApiView(ValidatedAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        paketler = VipPaket.get_all_aktiv()
        serializer = VipPaketSerializer(paketler, many=True)
        return Response(serializer.data)


class ElanActivateVipApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Elan, pk=pk, istifadeci=request.user)
        elan, profil, paket = buy_vip(request.user, pk, request.data.get('nov', 'vip'))
        return Response({'message': f'Elanınız {paket.ad} edildi.', 'vip_status': elan.vip_status,
                         'vip_bitis': elan.vip_bitis, 'balans': float(profil.balans)})


class ElanIreliCekApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        get_object_or_404(Elan, pk=pk)
        elan, profil = bump_listing(request.user, pk)
        return Response({'success': True, 'message': 'Elan irəli çəkildi.',
                         'balans': float(profil.balans), 'elan_id': elan.pk})


class BankInfoApiView(ValidatedAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        banklar = BankMelumat.objects.filter(aktiv=True)
        serializer = BankMelumatSerializer(banklar, many=True)
        return Response(serializer.data)


class PaymentCreateApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def post(self, request):
        nov = request.data.get('nov', 'balans')
        mebleg_raw = request.data.get('mebleg', '0')
        elan_id = request.data.get('elan_id')
        qebz = request.FILES.get('qebz')
        qeyd = request.data.get('qeyd', '').strip()

        if nov not in ('balans', 'vip', 'super_vip', 'ireli_cek'):
            raise ValidationError('Yanlış ödəniş növü.')
        mebleg = money(mebleg_raw, minimum=Decimal('0.01'), maximum=Decimal('500'))
        qebz = image_upload(qebz)
        elan = None
        if nov != 'balans':
            elan = get_object_or_404(visible_listings(request.user), pk=elan_id, istifadeci=request.user)
            expected = Decimal('1.00') if nov == 'ireli_cek' else VipPaket.get_paket(nov).qiymet
            if mebleg != expected:
                raise ValidationError('Məbləğ seçilmiş xidmətin tarifinə uyğun deyil.')
        elif elan_id:
            raise ValidationError('Balans ödənişinə elan əlavə edilməməlidir.')

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


class MyPaymentsApiView(ValidatedAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        odenisler = Odenis.objects.filter(istifadeci=request.user).order_by('-yaradildi')
        return serialize_page(odenisler.select_related('elan'), request, OdenisSerializer)


# -----------------------------------------------------------------------------
# BANNERS VIEW
# -----------------------------------------------------------------------------

class BannersApiView(ValidatedAPIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        banners = ReklamBanner.objects.filter(aktiv=True).filter(Q(bitis_tarixi__isnull=True) | Q(bitis_tarixi__gt=timezone.now()))
        serializer = ReklamBannerSerializer(banners, many=True, context={'request': request})
        return Response(serializer.data)
