from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv
from django.core.exceptions import ImproperlyConfigured

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
DEBUG = os.getenv('DEBUG', 'False').lower() == 'true'
SECRET_KEY = os.getenv('SECRET_KEY', '').strip()
if not SECRET_KEY or len(SECRET_KEY) < 50:
    raise ImproperlyConfigured('SECRET_KEY must contain at least 50 characters.')

ALLOWED_HOSTS = [host.strip() for host in os.getenv(
    'ALLOWED_HOSTS', 'prousta.az,www.prousta.az,localhost,127.0.0.1'
).split(',') if host.strip()]

CSRF_TRUSTED_ORIGINS = [
    'https://prousta.az',
    'https://www.prousta.az',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

INSTALLED_APPS = [
    'unfold',
    'unfold.contrib.filters',
    'unfold.contrib.forms',
    'unfold.contrib.inlines',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'rest_framework',
    'rest_framework.authtoken',
    'social_django',
    'cloudinary',
    'cloudinary_storage',
    'core',
]

MIDDLEWARE = [
    'core.middleware.TrustedProxyMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'core.seo.CanonicalHostMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'prousta.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'social_django.context_processors.backends',
                'social_django.context_processors.login_redirect',
                'core.context_processors.oxunmamis_mesaj',
                'core.seo.seo_context',
            ],
            'builtins': [
                'core.templatetags.cld_tags',
            ],
        },
    },
]

WSGI_APPLICATION = 'prousta.wsgi.application'

_active_db_url = os.getenv('DATABASE_URL', '').strip()
if not _active_db_url:
    raise ImproperlyConfigured('DATABASE_URL must be explicitly configured.')

if 'pooler.supabase.com:5432' in _active_db_url:
    _active_db_url = _active_db_url.replace(':5432', ':6543')

DATABASES = {
    'default': {
        **dj_database_url.parse(
            _active_db_url,
            conn_max_age=0,
            ssl_require=True if 'supabase' in _active_db_url else (not DEBUG),
        ),
        'DISABLE_SERVER_SIDE_CURSORS': True,
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'core.validation.PasswordLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'az'
TIME_ZONE = 'Asia/Baku'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'
PRIVATE_MEDIA_ROOT = Path(os.getenv('PRIVATE_MEDIA_ROOT', str(BASE_DIR / 'private_media')))
MEDIA_CLEANUP_EAGER = DEBUG

# Upload limitləri (mobil app profil şəkli + qəbz üçün)
DATA_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024      # 15 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 2 * 1024 * 1024      # 2 MB; larger uploads use temporary files

# Django 5.x STORAGES — köhnə DEFAULT_FILE_STORAGE / STATICFILES_STORAGE əvəzinə
_CLOUDINARY_URL = os.getenv('CLOUDINARY_URL', '').strip()

if _CLOUDINARY_URL:
    import cloudinary
    cloudinary.config(secure=True)
    _default_storage = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    _default_storage = 'django.core.files.storage.FileSystemStorage'

STORAGES = {
    'receipts': {'BACKEND': 'django.core.files.storage.FileSystemStorage',
                 'OPTIONS': {'location': str(PRIVATE_MEDIA_ROOT), 'base_url': '/private-unserved/'}},
    'default': {
        'BACKEND': _default_storage,
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'core.authentication.ExpiringTokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
    'EXCEPTION_HANDLER': 'core.validation.api_exception_handler',
    'DEFAULT_THROTTLE_CLASSES': ['rest_framework.throttling.AnonRateThrottle', 'rest_framework.throttling.UserRateThrottle', 'core.throttles.WriteThrottle'],
    'DEFAULT_THROTTLE_RATES': {'anon': '120/min', 'user': '600/min', 'write': '30/min', 'auth': '5/min'},
    'NUM_PROXIES': 0,
}

# Production təhlükəsizlik
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = os.getenv('SECURE_HSTS_INCLUDE_SUBDOMAINS', 'False').lower() == 'true'
    SECURE_HSTS_PRELOAD = os.getenv('SECURE_HSTS_PRELOAD', 'False').lower() == 'true'
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_REFERRER_POLICY = 'strict-origin-when-cross-origin'

LOGIN_URL = '/giris/'
TRUSTED_PROXY_CIDRS = [cidr.strip() for cidr in os.getenv(
    'TRUSTED_PROXY_CIDRS', '127.0.0.1/32,::1/128'
).split(',') if cidr.strip()]
SECURE_REDIRECT_EXEMPT = [r'^health/$']

# Axtarış sistemləri təsdiq kodları (Google Search Console / Yandex Webmaster)
GOOGLE_SITE_VERIFICATION = os.getenv('GOOGLE_SITE_VERIFICATION', '')
YANDEX_VERIFICATION = os.getenv('YANDEX_VERIFICATION', '')
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# ============================================================
# Social Auth (Google OAuth2)
# ============================================================
AUTHENTICATION_BACKENDS = (
    'social_core.backends.google.GoogleOAuth2',
    'django.contrib.auth.backends.ModelBackend',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_KEY = os.getenv('GOOGLE_OAUTH2_KEY', '')
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET = os.getenv('GOOGLE_OAUTH2_SECRET', '')

# Mobil tətbiqin Credential Manager-dən göndərdiyi ID token-in audience-i
# (Google Cloud Console → Web application OAuth client ID)
GOOGLE_WEB_CLIENT_ID = os.environ.get(
    'GOOGLE_WEB_CLIENT_ID',
    '811460264298-gge8uv2mfv7rro7fsi6jhkgfs7i1krht.apps.googleusercontent.com',
)

SOCIAL_AUTH_GOOGLE_OAUTH2_SCOPE = [
    'https://www.googleapis.com/auth/userinfo.email',
    'https://www.googleapis.com/auth/userinfo.profile',
]

SOCIAL_AUTH_LOGIN_REDIRECT_URL = '/'
SOCIAL_AUTH_LOGIN_ERROR_URL = '/giris/'
SOCIAL_AUTH_RAISE_EXCEPTIONS = False
SOCIAL_AUTH_JSONFIELD_ENABLED = True

SOCIAL_AUTH_PIPELINE = (
    'social_core.pipeline.social_auth.social_details',
    'social_core.pipeline.social_auth.social_uid',
    'social_core.pipeline.social_auth.auth_allowed',
    'social_core.pipeline.social_auth.social_user',
    'social_core.pipeline.user.get_username',
    'core.identity.require_explicit_google_link',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    # 'social_core.pipeline.user.user_details' qəsdən silinib —
    # əks halda Google hər daxilolmada istifadəçinin dəyişdiyi ad/soyadı
    # Google hesabındakı dəyərlərə geri qaytarırdı.
    'core.pipeline.create_profil',
)

# ============================================================
# Unfold Admin Configuration
# ============================================================
from django.urls import reverse_lazy

UNFOLD = {
    "SITE_TITLE": "Prousta İdarəetmə Paneli",
    "SITE_HEADER": "Prousta Admin",
    "SITE_SUBHEADER": "Elan və Usta Xidmətləri Platforması",
    "SITE_URL": "/",
    "SITE_ICON": {
        "light": lambda request: "/static/brand-logo.svg",
        "dark": lambda request: "/static/brand-logo-dark.svg",
    },
    "SITE_LOGO": {
        "light": lambda request: "/static/brand-logo.svg",
        "dark": lambda request: "/static/brand-logo-dark.svg",
    },
    "SITE_FAVICONS": [
        {
            "rel": "icon",
            "type": "image/svg+xml",
            "href": lambda request: "/static/favicon.svg",
        },
    ],
    "DASHBOARD_CALLBACK": "core.admin.dashboard_callback",
    "COLORS": {
        "primary": {
            "50": "240 253 244",
            "100": "220 252 231",
            "200": "187 247 208",
            "300": "134 239 172",
            "400": "74 222 128",
            "500": "34 197 94",
            "600": "22 163 74",
            "700": "21 128 61",
            "800": "22 101 52",
            "900": "20 83 45",
            "950": "5 46 22",
        },
    },
    "COMMAND": {
        "search_models": True,
        "show_history": True,
    },
    "SCRIPTS": [
        lambda request: "/static/js/admin_notifications.js",
    ],
    "SIDEBAR": {
        "show_search": True,
        "show_all_applications": False,
        "navigation": [
            {
                "title": "İdarəetmə Mərkəzi",
                "separator": True,
                "items": [
                    {
                        "title": "Dashboard / Statistika",
                        "icon": "dashboard",
                        "link": reverse_lazy("admin:index"),
                    },
                ],
            },
            {
                "title": "Elanlar və Xidmətlər",
                "separator": True,
                "items": [
                    {
                        "title": "Yeni Elanlar (Gözləmədə)",
                        "icon": "mark_email_unread",
                        "link": "/admin/core/elan/?status__exact=gozlemede",
                        "badge": "core.admin.badge_elan_gozlemede",
                    },
                    {
                        "title": "Bütün Elanlar",
                        "icon": "campaign",
                        "link": reverse_lazy("admin:core_elan_changelist"),
                    },
                    {
                        "title": "Kateqoriyalar",
                        "icon": "category",
                        "link": reverse_lazy("admin:core_kategori_changelist"),
                    },
                    {
                        "title": "Problemlər (Bloq / FAQ)",
                        "icon": "help_center",
                        "link": reverse_lazy("admin:core_problem_changelist"),
                    },
                    {
                        "title": "Ustalar Bazası (Toplu Mesaj)",
                        "icon": "contacts",
                        "link": reverse_lazy("admin:core_elan_cixaris"),
                    },
                ],
            },
            {
                "title": "Maliyyə və VIP Tarifləri",
                "separator": True,
                "items": [
                    {
                        "title": "VIP Tarifləri və Qiymətlər",
                        "icon": "workspace_premium",
                        "link": reverse_lazy("admin:core_vippaket_changelist"),
                    },
                    {
                        "title": "Ödənişlər",
                        "icon": "payments",
                        "link": reverse_lazy("admin:core_odenis_changelist"),
                        "badge": "core.admin.badge_odenis_gozlemede",
                    },
                    {
                        "title": "Bank Məlumatları",
                        "icon": "account_balance",
                        "link": reverse_lazy("admin:core_bankmelumat_changelist"),
                    },
                ],
            },
            {
                "title": "Marketinq və Reklam",
                "separator": True,
                "items": [
                    {
                        "title": "Reklam Bannerləri",
                        "icon": "ad_units",
                        "link": reverse_lazy("admin:core_reklambanner_changelist"),
                    },
                    {
                        "title": "Banner Klik Hesabatları",
                        "icon": "query_stats",
                        "link": reverse_lazy("admin:core_bannerklik_changelist"),
                    },
                ],
            },
            {
                "title": "İstifadəçilər və Əlaqə",
                "separator": True,
                "items": [
                    {
                        "title": "İstifadəçilər",
                        "icon": "group",
                        "link": reverse_lazy("admin:auth_user_changelist"),
                    },
                    {
                        "title": "Profillər",
                        "icon": "badge",
                        "link": reverse_lazy("admin:core_profil_changelist"),
                    },
                    {
                        "title": "Mesajlar",
                        "icon": "chat",
                        "link": reverse_lazy("admin:core_mesaj_changelist"),
                    },
                    {
                        "title": "Favoritlər",
                        "icon": "favorite",
                        "link": reverse_lazy("admin:core_favorit_changelist"),
                    },
                ],
            },
            {
                "title": "Sistem və Təhlükəsizlik",
                "separator": True,
                "items": [
                    {
                        "title": "Qruplar və Hüquqlar",
                        "icon": "shield_person",
                        "link": reverse_lazy("admin:auth_group_changelist"),
                    },
                ],
            },
        ],
    },
}


# Shared across workers in production; created by core migration 0028.
CACHES = {'default': {
    'BACKEND': 'django.core.cache.backends.locmem.LocMemCache' if DEBUG else 'django.core.cache.backends.db.DatabaseCache',
    'LOCATION': 'prousta_cache',
}}
API_TOKEN_MAX_AGE = int(os.getenv('API_TOKEN_MAX_AGE', '2592000'))
EMAIL_HOST = os.getenv('EMAIL_HOST', 'localhost')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '25'))
EMAIL_HOST_USER = os.getenv('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'False').lower() == 'true'
EMAIL_USE_SSL = os.getenv('EMAIL_USE_SSL', 'False').lower() == 'true'
EMAIL_TIMEOUT = 10
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@prousta.az')
LOGGING = {
    'version': 1, 'disable_existing_loggers': False,
    'handlers': {'console': {'class': 'logging.StreamHandler'}},
    'loggers': {'core': {'handlers': ['console'], 'level': 'INFO', 'propagate': False}},
}
