# SEO, lokal axtarış və GEO təkmilləşdirmələri

25.10.2026 — mənbə kodunda tətbiq edilib; deployment və real bazada dəyişiklik edilməyib.

## Tətbiq edilənlər

1. **Vahid metadata:** title, description, canonical, hreflang, Open Graph və Twitter məlumatı `core/seo_metadata.py` vasitəsilə hazırlanır. Kateqoriya, elan, bələdçi, bloq siyahısı və pagination eyni URL qaydalarından istifadə edir. Hər səhifənin JSON-LD WebPage URL-i də həmin canonical-dır.
2. **İndeksləmə qaydaları:** mətnli axtarış və filtr variantları `noindex, follow` alır; boş `q=` əsas siyahını noindex etmir. Şəxsi səhifələr, API və xətalı cavablar HTTP `X-Robots-Tag` ilə də qorunur. Robots qaydaları crawler-in noindex olan axtarış səhifələrini oxumasını qadağan etmir.
3. **Əraziyə dair real sübut:** lokal sitemap bütün kateqoriyaları bütün rayonlara vuraraq yaradılmır. Yalnız aktiv, vaxtı bitməmiş elanın ərazi mətninə uyğun kombinasiyalar daxil edilir. `Binəqədi` sözü `Binə` kimi qəbul edilmir; ümumi `Abşeron` məlumatı avtomatik Xırdalan sübutu sayılmır. Elanında uyğun ərazi göstərilməyən lokal səhifələr noindex olur.
4. **Mövcud axtarış davranışı saxlanılıb:** rayon seçimi başqa ərazilərin elanlarını gizlətmir. Lokal səhifə uyğun ərazini göstərən elan sayını və onların keçidlərini ayrıca verir. Elanın ərazi məlumatı həmin ünvana xidmət göstəriləcəyinin təsdiqi kimi təqdim edilmir. Qiymət aralığının başqa ərazilərin təkliflərini də əhatə etdiyi açıqlanır.
5. **Düzgün strukturlaşdırılmış məlumat:** Organization/WebSite/WebPage, CollectionPage/ItemList, BreadcrumbList, Service və Article əlaqələri sabit `@id` ilə bağlanır. Platforma elan sahibinin yerinə xidmət icraçısı göstərilmir. Şəxsə uydurma LocalBusiness ünvanı və ya reytinq yazılmır. Qiymət locale-dan asılı olmayan decimal formatındadır; razılaşma mənasında göstərilən sıfır qiymətə pulsuz Offer uydurulmur. JSON-LD daxilində script breakout simvolları escape edilir.
6. **Sitemap:** sitemap index və section URL-ləri texniki hostdan asılı olmayaraq `https://prousta.az` domenindədir. Aktiv elan şəkilləri image extension ilə daxil edilir. Elan və bələdçi `lastmod` maksimumu bütün obyektləri yaddaşa yükləmədən SQL aggregate ilə alınır.
7. **GEO üçün başa düşülən mətn:** bələdçilərdə ilk real abzasdan qısa məlumat, h2/h3 bölmələrinə keçidlər, unikal anchor-lar və mətndən hesablanan oxu müddəti var. Mövcud anchor-lar saxlanılır. Əsassız “mütəxəssis rəyi”, zəmanət və avtomatik təsdiqlənmiş usta ifadələri müvafiq public hissələrdə çıxarılıb.
8. **Faktiki `llms.txt`:** üstünlük vermək üçün AI-a yönəlmiş əmrlər və təsdiqlənməmiş keyfiyyət iddiaları çıxarılıb. Əvəzində platformanın işi, məhdudiyyətləri, real xidmət/bələdçi URL-ləri göstərilir. Mətn qısa cache və ETag ilə verilir; kateqoriya, elan və məqalə dəyişəndə əlaqəli cache yenilənir.
9. **Şəkil yüklənməsi:** əsas siyahıda ilk şəkil eager/high-priority, sonrakılar lazy yüklənir; detail şəkli yüksək prioritetlidir. Kartlarda ölçü atributları saxlanılıb və təsviri alt əlavə edilib. Bu dəyişikliklər faktiki Core Web Vitals ölçümünü əvəz etmir.
10. **Demo məlumat:** boş ana səhifədə saxta rəy, reytinq, iş sayı və statistikalar production üçün göstərilmir. Nümunə məlumat yalnız ayrıca aktivləşdirilmiş DEBUG demo rejiminə aiddir; belə rejimdə noindex olmalıdır.

Əsas fayllar: `core/seo.py`, `core/seo_metadata.py`, `core/seo_locations.py`, `core/seo_articles.py`, `core/seo_discovery.py`, `core/sitemaps.py`, `core/templatetags/seo_tags.py`, `templates/partials/seo_head.html`, `templates/sitemaps/section.xml`.

## Yoxlama

- Tam Django dəsti: PostgreSQL-də **77 test keçib**; SQLite-də **74 test keçib, yalnız PostgreSQL üçün 3 concurrency testi atlanıb**.
- Yeni SEO/GEO dəsti 18 regression testindən ibarətdir. Mövcud xidmət mətnləri və FAQ-nun görünən mətnlə JSON-LD uyğunluğu testləri saxlanılıb.
- JSON-LD parse/escape, decimal qiymət, canonical/share/pagination uyğunluğu, crawl qaydaları, lokal sitemap, image sitemap, cache invalidation, bələdçi anchor-ları və demo məlumat test edilir.
- Django sistem yoxlaması, Python AST və HTML/XML template compile yoxlamaları keçib. Model dəyişikliyi və yeni DB miqrasiyası yoxdur.
- SEO/GEO mənbəyini ehtiva edən Docker build və `collectstatic` uğurludur. Image `prousta-audit:local` adı ilə yalnız lokal hazırlanıb; deployment edilməyib.

Təkrar icra:

```bash
python manage.py check --settings=prousta.test_settings
python manage.py test core.test_seo_geo core.test_service_copy core.test_search --settings=prousta.test_settings --noinput
python manage.py test core --settings=prousta.test_settings --noinput
python manage.py makemigrations --check --dry-run --settings=prousta.test_settings
```

PostgreSQL yoxlaması üçün `TEST_DATABASE_URL` yalnız README-dəki izolə edilmiş `/tmp/prousta-isolated-pg-...` socket-i qəbul edir. Workspace `.env` bazası testdə istifadə edilmir.

## Buraxılışdan sonra görüləcək işlər

1. Google Search Console və Bing Webmaster Tools-da domeni təsdiqləyin; sitemap təqdim edin. Canlı canonical/noindex və URL Inspection nəticələrini yoxlayın. Bu hesab əməliyyatları burada icra edilməyib.
2. Saytın CDN/WAF qaydalarının axtarış crawler-lərini bloklamadığını access log ilə yoxlayın. Image sitemap üçün ayrıca CDN domeninin Search Console tələblərini də qiymətləndirin.
3. Search Console-da uyğun sorğular üzrə impressions, clicks, CTR, seçilmiş canonical, indekslənmə və crawl statistikasını buraxılışdan əvvəlki dövrlə müqayisə edin. Orta mövqeyi yalnız eyni sorğu/cihaz/ölkə kəsimində müqayisə edin.
4. Real istifadəçi mobil məlumatında LCP, INP və CLS göstəricilərini ölçün. Lokal testlərdən PageSpeed 100 və ya Core Web Vitals keçidi nəticəsi çıxarılmır.
5. Ən çox tələb olan xidmətlər üçün real iş nümunələri, müəllifi və yoxlayan mütəxəssisi müəyyən olan bələdçilər, qiymətin hesablanma qaydası və aktual mənbələr hazırlayın. Mətnin dəqiqliyini xidmət sahəsinin mütəxəssisi yoxlasın; kütləvi təkrar rayon mətnləri yaratmayın.
6. Rayon üzrə faktiki xidmət əhatəsi lazımdırsa, onu ustanın açıq seçdiyi strukturlaşdırılmış əhatə sahələri kimi ayrıca məhsul funksiyası ilə toplayın. Hazırkı sərbəst `sheher` mətnini koordinat və ya təsdiqlənmiş xidmət radiusu kimi təqdim etməyin.
7. Həqiqi müştəri rəyləri üçün doğrulanmış iş/rəy axını yaradılmadan review və aggregateRating schema əlavə etməyin. Google Business Profile yalnız faktiki uyğun biznes üçün açılmalıdır; platformaya uydurma fiziki ünvan əlavə edilməməlidir.

## Rəsmi əsaslar və gözlənti

[Google AI features](https://developers.google.com/search/docs/appearance/ai-features) üçün ayrıca sehrli schema və ya AI mətn faylı tələb olunmur; əsas texniki SEO və faydalı, etibarlı məzmun vacibdir. `llms.txt` burada əlavə mənbə kataloqudur, reytinq və ya AI cavabında sitat zəmanəti deyil.

[Canonical qaydaları](https://developers.google.com/search/docs/crawling-indexing/consolidate-duplicate-urls), [structured data siyasəti](https://developers.google.com/search/docs/appearance/structured-data/sd-policies), [image sitemap](https://developers.google.com/search/docs/crawling-indexing/sitemaps/image-sitemaps) və [spam siyasəti](https://developers.google.com/search/docs/essentials/spam-policies) tətbiqin seçilmiş davranışlarını əsaslandırır. FAQ schema yalnız görünən sual/cavabı təsvir edir; xüsusi Google rich result vədi verilmir.

Birinci yer, indekslənmə müddəti və AI tövsiyəsi kodla zəmanət verilə bilən nəticələr deyil. Bu paket saytı daha aydın, ziddiyyətsiz və yoxlanıla bilən edir; qalan nəticə real məzmun, etibar, yayım və müşahidə məlumatından asılıdır.
