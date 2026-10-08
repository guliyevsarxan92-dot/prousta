from pathlib import Path
import os
import dj_database_url
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = os.getenv('SECRET_KEY', 'fallback-key-only-for-dev')
DEBUG = os.getenv('DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = [
    'https://prousta.az',
    'https://www.prousta.az',
    'https://*.onrender.com',
    'http://localhost:8000',
    'http://127.0.0.1:8000',
]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sitemaps',
    'rest_framework',
    'social_django',
    'cloudinary',
    'cloudinary_storage',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'prousta.wsgi.application'

_SUPABASE_DB_URL = "postgresql://postgres.nxisjlyoxzuhirhrewkj:Quliyev1992!@aws-1-eu-central-1.pooler.supabase.com:6543/postgres"

_raw_db_url = os.getenv('DATABASE_URL', '').strip()
if not _raw_db_url or 'frankfurt-postgres.render.com' in _raw_db_url or 'dpg-' in _raw_db_url or 'prousta-db' in _raw_db_url:
    _active_db_url = _SUPABASE_DB_URL
else:
    _active_db_url = _raw_db_url

DATABASES = {
    'default': dj_database_url.parse(
        _active_db_url,
        conn_max_age=600,
        ssl_require=True if 'supabase' in _active_db_url else (not DEBUG),
    )
}

AUTH_PASSWORD_VALIDATORS = [
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

# Upload limitləri (mobil app profil şəkli + qəbz üçün)
DATA_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024      # 15 MB
FILE_UPLOAD_MAX_MEMORY_SIZE = 15 * 1024 * 1024      # 15 MB

# Django 5.x STORAGES — köhnə DEFAULT_FILE_STORAGE / STATICFILES_STORAGE əvəzinə
_CLOUDINARY_URL = os.getenv('CLOUDINARY_URL', '').strip()

if _CLOUDINARY_URL:
    import cloudinary
    cloudinary.config(secure=True)
    _default_storage = 'cloudinary_storage.storage.MediaCloudinaryStorage'
else:
    _default_storage = 'django.core.files.storage.FileSystemStorage'

STORAGES = {
    'default': {
        'BACKEND': _default_storage,
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Production təhlükəsizlik
if not DEBUG:
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = True

LOGIN_URL = '/giris/'
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
    'social_core.pipeline.social_auth.associate_by_email',
    'social_core.pipeline.user.create_user',
    'social_core.pipeline.social_auth.associate_user',
    'social_core.pipeline.social_auth.load_extra_data',
    # 'social_core.pipeline.user.user_details' qəsdən silinib —
    # əks halda Google hər daxilolmada istifadəçinin dəyişdiyi ad/soyadı
    # Google hesabındakı dəyərlərə geri qaytarırdı.
    'core.pipeline.create_profil',
)
