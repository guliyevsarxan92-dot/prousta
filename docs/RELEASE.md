# Buraxılış qaydası

Bu sənəd addımları avtomatik icra etmir. Düzəlişlər zamanı real baza dəyişdirilməyib və deployment edilməyib.

## Buraxılışdan əvvəl

1. Koddan çıxarılmış baza parolunu provayderdə rotasiya edin və istifadə tarixçəsini qiymətləndirin. Git tarixçəsindəki nüsxə də kompromis hesab edilməlidir. Cari `.env`-də yeni lokal `SECRET_KEY` yaradılıb; yerləşdirmə mühitində ayrıca secret təyin edin. Secret dəyişməsi köhnə sessiyaları etibarsız edir.
2. Dəyişiklikdən əvvəl tam DB backup və media inventarı alın. `elanlar_backup_tam.json` tam backup deyil. Backup-ı ayrıca bazaya bərpa edib istifadəçi/ödəniş/balans/mesaj əlaqələrini yoxlayın. Supabase PITR, retention və RPO/RTO parametrlərini hesab səviyyəsində təsdiqləyin.
3. Production surətinin izolə edilmiş nüsxəsində mənfi balansları, sıfır/mənfi ödənişləri və tarixən ləğv edilib yenidən təsdiqlənmiş ödənişləri araşdırın. Yeni constraint-lər səhv məlumatı avtomatik dəyişmir; belə məlumat varsa miqrasiya dayanacaq.
4. Qəbzlər üçün davamlı private volume/bucket hazırlayın. Köhnə Cloudinary/lokal açıq qəbzləri ayrıca yoxlanmış transfer planı ilə private storage-a köçürün. Köçürmə yoxlanmadan əvvəl köhnə faylları silməyin; köhnə açıq URL-lərin ləğvi ayrıca tamamlanmalıdır.
5. Lokal/staging testlərini və mobil build-ləri tamamlayın. iOS üçün `mobile_app/ios/Flutter/GoogleSignIn.xcconfig.example` əsasında düzgün bundle ID-yə aid iOS client ID və reversed ID təyin edin. Bunlar server client ID ilə eyni deyil. Keychain entitlement-i signing profilində yoxlayın.

## Uyğunluq və miqrasiyalar

- `0028`: paylaşılan cache, birdəfəlik mobil ticket və ödənişin `applied_at` nişanı. Mövcud təsdiqlənmiş ödənişlər yenidən kredit verilmədən işarələnir. Keçmiş ləğv/təkrar kredit səhvləri avtomatik düzəldilmir.
- `0029`: chat/unread indeksləri.
- `0030`: mənfi balans və qeyri-müsbət ödəniş constraint-ləri.
- `0031`: media cleanup növbəsi və əlavə elan ödənişi tipi.
- Tarixi `0006`-ya unique constraint-dən əvvəl boş/dublikat nömrələri dolduran addım əlavə edilib. Əvvəllər tətbiq edilmiş `0006` yenidən işlədilmir; mövcud production nömrələri avtomatik yenidən yazılmır.
- Şəxsi API siyahılarında pagination opt-in-dir; yeni müştəri `page` göndərir, legacy v1 array müqaviləsi 1000 elementlik sərhədlə saxlanılır. Veb/backend və yeni mobil buraxılışın yayımını koordinasiya edin; mövcud mobil versiyaları ayrıca uyğunlaşdırın.

## Yerləşdirmə ardıcıllığı

1. Köhnə writer proseslərini dayandırın və ya maintenance pəncərəsi istifadə edin. Köhnə ödəniş signal-ı ilə yeni modelin paralel yazmasına icazə verməyin.
2. `requirements.txt` əsasında asılılıqları quraşdırın; Django 5.2.18 istifadə olunduğunu yoxlayın. Yeni Django ayrıca `/tmp` mühitində test olunub; workspace venv-i avtomatik yüksəldilməyib.
3. Yalnız təsdiqlənmiş hədəf bazada miqrasiyaları icra edin. Default cache cədvəli yeni versiya başlamazdan əvvəl mövcud olmalıdır.
4. Statik manifest-i yaradın (`collectstatic`) və ya onu ehtiva edən Docker image-i istifadə edin. Docker image-də `.env` və media olmur.
5. `DEBUG=False`, konkret hostlar, düzgün secret/Google/SMTP dəyişənləri, private volume və trusted proxy şəbəkələrini təyin edin. TLS reverse proxy-də məcburi olmalıdır. HSTS subdomain/preload qərarını faktiki domen əhatəsinə əsasən verin.
6. Yeni prosesləri başladın; health/readiness, login, reset email-i, şəkil/qəbz, mesaj cavabı və test ödənişinin nəticəsini staging-də yoxlayın.
7. `cleanup_expired` və `cleanup_media` əmrlərini hər dəqiqə planlaşdırın. Cleanup növbəsinin yaşını/sayını, uğursuzluqları, 5xx, DB gecikməsi və disk həcmini monitorinq edin.

## Rollback

Ödənişlər yeni versiyada qəbul edildikdən sonra köhnə maliyyə signal-ına kor-koranə qayıtmayın. `applied_at` nişanını anlamayan köhnə kod təkrar kredit yarada bilər. Əvvəl writer-ləri dayandırın, əməliyyatları uzlaşdırın və DB backup-a qayıtmağın sonrakı ödənişlərə təsirini qiymətləndirin. Qəbz və DB backup-larını eyni bərpa nöqtəsi üzrə saxlayın.

## Hesab/mühit səviyyəsində qalanlar

DB credential rotasiyası, real backup restore, private receipt transfer, TLS/proxy/SMTP və alert-lər, iOS OAuth/signing, Android release sertifikatı, təmsilçi həcmdə query planları və yük sınağı. Lokal test nəticələri bunların production-da tamamlandığını bildirmir.
