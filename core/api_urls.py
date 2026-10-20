from django.urls import path
from . import api_views

urlpatterns = [
    # Auth
    path('auth/login/', api_views.LoginApiView.as_view(), name='api_login'),
    path('auth/register/', api_views.RegisterApiView.as_view(), name='api_register'),
    path('auth/google/', api_views.GoogleLoginApiView.as_view(), name='api_google_login'),
    path('auth/logout/', api_views.LogoutApiView.as_view(), name='api_logout'),
    path('auth/delete-account/', api_views.DeleteAccountApiView.as_view(), name='api_delete_account'),
    path('auth/me/', api_views.ProfileApiView.as_view(), name='api_me'),

    # Categories
    path('categories/', api_views.CategoriesApiView.as_view(), name='api_categories'),

    # Elanlar
    path('elanlar/', api_views.ElanlarListApiView.as_view(), name='api_elanlar_list'),
    path('elanlar/create/', api_views.ElanCreateApiView.as_view(), name='api_elan_create'),
    path('elanlar/<int:pk>/', api_views.ElanDetailApiView.as_view(), name='api_elan_detail'),
    path('elanlar/<int:pk>/update/', api_views.ElanUpdateApiView.as_view(), name='api_elan_update'),
    path('elanlar/<int:pk>/delete/', api_views.ElanDeleteApiView.as_view(), name='api_elan_delete'),
    path('elanlar/<int:pk>/vip/', api_views.ElanActivateVipApiView.as_view(), name='api_elan_activate_vip'),
    path('elanlar/<int:pk>/ireli-cek/', api_views.ElanIreliCekApiView.as_view(), name='api_elan_ireli_cek'),
    path('elanlar/<int:pk>/click/<str:nov>/', api_views.ElanClickApiView.as_view(), name='api_elan_click'),
    path('my-elanlar/', api_views.MyElanlarApiView.as_view(), name='api_my_elanlar'),

    # Favorites
    path('favorites/', api_views.FavoritesListApiView.as_view(), name='api_favorites_list'),
    path('favorites/toggle/<int:pk>/', api_views.FavoriteToggleApiView.as_view(), name='api_favorite_toggle'),

    # Messages / Chat
    path('messages/conversations/', api_views.ConversationsApiView.as_view(), name='api_conversations'),
    path('messages/<int:other_user_id>/', api_views.ChatMessagesApiView.as_view(), name='api_chat_messages'),

    # Report & Block (Google Play UGC)
    path('report/', api_views.ReportApiView.as_view(), name='api_report'),
    path('users/<int:user_id>/block/', api_views.BlockToggleApiView.as_view(), name='api_block_toggle'),
    path('users/blocked/', api_views.BlockedUsersApiView.as_view(), name='api_blocked_users'),

    # VIP & Payments
    path('vip-packages/', api_views.VipPackagesApiView.as_view(), name='api_vip_packages'),
    path('bank-info/', api_views.BankInfoApiView.as_view(), name='api_bank_info'),
    path('payments/create/', api_views.PaymentCreateApiView.as_view(), name='api_payment_create'),
    path('payments/my/', api_views.MyPaymentsApiView.as_view(), name='api_my_payments'),

    # Banners
    path('banners/', api_views.BannersApiView.as_view(), name='api_banners'),
]
