# Prousta

Usta və xidmət elanları platforması: Django veb tətbiqi və REST API, PostgreSQL/Supabase, Flutter mobil/web müştərisi.

## Quruluş

- `core/listings.py`: veb/API üçün ortaq elan, limit, kateqoriya və şəkil qaydaları.
- `core/payments.py`: kilidlənən balans, VIP və irəli çəkmə əməliyyatları.
- `core/identity.py`, `authentication.py`: Google subject əlaqəsi və müddətli API token-ləri.
- `core/validation.py`: qiymət, telefon, mətn və etibarlı şəkil validasiyası.
- `core/media_cleanup.py`: commit-dən sonra, təkrar icra edilə bilən media təmizləmə növbəsi.
- `templates/`, `static/`: serverdə yaradılan veb interfeys; `mobile_app/`: Flutter 3.41.7 / Dart 3.11.5.
- `prousta/index.html`, `style.css`, boş `app.js` və `dentcrm/`: köhnə prototip qalıqları; Django onları təqdim etmir. İstifadəsi tam təsdiqlənmədən silinməyib.

## Lokal qurulum

Python 3.12 və ayrıca virtual mühit istifadə edin. Asılılıqlar `requirements.txt`-dədir.
Yeni qurulum üçün `.env.example` əsasında `.env` yaradın; mövcud `.env`-i əvəz etməyin.

- `SECRET_KEY`: təsadüfi, minimum 50 simvol. Generasiya: `python -c "import secrets; print(secrets.token_urlsafe(64))"`.
- Lokal inkişaf: `DEBUG=True`, `DATABASE_URL=sqlite:///db.sqlite3`, `PRIVATE_MEDIA_ROOT=./private_media`.
- İstehsalat: `DEBUG=False`, konkret `ALLOWED_HOSTS`, ayrıca PostgreSQL URL-i, HTTPS və davamlı private storage.
- Baza URL-i və secret məcburidir. Canlı bazaya avtomatik fallback yoxdur.
- Google veb OAuth: `GOOGLE_OAUTH2_KEY`, `GOOGLE_OAUTH2_SECRET`, `GOOGLE_WEB_CLIENT_ID`.
- Şifrə bərpası üçün SMTP dəyişənlərini doldurun. Şifrə email ilə göndərilmir; birdəfəlik keçid göndərilir.

Yalnız ayrıca lokal bazanı konfiqurasiya etdikdən sonra `python manage.py migrate` və `python manage.py runserver` işlədin.

## Təhlükəsiz testlər

Test parametrləri workspace `.env` bazasını/storage-ını istifadə etmir:

```bash
python manage.py check --settings=prousta.test_settings
python manage.py makemigrations --check --dry-run --settings=prousta.test_settings
python manage.py test core --settings=prousta.test_settings --noinput
```

SQLite row lock təminatlarını yoxlamır; üç concurrency testi orada atlanır. Tam PostgreSQL testləri üçün `TEST_DATABASE_URL` yalnız `/tmp/prousta-isolated-pg-.../socket` ünvanlı ayrıca test cluster-ini qəbul edir. Real Supabase URL-ini test konfiqurasiyasına verməyin.

Mobil yoxlamalar:

```bash
cd mobile_app
flutter pub get --enforce-lockfile
flutter analyze --fatal-infos
flutter test
flutter build web --no-pub
```

Mobil tətbiq `--dart-define=API_URL=https://staging.example/api/v1` parametrinə həm debug, həm release-də hörmət edir. Release yalnız HTTPS qəbul edir. Debug avtomatik canlı API-yə keçmir. Android emulatoru üçün ayrıca lokal server ünvanını göstərin.

## Autentifikasiya və API müqaviləsi

- Google şəxsiyyəti email ilə avtomatik birləşdirilmir; provider `sub` əsas götürülür. Mövcud parollu hesabı əlaqələndirmək üçün əvvəl vebdə həmin hesaba daxil olun, sonra Google girişini başladın.
- Köhnə mobil Google hesabı yalnız parolsuz, aktiv, qeyri-staff və başqa social əlaqəsi olmayan yeganə email hesabıdırsa təhlükəsiz qəbul edilir; əvvəlki token/sessiyalar ləğv olunur.
- API token-ləri default 30 gün qüvvədədir. Parol dəyişikliyi və logout token-i ləğv edir.
- Mobil token əvvəlki plaintext SharedPreferences-dən secure storage-a köçürülür; köhnə nüsxə yalnız uğurlu köçürmədən sonra silinir.
- `my-elanlar/`, `favorites/`, `payments/my/` `page`/`page_size` göndərildikdə `count/next/previous/results` pagination qaytarır; legacy v1 çağırışları maksimum 1000 elementlik array alır; `page_size` maksimum 50-dir. Köhnə mobil buraxılışlar bu müqaviləyə uyğunlaşdırılmalıdır.
- Chat: son 100 mesaj; `before_id` əvvəlki, `after_id` yeni mesajlar üçündür. Mobil müştəri incremental polling edir.
- Conversations maksimum 100 söhbət qaytarır; daha köhnə söhbətlər üçün `before_id` istifadə olunur.
- Telefon təqdimatı E.164 (`+994...`) formatındadır. Şəkillər maksimum 5 MB / 20 MP, elan üzrə maksimum 5 ədəddir; JPEG-ə yenidən kodlaşdırılır. Yeni qəbzlər yalnız etibarlı şəkildir; PDF qəbul edilmir.

## Buraxılış və əməliyyatlar

Ətraflı ardıcıllıq: [docs/RELEASE.md](docs/RELEASE.md). Audit üzrə vəziyyət: [docs/REMEDIATION.md](docs/REMEDIATION.md).

SEO, lokal axtarış və GEO qaydaları, testlər və buraxılışdan sonrakı ölçmə planı: [docs/SEO_GEO.md](docs/SEO_GEO.md).

- Docker image runtime-da miqrasiya və ya admin seed əmri işlətmir.
- `/health/` baza/cache əlçatanlığını yoxlayır, texniki detallar qaytarmır.
- İstehsalat cache-i `prousta_cache` DB cədvəlidir; worker-lər arasında paylaşılır. Mobil birdəfəlik giriş ayrıca DB ticket-i ilə atomik istehlak olunur.
- Yalnız `TRUSTED_PROXY_CIDRS` daxilindəki proxy-lərin forwarded IP/protokolu qəbul edilir. Reverse proxy istifadəçi başlıqlarını özü yenidən yazmalıdır.
- Hər dəqiqə `cleanup_expired` və `cleanup_media` planlaşdırın. İstehsalat media silinmələri davamlı növbəyə yazılır; uğursuzluqlar təkrar icra olunur.
- `private_media/` heç vaxt Nginx/media/CDN ilə açıq təqdim edilməməlidir. Qəbzlər icazəli endpoint və ya 5 dəqiqəlik imzalı URL ilə verilir.
- `.env`, backup, keystore və qəbzlər Git/Docker image-ə daxil edilmir.
