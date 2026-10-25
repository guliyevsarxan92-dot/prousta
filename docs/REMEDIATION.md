# Auditdən sonra düzəliş reyestri

Tarix: 25.10.2026. Sıra nömrələri ilkin auditin 53 maddəsinə uyğundur.

**Statusların mənası:** “Kodda həll” mənbədə düzəlişin və uyğun lokal yoxlamanın hazır olmasıdır. Production-a yerləşdirildiyini bildirmir. “Qismən” əlavə mühit, məlumat, hesab və ya performans yoxlaması tələb edir.

47 maddə üzrə kod düzəlişi tamamlanıb; 6 maddə qismən açıqdır: **01, 07, 27, 39, 46, 47**. Mövcud istifadəçi dəyişiklikləri saxlanılıb. Real Supabase bazasına yazılmayıb, production miqrasiyası və deployment edilməyib.

| № | Problem | Status | Həll və əsas fayllar | Qalan iş / yoxlama |
|---|---|---|---|---|
| 01 | Kodda DB credential | Qismən | `prousta/settings.py` içindəki fallback çıxarılıb; `DATABASE_URL` məcburidir. `.env.example` təhlükəsiz nümunədir. | Köhnə credential provayderdə rotasiya olunmalıdır; Git tarixçəsində olması da nəzərə alınmalıdır. |
| 02 | Admin bildirişində stored XSS | Kodda həll | `static/js/admin_notifications.js`: istifadəçi mətnləri DOM vasitəsilə escape edilir. | Dəyişdirilmiş JS üçün syntax yoxlaması keçib. |
| 03 | DEBUG, secret və host default-ları | Kodda həll | `prousta/settings.py`: DEBUG default false, məcburi uzun secret, konkret hostlar. Lokal ignored `.env` üçün yeni secret yaradılıb. | Production ayrıca secret və hostlarla buraxılmalıdır. |
| 04 | Köhnə Django | Kodda həll | `requirements.txt`: Django 5.2.18. Bu versiya ayrıca `/tmp` paket yolunda və Docker image-də yoxlanılıb. | Workspace venv-i avtomatik yüksəldilməyib; buraxılışda manifest quraşdırılmalıdır. |
| 05 | Google email əsasında hesabın ələ keçirilməsi | Kodda həll | `core/identity.py`, `core/api_views.py`, `core/mobile_auth.py`, settings pipeline: provider subject əsasında giriş, parollu hesab üçün açıq əlaqələndirmə. | Collision və təhlükəsiz legacy adoption regression testləri var. |
| 06 | Nəzarətsiz upload | Kodda həll | `core/validation.py`: format, ölçü, piksel və dimension limitləri; şəkil JPEG-ə yenidən kodlanır. | Invalid və həddən böyük upload testləri keçib. |
| 07 | Qəbzlərin açıq media URL-i | Qismən | Yeni qəbzlər ayrıca private storage-a yazılır; `core/receipts.py`: sahib/icazəli admin və ya 5 dəqiqəlik imzalı keçid, private/no-store cavab. | Köhnə açıq faylların transferi, URL-lərin ləğvi və davamlı private volume tələb olunur. |
| 08 | Staff üçün çatışmayan icazə yoxlamaları | Kodda həll | `core/admin.py`: export, hesabat və bildirişlər model icazələrini yoxlayır. | İcazəsiz staff üçün regression testləri var. |
| 09 | Vebdə bloklamanın keçilməsi | Kodda həll | `core/listings.py`, `core/views.py`: görünürlük və mesajlaşma qaydaları paylaşılır. | Bloklanmış tərəflər üçün testlər keçib. |
| 10 | Gözləyən elanların açıq görünməsi | Kodda həll | `check_access` və `visible_listings`: sahibi və icazəli moderator xaricində pending elan açılmır. | API/veb görünürlük testləri var. |
| 11 | Ödənişin təkrar kreditləşdirilməsi | Kodda həll | `Odenis.save`, `core/payments.py`, migration 0028: row lock və `applied_at`; tətbiq edilmiş maliyyə sahələri dəyişdirilə bilmir. | Paralel təsdiq PostgreSQL-də yalnız bir kredit yaradıb. |
| 12 | Admin-də transaction import xətası | Kodda həll | `core/admin.py`: import və admin əməliyyat axını düzəldilib. | Sistem və admin regression yoxlamaları keçib. |
| 13 | Paralel elan yaradarkən balansın mənfiyə düşməsi | Kodda həll | `core/listings.py`: profil lock, limit/duplikat yoxlaması və debit eyni transaction-dadır; DB constraint əlavə edilib. | Real PostgreSQL paralel yazı testi keçib. |
| 14 | Paralel VIP alışında ikiqat debit | Kodda həll | `core/payments.py`: profil və elan lock, təkrar aktiv paket yoxlaması. | Real PostgreSQL concurrency testi keçib. |
| 15 | Save zamanı bitmiş VIP-in yenilənməsi | Kodda həll | `Elan.save`: müddəti bitmiş VIP normal vəziyyətə keçir, save yeni müddət vermir. | Regression testi var. |
| 16 | Uyğunsuz şifrə siyasəti | Kodda həll | Django validator-ları veb/API-də paylaşılır; 128 simvol yuxarı həddi var; şifrə whitespace-i dəyişdirilmir. | Validator və giriş testləri keçib. |
| 17 | API sorğu limiti yoxdur | Kodda həll | `core/throttles.py`, settings: anon/user/write/auth limitləri; ayrıca mobil Google yoxlaması provider çağırışından əvvəl məhdudlaşdırılır. | DRF və mobil Google 429 testləri var. Limitlər production trafikdə izlənməlidir. |
| 18 | Təhlükəli şifrə bərpası | Kodda həll | Django reset token/link axını, generic cavab və sorğu limiti; SMTP env parametrləri. | Email-link və mövcud olmayan hesab cavabı test edilib; real SMTP buraxılışda yoxlanmalıdır. |
| 19 | Müddətsiz/plaintext mobil token | Kodda həll | `core/authentication.py`: token expiry və revoke. Flutter secure storage, köhnə plaintext tokenin uğurlu köçürülmədən sonra silinməsi. | Expiry, revoke, offline və secure migration testləri var. |
| 20 | Yanlış JSON tipləri ilə 500 | Kodda həll | `ValidatedAPIView`, `core/validation.py`: object, scalar və ID yoxlaması, validation error üçün 400. | Səhv JSON/null/field testləri keçib. |
| 21 | Elan redaktəsində qeyri-düzgün qiymət və sahələr | Kodda həll | Paylaşılan `listing_values` və `update_listing`: mətn, qiymət, telefon, kateqoriya yoxlanır. | Mənfi, qeyri-sonlu və səhv precision qiymət testləri var. |
| 22 | Duplikat kateqoriya və pulsuz limitin keçilməsi | Kodda həll | Create/update/reactivate eyni xidmət qaydalarını istifadə edir; profil lock altında yoxlanır. | Limit və reactivation testləri var. |
| 23 | Ödəniş tipi/məbləği yoxlanmır | Kodda həll | Tip, aktiv paket, dəqiq tarif, maksimum 500 AZN və müsbət məbləğ; DB constraint. | Yanlış məbləğ və paket testləri keçib. |
| 24 | Fayl silinməsi və rollback uyğunsuzluğu | Kodda həll | `core/media_cleanup.py`, signals, migration 0031: davamlı cleanup növbəsi, post-commit davranış, retry, paylaşılmış fayl istinadlarının yoxlanması; upload rollback kompensasiyası. | Production-da `cleanup_media` planlaşdırılmalıdır; rollback/retry/reference testləri var. |
| 25 | Chat N+1 və təkrar tam tarixçə | Kodda həll | API grouped conversations, əlaqələrin əvvəlcədən yüklənməsi, 100 mesajlıq cursor-lar; Flutter incremental polling və köhnə mesajların ayrıca yüklənməsi. | Query sayı və pagination regression testləri var. |
| 26 | Digər N+1 və səhifələnməyən siyahılar | Kodda həll | Kateqoriya sayları qruplanır; şəxsi API siyahıları səhifələnir; veb profil, favoritlər, istifadəçi elanları və mesajlar səhifələnir. Profil statistikası SQL aggregate-dir. | Legacy API array cavabı maksimum 1000-dir; yeni müştəri paging göndərir. Bütün səhifələri birdən toplayan mobil şəxsi siyahılar gələcəkdə incremental UI-a keçirilə bilər. |
| 27 | Bahalı axtarış/MD5 rotasiyası | Qismən | Query/seed limitləri, görünürlük və VIP expiry qaydaları düzəldilib, rotasiya ayrıca modula çıxarılıb. | PostgreSQL-də MD5 sort qalır. Təmsilçi məlumatda `EXPLAIN ANALYZE`, p95 yük ölçümü və nəticəyə uyğun indeks/rotasiya strategiyası tələb olunur. |
| 28 | Elan expiry yalnız trafikdən asılıdır | Kodda həll | Aktiv görünürlük hər oxunuşda tarixə baxır; `cleanup_expired` ayrıca əmri var. | Əmri scheduler-də aktivləşdirmək release addımıdır. |
| 29 | Worker-lər arasında cache/login vəziyyətinin itməsi | Kodda həll | Production DatabaseCache; migration 0028-də cache cədvəli. Mobil giriş ticket-ləri hash-lənmiş, DB-də və birdəfəlikdir. | Müstəqil cache instance və ticket replay testləri keçib. |
| 30 | Banner beacon CSRF xətası | Kodda həll | `templates/base.html`: uyğun GET impression sorğusu istifadə olunur. | JS/template yoxlamaları keçib. |
| 31 | Banner expiry/cache köhnəlməsi | Kodda həll | Vaxt filtri, cache oxunuşunda expiry və save/delete/bulk invalidation. | Banner expiry regression testi var. |
| 32 | Mobildə çoxsaylı şəkil silinmir | Kodda həll | Silinəcək ID-lər bütöv JSON array kimi multipart-a göndərilir; server array-i yoxlayır. | Flutter serialization və backend deletion testləri keçib. |
| 33 | WhatsApp telefon formatı | Kodda həll | E.164 normallaşdırma; veb tel/WhatsApp keçidləri eyni nömrədən yaranır. | +994 format regression testi var. |
| 34 | Əsas şəkil nəzərə alınmır | Kodda həll | Model `primary_photo`, serializer və kartlar əsas işarəli şəkli seçir. | Primary photo regression testi var. |
| 35 | Köhnə mobil filtr cavabı yeni nəticəni əvəz edir | Kodda həll | ElanProvider request generation və stale response yoxlaması. | Gecikdirilmiş iki cavabla Flutter testi keçib. |
| 36 | Offline başlanğıcda token silinir | Kodda həll | Şəbəkə/server xətasında token saxlanılır; 401 ayrıca işlənir. | Offline və 401 testləri keçib. |
| 37 | Hesab dəyişəndə şəxsi məlumat cache-i qalır | Kodda həll | User binding private state-i təmizləyir; Navigator user ID ilə yenilənir; gecikmiş profil və list cavabları session token-i yoxlayır. | Logout-dan sonra gecikmiş profil cavabı regression testi keçib. |
| 38 | HTTP timeout yoxdur | Kodda həll | `BoundedClient`: send və response stream üçün timeout, generic decode xətası, test client injection. | Flutter analyzer və mock HTTP testləri keçib. |
| 39 | iOS Google login konfiqurasiyası | Qismən | xcconfig nümunəsi, plist dəyişənləri, Keychain entitlements və Xcode wiring hazırdır. | Həqiqi iOS OAuth ID/reversed ID, signing profili və cihaz testi tələb olunur; Linux-da yoxlanmayıb. |
| 40 | Android release debug signing fallback | Kodda həll | `build.gradle.kts`: release üçün düzgün signing tələb olunur; debug fallback çıxarılıb. | Debug APK yığılıb. Release sertifikatı ilə imzalanma ayrıca buraxılış addımıdır. |
| 41 | Olmayan pagination səhifəsi 200 qaytarır | Kodda həll | `strict_page` ilə səhv/out-of-range səhifə 404-dür. | SEO/pagination regression testləri var. |
| 42 | Sitemap səhifələrinin indeksdə itməsi | Kodda həll | Sitemap index və ayrıca section URL-ləri. | Sitemap regression testi keçib. |
| 43 | Structured data telefon və image URL səhvləri | Kodda həll | Elandakı telefon, E.164 və `absolute_media` filter; absolute image metadata. | Template və SEO regression yoxlamaları keçib. |
| 44 | Hər səhifədə saxta conversion | Kodda həll | Qlobal conversion trigger çıxarılıb. | Yeni conversion hadisəsi biznes qaydası müəyyən edilmədən əlavə olunmayıb. |
| 45 | Modal klaviatura/ARIA çatışmazlığı | Kodda həll | Role/label/modal atributları, focus trap, Escape və focus restore. | JS/template yoxlaması keçib; real screen reader və cihaz sınağı buraxılış QA-sına daxildir. |
| 46 | Deployment, backup və monitorinq çatışmazlığı | Qismən | Dockerfile, `.dockerignore`, SQLite/PostgreSQL və Flutter CI addımları, readiness, env nümunəsi, release/rollback runbook. | Production TLS/proxy/SMTP, scheduler, alert-lər və real backup restore təsdiqlənməlidir. Yeni CI konfiqurasiyası remote runner-də hələ icra edilməyib. |
| 47 | Köhnə sənədlər və istifadəsiz prototiplər | Qismən | Backend/mobile README, release qaydası və bu reyestr yenilənib. | Köhnə prototip və asset-lər avtomatik silinməyib; istifadə statusu ayrıca təsdiqlənib təmizlənməlidir. |
| 48 | 0006-da duplicate boş nömrə migration xətası | Kodda həll | Unique constraint-dən əvvəl boş/duplikat nömrələr backfill edilir. | 0005-dən cari sxemə upgrade testi keçib. Əvvəl tətbiq edilmiş production migration yenidən işləmir. |
| 49 | CSV formula injection | Kodda həll | `SafeCSVWriter` formula prefix-lərini neytrallaşdırır. | Regression testi keçib. |
| 50 | Vebdə sahib mesaja cavab verə bilmir | Kodda həll | Ayrı cavab route-u; iştirakçı və blok yoxlamaları; uyğun receiver/template. | Reply regression testi keçib. |
| 51 | Kritik test və CI çatışmazlığı | Kodda həll | Maliyyə/auth/upload/visibility/cache/SEO/media regression testləri, 3 PostgreSQL concurrency testi, migration upgrade testi, Flutter testləri və CI. | Lokal nəticələr aşağıdadır; remote CI və real cihaz QA-sı ayrıca yoxlanmalıdır. |
| 52 | Şəkil emalında həddən artıq CPU/yaddaş | Kodda həll | Upload piksel/ölçü limitləri, JPEG normallaşdırma, watermark analizi üçün maksimum 800×800 iş sahəsi. | Limit və upload regression testləri keçib; real trafikdə latency ölçülməlidir. |
| 53 | Flutter web-də dart:io/File uyğunsuzluğu | Kodda həll | XFile/bytes multipart və memory preview; platformadan asılı File istifadəsi çıxarılıb. | Flutter web build və byte upload testi keçib. |

## Yoxlama nəticələri

- Django **5.2.18**, ayrıca PostgreSQL 16: **59 test, hamısı keçib**; concurrency testləri burada atlanmayıb.
- Açıq istifadəçi profilinin son pagination əlavəsi ayrıca PostgreSQL regression testində də keçib; müvəqqəti PostgreSQL prosesi yoxlamalardan sonra dayandırılıb.
- SQLite: **59 test, 56-sı keçib, 3 PostgreSQL concurrency testi gözlənildiyi kimi atlanıb**. Şəxsi və açıq profil səhifələməsinin son yoxlamaları daxildir.
- Flutter: **9 test keçib**, `dart analyze --fatal-infos .` xətasızdır.
- Flutter web release build: uğurlu (`--no-pub --no-wasm-dry-run`).
- Android debug APK: uğurlu. Release signing və iOS build test edilməyib.
- Docker image: uğurla yığılıb; collectstatic **235 fayl, 619 post-process** tamamlayıb. Unfold-un Django admin üçün 3 eyni adlı JS override xəbərdarlığı var; ilk tapılan Unfold faylları seçilir.
- Şəbəkəsiz müvəqqəti Docker konteynerində Django `check` və `pip check` keçib.
- `makemigrations --check --dry-run`: əlavə model dəyişiklikləri aşkar edilməyib.
- Python AST və bütün HTML template-lərinin compile yoxlaması, dəyişdirilmiş JS fayllarının syntax yoxlaması və `git diff --check` keçib.
- Media retry testindəki “Media cleanup failed; queued for retry” mesajı qəsdən simulyasiya edilmiş storage xətasına aiddir; testin uğursuzluğu deyil.
- Production parametrləri ilə, real DB-yə qoşulmadan `check --deploy` icra edilib: **0 error, 2 warning** — HSTS include-subdomains və preload. Bütün subdomain-lərin HTTPS vəziyyəti təsdiqlənmədiyinə görə bu seçimlər avtomatik aktivləşdirilməyib.
- Real provider/SMTP, production DB, backup restore, remote CI, browser/screen reader, yük sınağı və real cihaz sınaqları bu lokal nəticələrə daxil deyil.

Əsas icra əmrləri:

```bash
# Backend yoxlamalarında Django 5.2.18 ayrıca paket yolundan istifadə edilib:
PYTHONPATH=/tmp/prousta-django-5.2.18 PYTHONDONTWRITEBYTECODE=1 venv/bin/python manage.py check --settings=prousta.test_settings
PYTHONPATH=/tmp/prousta-django-5.2.18 PYTHONDONTWRITEBYTECODE=1 venv/bin/python manage.py makemigrations --check --dry-run --settings=prousta.test_settings
PYTHONPATH=/tmp/prousta-django-5.2.18 PYTHONDONTWRITEBYTECODE=1 venv/bin/python manage.py test core --settings=prousta.test_settings --noinput
# PostgreSQL icrasında əlavə TEST_DATABASE_URL yalnız müvəqqəti unix socket-ə verilib.
# Əlavə olaraq son profil dəyişməsi üçün tək regression testi PostgreSQL-də təkrar işlədilib.

# Flutter SDK cache çıxışı ilə bu əmrlərin Flutter tool snapshot ekvivalentləri icra edilib:
flutter test --no-pub
dart analyze --fatal-infos .
flutter build web --no-pub --no-wasm-dry-run
flutter build apk --debug --no-pub

docker build -t prousta-audit:local .
docker run --rm --network none prousta-audit:local python manage.py check --settings=prousta.test_settings
docker run --rm --network none prousta-audit:local pip check
node --check static/js/admin_notifications.js
node --check static/js/motion.js
git diff --check
```

## İcra ardıcıllığı

1. **P0:** DB credential rotasiyası; tam DB/media backup və ayrıca restore; köhnə açıq qəbzlərin private transfer planı.
2. **P1:** İzolə edilmiş production surətində 0028–0031 miqrasiyaları və əvvəlki balans/ödəniş qeydlərinin uyğunluğu; sonra koordinasiyalı backend/mobil buraxılış.
3. **P1:** Private volume, TLS/proxy, SMTP, cleanup scheduler və alert-lər; staging smoke sınağı; Android release signing və iOS Google/Keychain cihaz sınağı.
4. **P2:** Təmsilçi məlumatla PostgreSQL query planları və yük sınağı; MD5 rotasiyası üçün ölçüyə əsaslanan qərar.
5. **P3:** Köhnə asset/prototip inventarı və istifadəsi təsdiqlənmiş təmizləmə.

Buraxılışın ətraflı ardıcıllığı və rollback məhdudiyyətləri: [RELEASE.md](RELEASE.md).
