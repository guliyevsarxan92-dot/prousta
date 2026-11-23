# Prousta.az — SEO, GEO və AI axtarış auditi

Tarix: 12.11.2026. GEO burada generativ axtarışlarda görünmə mənasındadır; lokal axtarış ayrıca qiymətləndirilib.

Canlı saytın seçilmiş açıq səhifələri, HTTP başlıqları, robots.txt, llms.txt, sitemap bölmələri və workspace-dəki mövcud kod yoxlanılıb. Canlı bazaya və tətbiq koduna dəyişiklik edilməyib. Bu sənəd audit nəticəsidir.

## Ümumi nəticə

Texniki SEO bazası işləyir. Əsas zəifliklər canlı məzmunun doğruluğu, boş kateqoriyalar, xidmət icraçısının etibarlılığını qiymətləndirməyə yetən məlumatın azlığı və ölçmə boşluqlarıdır. Yeni schema və ya daha çox rayon səhifəsi yaratmaqdan əvvəl bunlar həll edilməlidir.

## Prioritetli tapıntılar

### 1. Yüksək — canlı səhifələrdə sübutlanmayan və ziddiyyətli vədlər

**Təsdiqlənib:** [Fizioterapiya](https://prousta.az/xidmet/fizioterapiya/), [SEO xidməti](https://prousta.az/xidmet/seo-xidmeti/), [Yükdaşıma](https://prousta.az/xidmet/yukdasima/) və [Avtomobil ustası](https://prousta.az/xidmet/avtomobil-ustasi/) səhifələrində aktiv elan yoxdur. Bununla yanaşı, köhnə mətnlərdə yoxlanılmış ustalar, müştəri rəyləri/reytinqi, bütün Bakı üzrə əhatə və 1 aydan 1 ilə qədər zəmanət iddiaları qalır. Bəzi səhifələr özünü Azərbaycanın ən böyük platforması kimi təqdim edir. Eyni köhnə iddialar [Mebel ustası](https://prousta.az/xidmet/mebel-ustasi/) səhifəsində də görünür.

Mövcud modeldə müştəri rəyi/reytinqi və ustanın peşə səriştəsinin yoxlanmasını təsdiqləyən ayrıca mexanizm görünmür. Elanın moderasiyası xidmətin keyfiyyətinin yoxlanması demək deyil. `llms.txt` isə VIP nişanının ixtisas və keyfiyyət təsdiqi olmadığını düzgün bildirir.

**Təsir:** istifadəçi və AI eyni sayt daxilində bir-birinə uyğun gəlməyən məlumat alır. Yanlış zəmanət və əhatə məlumatı sitat gətirilə bilər.

**Tövsiyə:** sübutu olmayan ümumi iddiaları çıxarın. Yalnız elanda açıq göstərilən şərtləri, onların elan sahibinin bəyanatı olduğunu qeyd edərək təqdim edin. Həqiqi rəy sistemi qurulanda rəyin hansı işə və müəllifə aid olduğunu göstərmək mümkün olsun.

### 2. Yüksək — boş və şablon məzmunlu kateqoriyalar indekslənməyə açıqdır

**Təsdiqlənib:** yuxarıdakı dörd boş səhifə `200` və `index, follow` qaytarır. Alt kateqoriya sitemap-ında 104 URL var; bu, onların hamısının boş olması demək deyil.

**Kod səbəbi:** `core/seo.py:83` daxilində `seo_metn` sahəsinin boş olmaması indeksləmə üçün kifayətdir. Mətnin köhnə şablon, görünməyən HTML və ya faydalı xidmət bələdçisi olması fərqləndirilmir.

**Təsir:** axtarışdan gələn istifadəçi real seçim əvəzinə boş siyahı və ümumi reklam mətni görür. Təkrar mətnlər səhifələr arasındakı fərqi azaldır. Bu müşahidə Google cəzasının sübutu deyil.

**Tövsiyə:** keyfiyyəti zəif boş səhifələrə müvəqqəti `noindex, follow` verin və sitemap-dan çıxarın. Elanı olmayan səhifə yalnız ayrıca faydalı, fərdi bələdçi təqdim edirsə indekslənə bilər; sıfır elan təkbaşına avtomatik qadağa olmamalıdır.

### 3. Yüksək — lokal hazırlanan məzmunun nəticəsi canlıda tam görünmür

**Təsdiqlənib:** lokal kataloqda 114 kateqoriya üçün fərdi məzmun var. Canlı kombi səhifəsində fərdi bələdçi görünür, amma fizioterapiya, SEO xidməti, yükdaşıma, avtomobil və mebel nümunələrində köhnə title/description və şablon HTML qalır. Workspace-də müvafiq JSON və kod dəyişikliklərinin bir hissəsi commit olunmayıb.

**Təsir:** lokal testin keçməsi və əhatə sənədində “tamamlandı” yazılması canlı istifadəçinin həmin nəticəni aldığını göstərmir.

**Tövsiyə:** yayımlanacaq konkret versiyanı müəyyənləşdirin; bələdçi məlumatlarını, mənbə manifestini və template dəyişikliklərini birlikdə buraxın. Sonra hər xidmət qrupundan nümunə üzrə canlı title, description, bələdçi, köhnə iddialar və robots vəziyyətini yoxlayın. Dəqiq səbəbin deploy, ad uyğunluğu və ya başqa konfiqurasiya olması hazırkı açıq yoxlama ilə müəyyənləşdirilməyib.

### 4. Yüksək — həssas texniki məqalələrdə ekspert və mənbə sübutu zəifdir

**Təsdiqlənib:** [Kombinin partlayışla yanması haqqında məqalə](https://prousta.az/problemler/kombi-partlayisla-yanir/) müəllif kimi yalnız “Prousta.az redaksiyası” göstərir. Məqalədə adı və ixtisası açıqlanan texniki yoxlayıcı, istehsalçı təlimatına istinad və orijinal diaqnostika nümunəsi yoxdur. `Problem` modelində ayrıca müəllif/yoxlayıcı əlaqəsi də yoxdur. Məqalə ümumi sayt şəklini istifadə edir.

**Təsir:** istifadəçi məsləhətin hansı təcrübəyə və yoxlamaya əsaslandığını qiymətləndirə bilmir. AI cavabları üçün fərqləndirici, yoxlanıla bilən mənbə dəyəri zəif qalır. Bu, konkret AI sisteminin saytı niyə seçmədiyinin sübutu deyil.

**Tövsiyə:** qaz, elektrik və sağlamlıq mövzularını sahə mütəxəssisi yoxlasın; ad, ixtisas, yoxlama tarixi və uyğun ilkin mənbə göstərilsin. Orijinal iş nümunələri və modelə aid izahlar əlavə edilsin. `Organization` müəllif növü özlüyündə schema xətası deyil.

### 5. Orta — bütün ictimai usta profilləri axtarışdan çıxarılır

**Təsdiqlənib:** [Prousta Servis profili](https://prousta.az/istifadeci/1/) həm meta, həm HTTP başlığında `noindex, nofollow` alır. `istifadeci_profil` public view siyahısına daxil deyil. Elanların `Service.provider.url` sahəsi isə həmin profil tipinə bağlanır.

**Təsir:** ustanın adı ilə axtarışdan profilə gəlmək və ustaya aid ayrıca məlumat səhifəsi yaratmaq imkanı məhdudlaşır. Bu, təhlükəsizlik xətası deyil, böyümə imkanını məhdudlaşdıran məhsul seçimidir; təkcə profilin noindex olması elan schema-sını etibarsız etmir.

**Tövsiyə:** ictimai yayıma uyğun, dolğun və aktiv xidməti olan profillər üçün ayrıca indeksləmə qaydası yaradın. Təcrübə, iş portfeli, xidmət əhatəsi və icraçı məlumatı əlavə edin. Şəxsi kabinetlər və boş profillər noindex qalsın.

### 6. Orta — lokal əhatə sərbəst mətnə bağlıdır və real xidmət radiusunu göstərmir

**Təsdiqlənib:** [Yasamal kombi səhifəsi](https://prousta.az/xidmet/kombi-ustasi/yasamal/) sıfır uyğun ərazi elanı səbəbindən düzgün olaraq noindex-dir. [Nərimanov səhifəsi](https://prousta.az/xidmet/kombi-ustasi/nerimanov/) iki uyğun elanla indekslənməyə açıqdır. Ərazi sübutu əsasən `sheher` mətnindən çıxarılır. Məsələn, [431 nömrəli elan](https://prousta.az/elan/431-kombi-ustasi-baki/) təsvirində Binə deyir, amma strukturlaşdırılmış ərazisi Bakı olaraq qalır.

**Təsir:** ünvanı, fəaliyyət yeri və xidmət göstərdiyi rayonlar ayrılmır; bəzi real əhatələr lokal axtarışda təmsil olunmur. Bir elan əsasında açılan lokal səhifələrin əsas bələdçi mətnləri də böyük ölçüdə eynidir.

**Tövsiyə:** ustanın seçdiyi çoxsaylı xidmət əraziləri toplayın, nə vaxt təsdiqləndiyini göstərin. Lokal səhifədə həmin əraziyə aid elanlar və şərtlər əsas olsun. Bakı yazısından bütün rayonlara xidmət nəticəsi çıxarmayın.

### 7. Orta — qiymət məlumatı müqayisə üçün kifayət qədər strukturlaşdırılmayıb

**Təsdiqlənib:** kombi səhifəsində 15–30 AZN aralığı və “15 AZN-dən başlayır” cavabı var. Bu məlumat müxtəlif işləri əhatə edən elan qiymətlərindən hesablanır. Nərimanov səhifəsindəki aralıq da başqa ərazilərin elanlarını əhatə edir. Modeldə qiymətin çağırış, diaqnostika, işçilik və ya tam iş məbləği olması ayrıca saxlanılmır.

**Təsir:** istifadəçi və AI aşağı qiyməti tamamlanmış təmirin tipik qiyməti kimi anlaya bilər. Mövcud yekun qiymət qeydi riski azaldır, lakin müqayisə problemini həll etmir.

**Tövsiyə:** qiymət növü, ölçü vahidi, daxil olan iş/material, ərazi və aktuallıq tarixini toplayın. Fərqli işlərin minimumunu bazar qiyməti kimi təqdim etməyin. Etibarlı müqayisə məlumatı yığılandan sonra qiymət bələdçisi hazırlayın.

### 8. Orta — bəzi elanlar tövsiyə vermək üçün çox az məlumat təqdim edir

**Təsdiqlənib:** [826 nömrəli elan](https://prousta.az/elan/826-kombi-ustasi-baki/) əsasən dörd qısa xidmət/brend ifadəsindən ibarətdir. Təcrübə, işin sərhədi, çağırış haqqı və xidmət şərtləri izah edilmir. Siyahıda çox sayda eyni ümumi başlıqlı kombi elanı var; başlıqlar icraçıları az fərqləndirir.

**Tövsiyə:** elan formasında faydalı xidmət məlumatlarını ayrıca toplayın; başlıqda uyğun olduqda icraçı və ya konkret xidmət fərqini göstərin. İndeksləmə üçün keyfiyyət qaydası sadəcə söz sayına əsaslanmasın. `Service` schema mövcud olmayan təcrübə və etibarı yarada bilməz.

### 9. Orta — platforma və servis mərkəzinin rolu qarışır

**Təsdiqlənib:** `llms.txt` platformanı elan kataloqu kimi təqdim edir, haqqımızda səhifəsi birbaşa əlaqəni vurğulayır. Məqalədə isə “Prousta Təcili Xidmət” çağırışı və platformanın dəstək nömrəsi var; həmin nömrə bəzi ustaların elanlarında da işlənir.

**Təsir:** konkret işi platformanın, əlaqəli servis mərkəzinin, yoxsa müstəqil ustanın görməsi aydın olmaya bilər.

**Tövsiyə:** dəstək və xidmət sifarişi nömrələrinin rolunu açıqlayın. Platformaya bağlı xidmət hesabları varsa əlaqəni görünən şəkildə göstərin; məqalə çağırışları və təşkilat məlumatları eyni biznes modelini təsvir etsin.

### 10. Orta — SEO və AI nəticələrini ölçmək üçün görünən quruluş natamamdır

**Təsdiqlənib:** HTML-də Google Ads `AW-...`, Meta Pixel və Clarity var. Kodda elan üzrə zəng/WhatsApp klikləri izlənir. Açıq mənbədə ayrıca GA4 `G-...` konfiqurasiyası və kliklərin AI/organic mənbəsi ilə əlaqəsini göstərən axın görünmür. Bu, başqa yerdə analytics qurulmadığının qəti sübutu deyil.

**Tövsiyə:** Search Console/Bing məlumatlarını və mövcud analytics quruluşunu yoxlayın. Landing page → trafik mənbəyi → zəng/WhatsApp keçidi üzrə hesabat qurun. ChatGPT və digər AI keçidlərini mövcud referrer/UTM məlumatı olduqda ayırın; bütün AI istifadəsi ölçülə bilən klik yaratmır. Eyni sorğu/ölkə/cihaz üzrə əvvəl-sonra müqayisəsi aparın.

### 11. Aşağı — IndexNow bildirişləri etibarlı növbə ilə təmin edilmir

**Koddan görünən risk:** `core/indexnow.py:82` daemon thread işlədir; davamlı növbə və təkrar cəhd yoxdur. Signal-lar əsasən aktiv elan/məqalənin saxlanmasını bildirir; kateqoriya dəyişiklikləri, silinmə/deaktivləşmə və köhnə slug URL-ləri üçün tam bildiriş axını görünmür.

**Tövsiyə:** IndexNow istifadə ediləcəksə, davamlı növbə, retry və uyğun yaradılma/dəyişmə/silinmə hadisələri əlavə edin. Canlıda açarın aktivliyi və bildiriş qəbulu yoxlanılmayıb. IndexNow ayrıca Google və ya ChatGPT tövsiyəsinə zəmanət deyil.

## Mövcud tövsiyələrdə düzəliş edilməli gözləntilər

- `llms.txt` hazırda faktiki kataloq kimi düzgündür. Onu Google sıralamasını artıran mexanizm kimi prioritetləşdirmək olmaz: Google bu faylın görünməyə və mövqeyə müsbət/mənfi təsir etmədiyini açıqlayır. [Google yeniləməsi, 15 iyun 2026](https://developers.google.com/search/updates#june-2026)
- FAQ istifadəçiyə faydalı ola bilər, amma Google FAQ rich result imkanını 7 may 2026-dan dayandırıb. FAQ schema üzərində əlavə işi xüsusi nəticə görünüşü qazanmaqla əsaslandırmaq olmaz. [Google yeniləməsi, 8 may 2026](https://developers.google.com/search/updates#may-2026)
- Generativ Google nəticələri üçün xüsusi “AI schema” tələb olunmur; indekslənə bilən, faydalı məzmun və mövcud SEO əsasları vacibdir. [Google AI features](https://developers.google.com/search/docs/appearance/ai-features)
- ChatGPT axtarışı üçün OAI-SearchBot-a giriş vacibdir, amma bu, tövsiyə olunmağa zəmanət vermir. [OpenAI publisher FAQ](https://help.openai.com/en/articles/12627856-publishers-and-developers-faq)
- Daha çox eyni rayon mətni yaratmaq əvəzinə, yerli inventar və fərdi dəyər artırılmalıdır. [Google spam siyasəti](https://developers.google.com/search/docs/essentials/spam-policies)

## İşləyən hissələr və yoxlama nəticəsi

- HTTP və `www` ana səhifələri `301` ilə `https://prousta.az/` ünvanına keçir.
- Yoxlanan public səhifələrdə canonical, title/description və JSON-LD var; JSON parse olunur.
- `/elanlar/?page=2` öz canonical-ını saxlayır; mətn axtarışı `noindex, follow` qaytarır.
- `robots.txt`, `llms.txt`, sitemap index və yoxlanan bölmələr `200` qaytarır.
- Elan sitemap-ında 129, məqalə sitemap-ında 82, alt kateqoriya sitemap-ında 104, lokal sitemap-da 35 URL var. Bunlar 12 noyabr tarixindəki snapshot-dır, sabit say deyil.
- OAI-SearchBot, Claude-SearchBot, PerplexityBot və Googlebot User-Agent başlıqları ilə kombi səhifəsi `200` qaytarıb. Bu sorğular real botların IP-lərindən edilməyib; WAF/CDN-in həqiqi botlara münasibəti yalnız bunlarla təsdiqlənmir.
- Lokal olaraq `core.test_seo_geo`, `core.test_service_copy`, `core.test_search`, `core.test_service_content`: **40 test keçdi**. İzolə edilmiş `prousta.test_settings` istifadə olunub. Testlər canlı məzmun keyfiyyətini və faktiki indekslənməni təsdiqləmir.

## Ölçülməyən sahələr

Search Console/Bing hesabları, indekslənmə və seçilmiş canonical hesabatları, backlink keyfiyyəti, real AI cavablarında təmsil olunma tezliyi və mobil Core Web Vitals məlumatı yoxlanılmayıb. Saytın “Google-da indekslənmir”, “AI tövsiyə etmir” və ya “performansı zəifdir” nəticələri bu auditdən çıxarıla bilməz. Açıq axtarış nəticəsi tam indeks hesabatı sayılmır.

İcra ardıcıllığı: əvvəl canlıdakı ziddiyyətli iddialar və zəif boş səhifələr; sonra məzmun versiyasının tam yayımlanması; ardınca ekspert/usta sübutları, ərazi və qiymət strukturu; paralel olaraq nəticələrin ölçülməsi.
