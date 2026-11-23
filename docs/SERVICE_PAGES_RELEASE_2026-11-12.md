# Xidmət səhifələri və Bakı əhatəsi

12.11.2026. İş mövcud elanları saxlayır; yeni elan və kateqoriya qeydi yaratmır.

## Hazırlanan səhifələr

Beş mövcud ana səhifə: `/xidmet/kombi-ustasi/`, `/xidmet/su-sizma/`, `/xidmet/kanalizasiya-ustasi/`, `/xidmet/santexnik/`, `/xidmet/havalandirma-ustasi/`.

Altı ayrıca xidmət bələdçisi:

- `/xidmet/kombi-yuyulmasi/`
- `/xidmet/havalandirma-qurasdirilmasi/`
- `/xidmet/havalandirma-temizlenmesi/`
- `/xidmet/zont-muherrik-temizlenmesi/`
- `/xidmet/boyler-yuyulmasi/`
- `/xidmet/qazan-yuyulmasi/`

Hər istiqamətdə fərdi iş həcmi, qiymət amilləri, sifarişdən əvvəl hazırlanacaq məlumatlar, qəbul yoxlamaları, üç görünən FAQ və uyğun xidmət keçidləri var. Texniki iddialar Fernox, FLIR, RIDGID, Greenheck, Ariston və Viessmann mənbələri ilə məhdudlaşdırılıb. Real görülmüş iş və ya ekspert yoxlaması uydurulmayıb.

## Təklif və əlaqə

İstifadəçi qiymətləri, hesabı və ərazini bu sessiyada təsdiqləyib:

- `superadmin`; sifariş telefonu `+994515888884`.
- Su sızma təyini 80 AZN, kanalizasiya açılması 80 AZN.
- Kombi/radiator yuyulması 30 AZN-dən; yekun məbləğ radiator sayı və iş həcminə bağlıdır.
- Zəmanətli xidmət təklifidir; müddət, əhatə və təkrar müraciət şərtləri göstərilmədiyindən rəqəm uydurulmur, icraçı ilə dəqiqləşdirilməsi tələb olunur.

Təklif yalnız aktiv hesab və onun uyğun ictimai elanı olduqda göstərilir. Santexnika və boyler üçün sahibin təsdiqlədiyi əlaqəli xidmət elanları hesabı təsdiqləmək üçün istifadə edilə bilər; yeni elan yaradılmır. Elan sahibinin adı/profili və platformanın broker rolu ayrı göstərilir. 80 AZN təkliflər decimal qiymət kimi, 30 AZN başlanğıc qiymət isə `minPrice` kimi təqdim olunur. Aktiv olmayan təklifin rəqəmi ümumi bələdçi mətnində sabit reklam kimi qalmır.

Sifariş hazırlayıcısı ünvan/rayon, avadanlıq, iş təsviri və kombi yuyulması üçün radiator sayını bir mətnə yığır. Qiymət kalkulyatoru deyil; radiator üçün təsdiqlənməmiş vahid qiymət olmadığına görə yekun məbləğ hesablamır. Mətn brauzerdə hazırlanır, istifadəçi özü WhatsApp-a keçib göndərir. JavaScript-siz əsas məzmun və hazırlıq siyahısı oxunur.

## Bakı rayonlarının indekslənməsi

Sahib yalnız Bakı üzrə bütün rayonları təsdiqləyib. Qayda `core/service_pages/__init__.py` daxilində açıq registry-dir; məlumatın mənbəyi hesab sahibinin bu sessiyadakı bəyanatıdır.

Yalnız `superadmin`-in təsdiqlənmiş xidmət kateqoriyalarına aid aktiv, vaxtı bitməmiş elanları Bakı rayonları üzrə əhatə sübutu sayılır. Eyni elan ünvan və əhatə ilə iki dəfə sayılmır. Qayda başqasının elanına, başqa kateqoriyaya, deaktiv hesaba və ya vaxtı bitmiş elana şamil edilmir. Pirallahı rayonu lokasiya kataloquna əlavə edilib.

View, lokal say, uyğun elanlar, axtarış sıralaması və sitemap eyni əhatə mənbəyini istifadə edir. Sumqayıt, Xırdalan, Masazır və digər Abşeron ərazilərinə Bakı təsdiqindən avtomatik əhatə çıxarılmır. Başqa icraçının elanı həmin ərazini açıq göstərirsə mövcud qayda ilə nəzərə alınır.

## Köhnə URL-lər

Canlı bazada 570 və 575 nömrəli elan qeydləri yoxdur. Lokal ehtiyat nüsxədə onların superadmin-dən başqa sahiblərə aid olduğu görünüb. Eyni icraçı, telefon və məzmunla dəqiq aktiv davam müəyyən edilməyib. İstifadəçi aktiv elanlarla işləməyi tapşırıb; buna görə köhnə qeydlər yenidən yaradılmır və əlaqəsiz elana avtomatik 301 əlavə edilmir.

`audit_search_recovery` əmri tarixi URL CSV-sini oxuyaraq mövcud, aktiv olmayan/silinmiş elanları və lokal əhatə sübutunu ayırır. Əmr məlumatı dəyişmir:

```bash
python manage.py audit_search_recovery \
  --source docs/SEARCH_CONSOLE_PRIORITIES_2026-11-12.csv \
  --output /tmp/search-recovery.csv
```

## Yoxlama və yayım

- Lokal tam dəst: 111 test; 108 keçib, PostgreSQL concurrency üçün 3 test atlanıb.
- Yeni istiqamətlər üzrə 11 test: canonical/pagination, görünən FAQ və JSON-LD, qiymət atribusiyası, aktivlik, sübutlu Bakı əhatəsi, şəhər sərhədləri, təkrar sayın qarşısı və qeydlərə toxunmayan recovery auditi.
- Django check, migration drift və JavaScript sintaksis yoxlamaları keçib; DB miqrasiyası tələb olunmur.
- Headless Chrome-da 390px enində kombi səhifəsi: mətn hazırlığı və doğru WhatsApp nömrəsinə URL yoxlanıb; üfüqi daşma yoxdur.

Canlı paket yalnız tapşırığa aid faylları və beş kateqoriyanın metadata dəyişikliyini ehtiva edir. Lokal workspace-dəki digər yayımlanmamış xidmət kataloqları, ödəniş və təhlükəsizlik dəyişiklikləri bu paketə daxil edilmir. Paket quraşdırılmazdan əvvəl cari faylların SHA256 imzaları yoxlanır və ayrıca backup saxlanır. Uğursuz yoxlamada dəyişən mənbələr bərpa edilir. Yeni sitemap bölməsi: `/sitemap-xidmet_beledcileri.xml`.

## Canlı nəticə

12 noyabrda paket 29 fayl ilə tətbiq edildi. Backup: `/home/ubuntu/prousta-backups/services-20261112-134013`.
Canlı mühitdə izolə edilmiş 10 xidmət testi, sistem yoxlaması və collectstatic keçdi; tətbiq uğurla yeniləndi. Elan, istifadəçi və ödəniş qeydləri dəyişdirilmədi.

11 xidmət URL-i HTTPS üzərindən 200 cavabı, canonical metadata, parse olunan JSON-LD və elan sahibinin təklif bloku ilə yoxlanıldı. İki 80 AZN təklifi və 30 AZN başlanğıc təklifi görünür. Yeni CSS/JS faylları 200 qaytarır. Kombi/Yasamal və su sızması/Pirallahı yenidən indekslənməyə açıqdır. Təsdiqlənməyən Kombi/Xırdalan noindex olaraq qalır.

Lokal sitemap-da 81 xidmət–ərazi URL-i, yeni bələdçi sitemap-ında 6 URL, sitemap index-də 8 bölmə var. Bunlar snapshot saylarıdır və elanların aktivliyinə görə dəyişir. Əsas trafik gətirən kombi məqaləsi və `/health/` də 200 qaytarır. HTTP yoxlamaları `SERVICE_PAGES_LIVE_CHECK_2026-11-12.json` faylındadır.

Bu yoxlama Google-un səhifələri artıq yenidən indekslədiyini və ya mövqelərin yüksəldiyini təsdiqləmir. URL Inspection və sonrakı Search Console nəticələri ayrıca izlənməlidir.
