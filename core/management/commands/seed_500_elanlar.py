import random
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from core.models import Kategori, Elan, ElanShekil, Profil

PHONE_1 = '+994515888884'  # 051 588 88 84
PHONE_2 = '+994704919104'  # 070 491-91-04

AREAS = [
    'Bakı', 'Yasamal', 'Nəsimi', 'Nərimanov', 'Xətai', 'Nizami', 'Səbail',
    'Binəqədi', 'Suraxanı', 'Sabunçu', 'Xəzər', 'Abşeron', 'Xırdalan',
    'Masazır', 'Sumqayıt', 'Əhmədli', 'Həzi Aslanov', 'Qara Qarayev',
    'Neftçilər', 'Xalqlar Dostluğu', 'Koroğlu', 'Gənclik', '28 May',
    'Elmlər Akademiyası', 'İnşaatçılar', '20 Yanvar', 'Memar Əcəmi',
    'Azadlıq Prospekti', 'Dərnəgül', 'Avtovağzal', 'Badamdar', 'Bayıl',
    'Yeni Yasamal', 'Hövsan', 'Bakıxanov', 'Mərdəkan', 'Şüvəlan', 'Bilgəh',
    'Maştağa', 'Zabrat', 'Ramanı', 'Mehdiabad', 'Saray', 'Hökməli',
    'Lökbatan', 'Qaraçuxur', 'Günəşli', 'Bibiheybət', 'Müşfiqabad', 'Zığ',
    'Buzovna', 'Zirə', 'Türkan', 'Pirşağı', 'Kürdəxanı', 'Novxanı', 'Fatmayı',
    'Digah', 'Məhəmmədi', 'Binə', 'Qala', 'Şağan', 'Hövsan qəsəbəsi'
]

SERVICES_CONFIG = [
    {
        'key': 'kondisioner',
        'category_slug': 'kondisioner-ustasi',
        'count': 63,
        'titles': [
            'Kondisioner ustası — Təmir, montaj və quraşdırma ({area})',
            'Kondisioner təmiri və Freon qaz vurulması — Peşəkar xidmət ({area})',
            'Təcili Kondisioner ustası — Yuyulma, təmizlənmə və profilaktika ({area})',
            'Kondisioner motor və plata təmiri — Zəmanətli usta ({area})',
            'Kondisionerlərin sökülməsi, köçürülməsi və montajı ({area})',
            'İnverter kondisioner təmiri və diaqnostikası — {area}',
            'Kondisioner radiatorunun yuyulması və qaz dolumu ({area})',
            'Peşəkar kondisioner servisi və ehtiyat hissələri — {area}',
            'Kondisioner quraşdırılması və xüsusi dərmanla yuyulması ({area})',
            'Bütün markalı kondisionerlərin operativ təmiri ({area})',
            'Kondisioner kompressor dəyişimi və qaz sızmasının bərpası ({area})',
            'Kondisioner ustası — 24/7 Təcili çağırış və diaqnostika ({area})',
        ],
        'descriptions': [
            """Peşəkar Kondisioner ustası xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Bütün növ split sistem, inverter, kanal tipli, kolon tipli və multi-split kondisionerlərin yüksək keyfiyyətlə təmiri və quraşdırılması həyata keçirilir.

Görülən işlər:
✅ Kondisionerə keyfiyyətli Freon (R410A, R22, R32, R407) qazının vurulması və təzyiqin nizamlanması
✅ Qaz sızması yerlərinin aşkar edilməsi və lehimlənməsi
✅ Xüsusi antibakterial dərman və təzyiqli su aparatı ilə daxili və xarici blokun yuyulması
✅ Kondisioner filtrlərinin və radiatorunun dərindən təmizlənməsi (pis qoxuların aradan qaldırılması)
✅ Kompressor (motor) təmiri, kondensator və ventilyator dəyişdirilməsi
✅ Elektron idarəetmə lövhəsinin (plata / beyin) bərpası və proqramlaşdırılması
✅ 4 yollu klapan, termostat və sensorların dəyişdirilməsi
✅ Drenaj xəttinin açılması və su axıtma problemlərinin aradan qaldırılması
✅ Kondisionerlərin sökülməsi, başqa ünvana köçürülməsi və yenidən montajı

Xidmət etdiyimiz markalar:
Gree, Mitsubishi Electric, Mitsubishi Heavy, LG, Samsung, AUX, Midea, Bosch, Beko, Shivaki, Chigo, Hoffman, Toshiba, Panasonic, Daikin, General, Electrolux, Carrier, Vestel, Haier və s.

Üstünlüklərimiz:
- Orijinal ehtiyat hissələri və sertifikatlı materiallar
- 10 ildən artıq təcrübəli ustalar
- Görülən hər bir işə rəsmi yazılı zəmanət
- Günün istənilən vaxtı operativ çıxış

Açar sözlər: kondisioner ustasi {area}, kondisioner temiri baki, kondisioner qurasdirilmasi, kondisioner yuyulmasi, freon qaz vurulmasi r410 r22, kondisioner plata temiri, kondisioner motoru, inverter kondisioner servisi, ucuz kondisioner ustasi, tecili kondisioner temiri.""",

            """Kondisioneriniz soyutmur, qızdırmır, su axıdır və ya səs salır? Narahat olmayın! {area} ərazisində peşəkar kondisioner ustası xidməti ilə problemlərinizi ən qısa zamanda həll edirik.

Təqdim etdiyimiz xidmətlər:
🔹 Dəqiq diaqnostika və nasazlığın yerində aşkar edilməsi
🔹 Freon R410A, R32, R22 qaz dolumu və təzyiq yoxlanışı
🔹 Xüsusi avadanlıqla daxili və xarici blokun dərmanla təmizlənməsi
🔹 Plata (elektron modul) təmiri və sxemlərin bərpası
🔹 Kompressor, ventilyator motoru və kondensator dəyişimi
🔹 Kondisionerin peşəkar montajı və demontajı
🔹 Drenaj borusunun təmizlənməsi və su sızmasının ləğvi

Xidmət göstərilən brendlər:
Samsung, LG, Gree, AUX, Midea, Bosch, Beko, Mitsubishi, Toshiba, Panasonic, Electrolux, Shivaki və bütün digər istehsalçılar.

Niyə bizi seçməlisiniz?
- {area} və bütün Bakı qəsəbələrinə dərhal çıxış
- Münasib və şəffaf qiymətlər
- Keyfiyyətə 100% zəmanət
- Hər növ orijinal hissələr

Açar sözlər: kondisioner ustasi {area}, baki kondisioner temiri, freon qaz vurulmasi, kondisioner yuma xidmeti, kondisioner qurasdirma usta, split kondisioner temiri, zemanetli kondisioner ustasi.""",

            """{area} üzrə peşəkar və operativ kondisioner təmiri və montajı xidməti. İllərin təcrübəsinə malik ustalarımız istənilən mürəkkəblikdə olan nasazlıqları operativ şəkildə aradan qaldırır.

Əsas xidmət istiqamətlərimiz:
1. Kondisioner quraşdırılması, sökülməsi və yerinin dəyişdirilməsi
2. Freon R410 / R22 / R32 / R407 qazının vurulması
3. Təzyiqli yuma aparatı ilə kimyəvi təmizləmə və dezinfeksiya
4. Elektron plata (beyin) təmiri və detalların bərpası
5. Kompressor təmiri və dəyişdirilməsi
6. Sensor, drosel və ventilyator nasazlıqlarının aradan qaldırılması
7. Boru kəmərlərinin izolasiyası və sızma təmiri

Bütün Gree, LG, Samsung, AUX, Midea, Bosch, Beko, Mitsubishi və digər markalara tam zəmanət verilir. 
24/7 əlaqə saxlaya bilərsiniz.

Açar sözlər: kondisioner temiri {area}, kondisioner qaz vurulmasi, kondisioner ustasi baki, kondisioner yuyulmasi dermanla, inverter kondisioner ustasi, kondisioner montaj qiymeti, tecili kondisioner servisi."""
        ],
        'prices': [15, 20, 25, 30, 35, 40, 50, 60, None],
        'img_prefix': 'kondisioner',
        'img_count': 7
    },
    {
        'key': 'kombi',
        'category_slug': 'kombi-ustasi',
        'count': 63,
        'titles': [
            'Kombi ustası — Təmir, profilaktika və radiator yuyulması ({area})',
            'Kombi təmiri və plata bərpası — Zəmanətli usta xidməti ({area})',
            'Kombi və istilik sistemlərinin xüsusi aparatla yuyulması ({area})',
            'Təcili Kombi ustası — 24/7 Çıxış və operativ diaqnostika ({area})',
            'Kombi quraşdırılması, esenjor təmizliyi və servis — {area}',
            'Kombi su sızması və təzyiq probleminin həlli ({area})',
            'Kombi qaz klapanı və nasos təmiri — Orijinal hissələr ({area})',
            'Peşəkar Kombi təmiri xidməti — Bakı ({area})',
            'Kombi radiatorlarının dərmanla təmizlənməsi və qışa hazırlıq ({area})',
            'İmmergas, Baxi, Bosch, DemirDöküm kombi təmiri ({area})',
            'Kombi dövriyyə nasosu və 3 yollu klapan təmiri ({area})',
            'Kombi ustası — Evinizdə zəmanətli və etibarlı təmir ({area})',
        ],
        'descriptions': [
            """Peşəkar Kombi ustası xidməti {area} və ətraf ərazilərdə. Hər növ bir və iki esenjorlu kombilərin, istilik sistemlərinin təmiri, quraşdırılması və yuyulması.

Görülən işlər:
✅ Kombi və radiator sistemlərinin Almaniya istehsalı xüsusi aparat və kimyəvi dərmanla ərpdən təmizlənməsi
✅ Əsas və ikinci dərəcəli esenjorun yuyulması və dəyişdirilməsi
✅ Elektron idarəetmə platasının (beyin) təmiri və relelərin bərpası
✅ Sirkulyasiya nasosunun (Wilo, Grundfos) təmiri, bloklanmasının aradan qaldırılması və dəyişimi
✅ Üç yollu klapanın (3 yollu vana), motorik kartricin təmiri və dəyişdirilməsi
✅ Qaz klapanının tənzimlənməsi və nizamlanması
✅ Genişlənmə çəninin yoxlanılması və hava vurulması
✅ Kombidə su təzyiqinin düşməsi və ya qalxması probleminin tam həlli
✅ Su sızmalarının, damcılamaların aradan qaldırılması
✅ Baca (fan) motorunun təmizlənməsi və hava təzyiq sensorunun yoxlanması

Təmir etdiyimiz markalar:
İmmergas, Baxi, Bosch, DemirDöküm, Ariston, E.C.A, Viessmann, Beretta, Ferroli, Thermex, Baymak, Navien, Daewoo, Fondital, Termet, Vaillant, Protherm, Warmhaus və s.

Üstünlüklərimiz:
- Yerində operativ diaqnostika
- Orijinal zavod ehtiyat hissələri
- Rəsmi zəmanət
- Təcrübəli və məsuliyyətli ustalar

Açar sözlər: kombi ustasi {area}, kombi temiri baki, kombi yuyulmasi dermanla, radiatorlarin yuyulmasi, kombi plata temiri, kombi qurasdirilmasi, kombi tezyiq dusur, kombi isti su vermir, immergas kombi temiri, baxi kombi ustasi, zemanetli kombi servisi.""",

            """Kombiniz isti su vermir, radiatorlar qızmır, kombi səs edir və ya təzyiq daim düşür? {area} ərazisində təcrübəli kombi ustalarımız dərhal köməyinizə çatacaq!

Təklif etdiyimiz xidmətlər:
🔹 Kombinin bütün detallarının yerində dəqiq diaqnostikası
🔹 Xüsusi avadanlıq və turşusuz kimyəvi vasitələrlə radiator və kombi yuyulması
🔹 İdarəetmə platasının yüksək keyfiyyətlə təmiri
🔹 Nasos, qaz klapanı, 3 yollu vana və esenjor təmiri / dəyişimi
🔹 Təzyiq problemlərinin və su sızmalarının aradan qaldırılması
🔹 Yeni kombilərin və radiatorların peşəkar montajı

Xidmət göstərilən markalar:
Baxi, Immergas, Bosch, Demirdöküm, Ariston, E.C.A, Viessmann, Ferroli, Thermex və bütün digər modellər.

Zəmanətli və operativ xidmət üçün 24/7 əlaqə saxlaya bilərsiniz.

Açar sözlər: kombi ustasi {area}, kombi temiri, radiatorlarin xususi aparatla yuyulmasi, kombi plata ustasi, kombi su axidir, kombi sirkulyasiya nasosu, baki kombi temiri, tecili kombi ustasi.""",

            """{area} və Bakıətrafı qəsəbələrdə fəaliyyət göstərən peşəkar kombi servisi. Kombinizin uzunömürlü və qənaətcil işləməsi üçün ən keyfiyyətli təmir və profilaktika xidməti təklif edirik.

Görülən işlər:
1. Kombi və radiator xətlərinin xüsusi aparatla yuyulub təmizlənməsi (qaz sərfiyyatını 30% azaldır)
2. Elektron plata təmiri və mikroçiplərin dəyişdirilməsi
3. Dövriyyə nasosu və qaz reduktorunun təmiri
4. Təzyiq çəninin hava vurulması və membran yoxlanışı
5. Termostat və sensorların nizamlanması
6. Yanma kamerasının və injektorların təmizlənməsi

Bütün işlərə yazılı zəmanət verilir. Orijinal hissələrdən istifadə olunur.

Açar sözlər: kombi ustasi {area}, kombi yuyulmasi aparati, kombi temiri baki, kombi esenjor temiri, demirdokum kombi ustasi, ariston kombi temiri, baxi plata temiri, tecili kombi xidmeti."""
        ],
        'prices': [20, 25, 30, 35, 40, 45, 50, 60, None],
        'img_prefix': 'kombi',
        'img_count': 7
    },
    {
        'key': 'havalandirma',
        'category_slug': 'havalandirma-ustasi',
        'count': 63,
        'titles': [
            'Havalandırma ustası — Sistemlərin quraşdırılması və təmiri ({area})',
            'Restoran, kafe və obyektlər üçün havalandırma xidməti ({area})',
            'Havalandırma motoru təmiri və kanal çəkilişi — {area}',
            'Mətbəx zontikləri və manqal havalandırma sistemləri ({area})',
            'Havalandırma borularının təmizlənməsi və filtrlərin yuyulması ({area})',
            'Sənaye və anbar havalandırma sistemlərinin montajı ({area})',
            'Havalandırma layihələndirilməsi və səsboğucu quraşdırılması ({area})',
            'Ventilyasiya ustası — Peşəkar montaj və servis ({area})',
            'Obyektlər üçün kanal tipli və salyangoz motor quraşdırılması ({area})',
            'Dönərxana və kafe havalandırma zontiki ustası ({area})',
            'Havalandırma sistemlərinin təmiri və motor dəyişimi ({area})',
            'Peşəkar ventilyasiya və hava təmizləmə sistemləri ({area})',
        ],
        'descriptions': [
            """Peşəkar Havalandırma və Ventilyasiya ustası xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Restoranlar, kafelər, dönərxanalar, qəlyanxanalar, şadlıq sarayları, çörəkbişirmə sexləri, anbarlar, istehsalat sahələri, klinikalar, idman zalları, ofislər və fərdi evlər üçün tam havalandırma xidməti.

Görülən işlər:
✅ Havalandırma sistemlərinin layihələndirilməsi, hesablanması və peşəkar montajı
✅ Düzbucaqlı və spiralvari sinklənmiş boruların (hava kanallarının) çəkilməsi
✅ Paslanmaz poladdan (nerj) mətbəx zontiklərinin və manqal üstü kapotların quraşdırılması
✅ Salyangoz motor, kanal tipli ventilyatorlar, radial və aksial mühərriklərin montajı və təmiri
✅ Yağ tutucu filtrlərin, karbon və hepa filtrlərin quraşdırılması, təmizlənməsi
✅ Havalandırma kanallarının yağ, his və tozdan xüsusi kimyəvi üsulla təmizlənməsi
✅ Səsboğucu (qluşitel) quraşdırılması ilə səssiz işləmənin təmini
✅ Rekuperator (istilik bərpa) cihazlarının və hava tənzimləyici klapanların quraşdırılması
✅ Diffuzor, anemosat və ventilyasiya barmaqlıqlarının montajı

Üstünlüklərimiz:
- Yüksək çəkim gücü və optimal hava dövriyyəsinin hesablanması
- Standartlara tam uyğun quraşdırma və keyfiyyətli materiallar
- Görülən işlərə rəsmi zəmanət
- Texniki servis və profilaktik baxış

Açar sözlər: havalandirma ustasi {area}, ventilyasiya sistemleri qurasdirilmasi, restoran havalandirmasi baki, manqal havalandirmasi zontik, kanal tipli havalandirma motoru, salyangoz motor temiri, havalandirma borulari, havalandirma temizlenmesi, havalandirma layihe montaj.""",

            """{area} ərazisində hər növ ictimai-iaşə obyektləri və sənaye sahələri üçün etibarlı havalandırma xidməti. Güclü çəkim, təmiz hava və qoxusuz mühit təmin edirik!

Xidmətlərimiz:
🔹 Mətbəx, dönərxana, manqalxana və restoranlar üçün xüsusi zontiklərin hazırlanması və montajı
🔹 Havalandırma motorlarının (salyangoz, kanal tipli) təmiri, sarınması və yenilənməsi
🔹 Sinklənmiş polad kanalların və elastik boruların səliqəli çəkilişi
🔹 Kanalların yağ və çirkdən təmizlənməsi (yanğın təhlükəsizliyi üçün vacibdir)
🔹 Səs azaldıcı sistemlərin (qluşitel) quraşdırılması
🔹 Təmiz hava verən (pritok) və çirkli hava sovuran (vıtajka) sistemlərin balanslaşdırılması

İllərin təcrübəsi ilə obyektiniz üçün ən optimal və qənaətcil havalandırma həllini təklif edirik.

Açar sözlər: havalandirma ustasi {area}, donerxana havalandirmasi, restoran havalandirma zontiki, kafe ventilyasiya, havalandirma motoru temiri, nerj zontik qurasdirma, baki havalandirma servisi.""",

            """Havalandırma sisteminiz yaxşı çəkmir, səs-küy salır və ya məkanda yemək qoxusu qalır? {area} üzrə peşəkar havalandırma ustası xidmətimizlə probleminizi tez bir zamanda həll edirik.

Görülən işlər:
1. Mövcud havalandırma xətlərinin diaqnostikası və hava axınının tənzimlənməsi
2. Ventilyator motorlarının təmiri, yastıqların (podşipniklərin) dəyişdirilməsi
3. Yeni kanalların çəkilməsi və zontiklərin bərkidilməsi
4. Yağ filtrlərinin və hava kanallarının dərindən yuyulması
5. Rekuperator və filtrasiya bloklarının quraşdırılması

İstənilən miqyasda işləri dəqiqliklə və zəmanətlə icra edirik.

Açar sözlər: havalandirma temiri {area}, ventilyasiya ustasi baki, havalandirma sistemleri, aspirasiya sistemleri, havalandirma temizliyi, vıtajka temiri, manqal kapotu ustasi."""
        ],
        'prices': [30, 40, 50, 60, 70, 80, 100, None],
        'img_prefix': 'havalandirma',
        'img_count': 7
    },
    {
        'key': 'paltaryuyan',
        'category_slug': 'paltaryuyan-ustasi',
        'count': 63,
        'titles': [
            'Paltaryuyan ustası — Bütün markaların ünvanda təmiri ({area})',
            'Paltaryuyan maşın təmiri və baraban podşipnik dəyişimi ({area})',
            'Paltaryuyan plata (beyin) təmiri və proqramlaşdırma ({area})',
            'Təcili Paltaryuyan ustası — Su axıtma, sıxmama probleminin həlli ({area})',
            'Paltaryuyan nasos, ten və qapı kilidi təmiri — {area}',
            'Paltaryuyan maşınların diaqnostikası və orijinal ehtiyat hissələri ({area})',
            'Paltaryuyan silkələmə və səs probleminin aradan qaldırılması ({area})',
            'Paltaryuyan və qurutma maşını təmiri — Zəmanətli ({area})',
            'Samsung, LG, Bosch, Beko paltaryuyan təmiri ({area})',
            'Paltaryuyan su qızdırmır, su boşaltmır probleminin təmiri ({area})',
            'Paltaryuyan motor şotkası və remen dəyişdirilməsi ({area})',
            'Peşəkar paltaryuyan maşın ustası — Bakı ({area})',
        ],
        'descriptions': [
            """Peşəkar Paltaryuyan ustası xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Bütün növ avtomat və yarıavtomat paltaryuyan, həmçinin qurudan maşınların birbaşa evinizdə yüksək keyfiyyətlə təmiri.

Görülən işlər:
✅ Sıxma zamanı güclü səs, silkələmə və titrəmə problemlərinin həlli (baraban podşipniklərinin, salniklərin və amortizatorların dəyişdirilməsi)
✅ Suyun qızdırılmaması probleminin aradan qaldırılması (qızdırıcı element — TEN və temperatur sensorunun dəyişimi)
✅ Suyun boşaldılmaması və filtr tıxanması (drenaj nasosu / pompa təmiri və dəyişdirilməsi)
✅ Qapının açılmaması, bağlanmaması və ya xəta verməsi (qapı kilidi — zamok və mexanizmin təmiri)
✅ Elektron idarəetmə platasının (beyin / modul) təmiri, proqram təminatının yazılması və sıfırlanması
✅ Mühərrik (motor) təmiri, motor kömürlərinin (şotkaların) və qayışın (remenin) dəyişdirilməsi
✅ Su qəbul klapanının (ventel), presostatın (su səviyyə sensoru) dəyişdirilməsi
✅ Manjet rezinlərinin dəyişdirilməsi və su axıntıların aradan qaldırılması

Təmir etdiyimiz markalar:
Samsung, LG, Bosch, Beko, Indesit, Hotpoint-Ariston, Siemens, Candy, Vestel, Electrolux, Whirlpool, Gorenje, Zanussi, Midea, Haier, Toshiba və s.

Üstünlüklərimiz:
- Birbaşa ünvanda operativ təmir (maşını daşımağa ehtiyac yoxdur)
- Orijinal və zəmanətli ehtiyat hissələri
- Görülən işə yazılı zəmanət
- Münasib qiymətlər

Açar sözlər: paltaryuyan ustasi {area}, paltaryuyan temiri baki, paltaryuyan su bosaltmir pompa, paltaryuyan su qizdirmir ten, paltaryuyan podsipnik deyisimi, paltaryuyan plata temiri beyin, paltaryuyan cox ses edir, unvanda paltaryuyan temiri, samsung paltaryuyan temiri, lg paltaryuyan ustasi.""",

            """Paltaryuyan maşınınız işləmir, proqramı yarımçıq saxlayır, su axıdır və ya qapısı açılmır? {area} ərazisində təcrübəli ustalarımız evinizə gələrək problemi yerindəcə həll edir.

Xidmətlərimiz:
🔹 Dəqiq diaqnostika və nasazlığın operativ aşkarlanması
🔹 Baraban təmiri, podşipnik və amortizator yenilənməsi
🔹 Su boşaltma pompası və qızdırıcı ten dəyişimi
🔹 Elektron plata (beyin) bərpası və proqram xətalarının silinməsi
🔹 Qapı kilidi, manjet rezin və klapan dəyişimi
🔹 Motor və remen təmiri

Bütün işlərə zəmanət verilir. Əlaqə saxlayın, eyni gündə təmir edək!

Açar sözlər: paltaryuyan ustasi {area}, paltaryuyan masin temiri, paltaryuyan su axidir, bosch paltaryuyan temiri, beko paltaryuyan ustasi, paltaryuyan remen qirilib, paltaryuyan temiri unvanda baki.""",

            """{area} üzrə zəmanətli paltaryuyan maşın təmiri xidməti. Hər növ nasazlıq peşəkar ustalar tərəfindən orijinal detallarla aradan qaldırılır.

Görülən işlər:
1. Su qızdırmamaq, su boşaltmamaq və su götürməmək problemlərinin həlli
2. Baraban podşipniklərinin xüsusi preslə keyfiyyətli dəyişdirilməsi
3. Elektron lövhə və sensorların təmiri
4. Səs-küy, silkələnmə və yerindən oynama problemlərinin aradan qaldırılması
5. Qapı manjeti və şlanqların dəyişdirilməsi

Hər bir işimizə rəsmi zəmanət verilir.

Açar sözlər: paltaryuyan temiri {area}, paltaryuyan ustasi baki, paltaryuyan podsiplik temiri, avtomat paltaryuyan ustasi, indesit paltaryuyan temiri, ariston paltaryuyan ustasi, tecili paltaryuyan temiri."""
        ],
        'prices': [15, 20, 25, 30, 35, 40, 50, None],
        'img_prefix': 'paltaryuyan',
        'img_count': 7
    },
    {
        'key': 'qabyuyan',
        'category_slug': 'qabyuyan-ustasi',
        'count': 62,
        'titles': [
            'Qabyuyan ustası — Evdə operativ təmir və servis ({area})',
            'Qabyuyan maşın təmiri və orijinal hissələrin dəyişimi ({area})',
            'Qabyuyan su axıtma və qabları yumama probleminin təmiri ({area})',
            'Qabyuyan nasos, ten və plata təmiri — Peşəkar usta ({area})',
            'Təcili Qabyuyan ustası — Bakı ({area})',
            'Qabyuyan maşınların quraşdırılması və tam diaqnostikası ({area})',
            'Qabyuyan dövriyyə nasosu və filtr təmizlənməsi ({area})',
            'Qabyuyan maşın təmiri — Yazılı zəmanət ilə ({area})',
            'Bosch, Siemens, Beko, Samsung qabyuyan maşın təmiri ({area})',
            'Qabyuyan su qızdırmır, tablet əritmir probleminin təmiri ({area})',
            'Qabyuyan qapı yayları və rezinlərin dəyişdirilməsi ({area})',
            'Peşəkar qabyuyan maşın ustası — {area}',
        ],
        'descriptions': [
            """Peşəkar Qabyuyan ustası xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Bütün növ quraşdırılan (ankastre) və sərbəst dayanan qabyuyan maşınların birbaşa evinizdə operativ və zəmanətli təmiri.

Görülən işlər:
✅ Qabyuyan maşının suyu qızdırmaması, tabletin əriməməsi və soyuq su ilə yuması problemlərinin həlli (TEN və istilik sensoru dəyişimi)
✅ Qabların təmiz yuyulmaması, ləkəli qalması (sirkulyasiya dövriyyə nasosu, pərvanələr və farsunkaların təmizlənməsi / təmiri)
✅ Suyun boşaldılmaması və ya su axıtması (drenaj nasosu — pompa təmiri, filtrlərin təmizlənməsi)
✅ AquaStop təhlükəsizlik sisteminin xətalarının aradan qaldırılması
✅ Qapı prujinlərinin (yaylarının), troslarının və qapı rezinlərinin yenisi ilə əvəzlənməsi
✅ Elektron idarəetmə platasının (modul / beyin) bərpası və proqram xətalarının sıfırlanması
✅ Su qəbul klapanı və duz qabı sensorlarının dəyişdirilməsi
✅ Qabyuyan maşınların quraşdırılması, montajı və su-kanalizasiya xətlərinə qoşulması

Təmir etdiyimiz markalar:
Bosch, Siemens, Beko, Samsung, LG, Ariston, Indesit, Electrolux, Gorenje, Whirlpool, Miele, Vestel, Hansa, Zanussi və digərləri.

Üstünlüklərimiz:
- Birbaşa ünvanda sürətli təmir
- Orijinal hissələr və peşəkar alətlər
- Rəsmi zəmanət
- Sərfəli qiymətlər

Açar sözlər: qabyuyan ustasi {area}, qabyuyan temiri baki, qabyuyan masin temiri, qabyuyan su qizdirmir ten, qabyuyan yaxsi yumur, qabyuyan pompa temiri, qabyuyan plata temiri, bosch qabyuyan temiri, beko qabyuyan ustasi, zemanetli qabyuyan servisi.""",

            """Qabyuyanınız işə düşmür, su sızdırır, xəta kodu verir və ya qabları natəmiz çıxarır? {area} ərazisində peşəkar qabyuyan ustası ilə əlaqə saxlayın, operativ şəkildə həll edək.

Xidmətlər:
🔹 Yerində ətraflı diaqnostika
🔹 Sirkulyasiya və boşaltma nasoslarının təmiri
🔹 Qızdırıcı element (TEN) və termostat dəyişimi
🔹 Elektron beyin və sensorların təmiri
🔹 Qapı mexanizmi və rezinlərin yenilənməsi
🔹 Filtr və daxili sistemlərin ərpdən təmizlənməsi

Bütün markalara orijinal detallarla zəmanətli təmir təqdim edirik.

Açar sözlər: qabyuyan ustasi {area}, qabyuyan masin temiri baki, qabyuyan su axidir aquastop, qabyuyan tablet erimir, siemens qabyuyan ustasi, ariston qabyuyan temiri, unvanda qabyuyan temiri.""",

            """{area} və Bakı qəsəbələrində qabyuyan maşınların peşəkar təmiri və montajı. İllərin təcrübəsinə malik ustalarımız hər bir problemi keyfiyyətlə aradan qaldırır.

Görülən işlər:
1. Su qızdırmamaq və proqram donması xətalarının təmiri
2. Dövriyyə mühərrikinin və pompasının bərpası
3. Qapı trosları və yaylarının dəyişdirilməsi
4. Elektron plata təmiri və sxemlərin bərpası
5. Yeni qabyuyan maşınların quraşdırılması

İşimizə tam zəmanət veririk.

Açar sözlər: qabyuyan temiri {area}, qabyuyan ustasi baki, qabyuyan qurasdirilmasi, qabyuyan ehtiyat hisseleri, electrolux qabyuyan temiri, samsung qabyuyan ustasi, tecili qabyuyan servisi."""
        ],
        'prices': [20, 25, 30, 35, 40, 50, None],
        'img_prefix': 'qabyuyan',
        'img_count': 7
    },
    {
        'key': 'soyuducu',
        'category_slug': 'soyuducu-ustasi',
        'count': 62,
        'titles': [
            'Soyuducu ustası — Ünvanda təcili təmir və qaz vurulması ({area})',
            'No Frost soyuducu təmiri və kompressor dəyişimi ({area})',
            'Soyuducu soyutmur və buz bağlayır problemlərinin təmiri ({area})',
            'Soyuducu plata təmiri və freon qaz dolumu — {area}',
            'Təcili Soyuducu ustası — 24/7 Çıxış və diaqnostika ({area})',
            'İnverter soyuducu təmiri və motor dəyişdirilməsi ({area})',
            'Vitrin və sənaye soyuducularının təmiri — {area}',
            'Peşəkar Soyuducu servisi — Bütün modellər ({area})',
            'Samsung, LG, Bosch, Beko soyuducu təmiri ({area})',
            'Soyuducu alt hissəsi soyutmur probleminin aradan qaldırılması ({area})',
            'Soyuducu qapı rezinlərinin və termostatın dəyişdirilməsi ({area})',
            'Soyuducu motoru təmiri və vakuumla qaz doldurulması ({area})',
        ],
        'descriptions': [
            """Peşəkar Soyuducu ustası xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Bütün növ məişət soyuducularının, No Frost, De Frost, Side-by-Side, invertor modellərin, həmçinin vitrin və dondurucu soyuducuların birbaşa evinizdə və ya obyektinizdə təmiri.

Görülən işlər:
✅ Soyuducuya keyfiyyətli Freon (R134a, R600a, R404a, R12) qazının vurulması, qaz sızması yerlərinin tapılıb lehimlənməsi və sistemin vakuumlanması
✅ Kompressorun (motorun) dəyişdirilməsi və ya təmiri (inverter və adi kompressorlar)
✅ No Frost sistemində soyutmama, dondurucu işləyib alt hissənin soyutmaması və ya buz bağlama problemlərinin həlli (defrost ten, biometal datçik, qoruyucu termoqoruyucu, taymer və hava ventilyatorunun dəyişdirilməsi)
✅ Elektron idarəetmə lövhəsinin (plata / beyin / inverter blok) təmiri və bərpası
✅ Termostatın, başlanğıc relesinin və kondensatorun dəyişdirilməsi
✅ Qapı maqnit rezinlərinin dəyişdirilməsi və qapının kip bağlanmasının təmini
✅ Drenaj xəttinin təmizlənməsi (soyuducunun altına su axmasının qarşısının alınması)
✅ Vitrin soyuducuları, süd və ət soyuducularının təmiri və servisi

Təmir etdiyimiz markalar:
Samsung, LG, Bosch, Beko, Indesit, Liebherr, Hitachi, Sharp, Atlant, Biryusa, Vestel, Siemens, Toshiba, Electrolux, Snaige, Pozis, Ariston, Haier və s.

Üstünlüklərimiz:
- Yerində operativ diaqnostika və təmir
- Orijinal motor və ehtiyat hissələri
- Görülən hər bir işə yazılı zəmanət
- Münasib və şəffaf qiymətlər

Açar sözlər: soyuducu ustasi {area}, soyuducu temiri baki, no frost soyuducu temiri, soyuducu qaz vurulmasi freon r600a r134a, soyuducu kompressor deyisimi, soyuducu alt hisse soyutmur, soyuducu plata temiri, samsung soyuducu ustasi, lg soyuducu temiri, atlant soyuducu ustasi, tecili soyuducu ustasi.""",

            """Soyuducunuz yaxşı soyutmur, xarlanır, motoru sönmür və ya qəribə səslər çıxarır? {area} ərazisində təcrübəli soyuducu ustalarımız dərhal ünvanınıza gəlir!

Xidmətlər:
🔹 Dəqiq diaqnostika və sızma axtarışı
🔹 Freon R600a / R134a qaz doldurulması
🔹 Motor (kompressor) dəyişdirilməsi
🔹 No Frost defrost sisteminin təmiri (ten, sensor, ventilyator)
🔹 Elektron plata və inverter blok bərpası
🔹 Qapı rezini və termostat dəyişimi

Orijinal hissələr və 100% zəmanət.

Açar sözlər: soyuducu ustasi {area}, soyuducu temiri, nofrost soyuducu buz baglayir, soyuducu motoru ses edir, beko soyuducu ustasi, bosch soyuducu temiri, baki soyuducu ustasi, unvanda soyuducu temiri.""",

            """{area} və Bakı qəsəbələrində bütün növ soyuducuların etibarlı təmiri. Peşəkar ustalarımız tərəfindən ən mürəkkəb nasazlıqlar belə yerindəcə həll olunur.

Görülən işlər:
1. Qaz sızması aşkar edilməsi, lehimlənmə və qaz vurulması
2. Kompressor (motor) yenilənməsi
3. No Frost sistemlərinin tam sazlanması
4. Elektron idarəetmə modullarının təmiri
5. Vitrin və ticarət soyuducularına texniki baxış

Yazılı zəmanət təqdim edirik. 24/7 əlaqə saxlaya bilərsiniz.

Açar sözlər: soyuducu temiri {area}, soyuducu ustasi baki, freon qaz dolumu, soyuducu ehtiyat hisseleri, liebherr soyuducu temiri, hitachi soyuducu ustasi, tecili soyuducu servisi."""
        ],
        'prices': [20, 25, 30, 35, 40, 50, 60, None],
        'img_prefix': 'soyuducu',
        'img_count': 7
    },
    {
        'key': 'su_sizma',
        'category_slug': 'su-sizma',
        'count': 62,
        'titles': [
            'Su sızması təyini — Dağıtmadan xüsusi aparatla axtarış ({area})',
            'Termal kamera və akustik cihazla su sızması ustası ({area})',
            'Gizli su sızmasının nöqtəvi aşkarlanması və təmiri ({area})',
            'Kombi və isti su borularında su sızması tespiti — {area}',
            'Təcili Su sızma ustası — Söküb dağıtmadan dəqiq təyin ({area})',
            'Qonşuya su damcılaması və boru partlaması diaqnostikası ({area})',
            'Kafel və divar altı su borusu sızmasının aşkarlanması ({area})',
            'Peşəkar Su sızma xidməti — Bakı və Abşeron ({area})',
            'Su sızmasının 100% dəqiq aparatla təyini ({area})',
            'İsti döşəmə (isti pol) və kombi su qaçışının tapılması ({area})',
            'Akustik dinləmə və termal kamera ilə su sızması ustası ({area})',
            'Su borularının təmiri və sızma diaqnostikası ({area})',
        ],
        'descriptions': [
            """Peşəkar Su sızması təyini və Santexnik ustası xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Mənzillərdə, həyət evlərində, villalarda, ofis və obyektlərdə gizli su sızmalarının heç bir yeri söküb-dağıtmadan müasir elektron avadanlıqlarla 100% dəqiq nöqtəvi təyini və peşəkar təmiri.

İstifadə etdiyimiz müasir avadanlıqlar və görülən işlər:
✅ Almaniya və ABŞ istehsalı peşəkar Termal Kamera (İstilik kamerası) ilə isti su xətləri, kombi boruları və isti döşəmə (isti pol) sistemlərində sızma nöqtəsinin vizual aşkarlanması
✅ Yüksək həssaslıqlı Akustik Dinləmə Cihazı (Geofon) ilə soyuq su xətlərində və təzyiqli borularda gizli sızma səslərinin dəqiq koordinatının tapılması
✅ Rütubətölçən (nəmölçən) cihazlarla divar, döşəmə və tavanın nəm dərəcəsinin yoxlanılması
✅ Təzyiq testi (manometr və hidro-test nasosu) ilə boru kəmərlərində qəza və hava itkisinin diaqnostikası
✅ Endoskopik boru kamerası ilə görünməyən şaxta və xətlərin daxildən yoxlanılması
✅ Qonşunun tavanına su damcılaması səbəbinin dəqiq müəyyən edilməsi
✅ Kombidə su təzyiqinin hər gün düşməsi probleminin kökündən həlli
✅ Aşkarlanan nöqtənin minimal müdaxilə ilə səliqəli açılması və borunun etibarlı təmiri

Üstünlüklərimiz:
- Kafel, metlax və divarları boş yerə dağıtmadan nöqtəvi təyin
- Vaxta və təmir xərclərinə böyük qənaət
- 100% dəqiq nəticəyə zəmanət
- 24/7 operativ çıxış

Açar sözlər: su sizma ustasi {area}, su sizmasi teyini baki, akustik aparatla su sizmasi axtarisi, termal kamera su sizma, dagitmadan su sizmasi tapilmasi, gizli su borusu sizmasi, kombi tezyiq dusmesi su sizmasi, su sizintisi teyini, qonsuya su damir usta, santexnik su sizma.""",

            """Evinizdə su sızır, divarlar nəm çəkir, kombinin barı daim düşür və ya su sayğacı öz-özünə fırlanır? {area} ərazisində xüsusi aparatlarla təchiz olunmuş ustalarımız dağıtmadan dərhal təyin edir!

Xidmətlər:
🔹 Termal kamera ilə isti su və kombi borularının yoxlanışı
🔹 Akustik dinləmə aparatı ilə soyuq su borularında gizli qəzanın tapılması
🔹 Təzyiq testi ilə sızmanın hansı xətdə olmasının dəqiqləşdirilməsi
🔹 Nöqtəvi təmir — yalnız sızan yer açılır və boru bərpa olunur
🔹 Santexnika xidmətləri və kran/boru dəyişimi

100% dəqiqlik və zəmanət.

Açar sözlər: su sizma ustasi {area}, su sizintisi tapilmasi baki, termal kamera ile sizma axtarisi, su borusu partlayib, qirmadan su sizmasi teyini, baki santexnik su sizma.""",

            """{area} və bütün Bakı üzrə qırmadan və dağıtmadan su sızmalarının aparatla dəqiq təyini. Ən son model termal kamera və akustik cihazlarla sızma nöqtəsini 1 sm dəqiqliklə tapırıq.

Görülən işlər:
1. Kombi və radiator borularında təzyiq itkisinin səbəbinin tapılması
2. Döşəməaltı (isti pol) xətlərində gizli deşiklərin təyini
3. Divar içi və kafel altı boru qəzalarının aşkarlanması
4. Nöqtəvi təmir və boru lehimlənməsi
5. Qonşuya su axması problemlərinin aradan qaldırılması

Bizimlə əlaqə saxlayın, evinizi dağıtmadan problemi həll edək!

Açar sözlər: su sizma teyini {area}, su sizmasi ustasi baki, isti pol su sizmasi, akustik su axtarma cihazi, su sizinti servisi, pesekar santexnik usta."""
        ],
        'prices': [30, 40, 50, 60, 70, 80, None],
        'img_prefix': 'su_sizma',
        'img_count': 7
    },
    {
        'key': 'kanalizasiya',
        'category_slug': 'kanalizasiya-ustasi',
        'count': 62,
        'titles': [
            'Kanalizasiya açılması — Xüsusi elektrotros və aparatla ({area})',
            'Tıxanmış kanalizasiya xətlərinin və boruların açılması ({area})',
            'Kanalizasiya ustası — Hidrodinamik yuma və təmizləmə ({area})',
            'Təcili Kanalizasiya xidməti 24/7 — Trap, unitaz, moyka açılması ({area})',
            'Mətbəx və vanna otağı kanalizasiya tıxanmasının aradan qaldırılması ({area})',
            'Kanalizasiya quyularının (lyuk) təmizlənməsi və boru yuyulması — {area}',
            'Kanalizasiya borularının aparatla açılması — Qırmadan və dağıtmadan ({area})',
            'Kanalizasiya təmizləmə xidməti — Zəmanətli usta ({area})',
            'Restoran və iaşə obyektlərində yağlı kanalizasiya xətlərinin yuyulması ({area})',
            'Elektrikli tros aparatı ilə kanalizasiya açılması ({area})',
            'Kanalizasiya stoyak və həyət xətlərinin təmizlənməsi ({area})',
            'Peşəkar Kanalizasiya ustası — Bakı ({area})',
        ],
        'descriptions': [
            """Peşəkar Kanalizasiya açılması və təmizlənməsi xidməti {area} və bütün Bakı, Abşeron ərazisində. 
Bina mənzillərində, fərdi həyət evlərində, restoran, kafe, otel, sex və sənaye obyektlərində hər növ tıxanmış kanalizasiya borularının xüsusi avadanlıqlarla qırmadan və dağıtmadan 100% açılması.

İstifadə olunan texnologiyalar və görülən işlər:
✅ Almaniya istehsalı olan peşəkar fırlanan Elektrotros aparatı (Ridgid, Rems) ilə daşlaşmış ərpin, kənar əşyaların, saç və parça tıxaclarının borudan təmizlənməsi
✅ Yüksək təzyiqli su ilə Hidrodinamik Yuma (Hidrojetting) — borunun daxili divarındakı bütün bərkimiş yağ, gil və qum təbəqəsinin tamamilə yuyulub təmizlənməsi
✅ Mətbəx trapının, vanna və duş kabina trapının tıxanmasının açılması
✅ Unitaz, moykadodir, əlüzyuyan və pisuarların təcili açılması
✅ Əsas kanalizasiya dirəklərinin (vertikal stoyak xətlərinin) təmizlənməsi
✅ Həyət kanalizasiya xətlərinin və quyuların (lyukların) təmizlənməsi
✅ Yağ tutucu çənlərin (jirolovitel) təmizlənməsi və yuyulması
✅ Kanalizasiyadan gələn kəskin pis qoxuların aradan qaldırılması
✅ Boruların kamera ilə (video diaqnostika) daxildən yoxlanılması

Üstünlüklərimiz:
- Dağıtmadan, söküntüsüz və tam təmiz iş
- 24/7 təcili qəza xidməti (gecə-gündüz zənglər qəbul olunur)
- Ən çətin tıxanmaların operativ həlli
- Zəmanətli və keyfiyyətli xidmət

Açar sözlər: kanalizasiya ustasi {area}, kanalizasiya acilmasi baki, tixanmis kanalizasiya borusu acilmasi, aparatla kanalizasiya temizleme, trosla kanalizasiya acilmasi, hidrodinamik kanalizasiya yuma, trap acilmasi, unitaz acilmasi, 24 saat kanalizasiya ustasi, baki kanalizasiya temizleme xidmeti.""",

            """Kanalizasiya borunuz tutulub, su geri qayıdır və ya pis qoxu gəlir? {area} ərazisində 24/7 fəaliyyət göstərən peşəkar kanalizasiya xidmətimizə müraciət edin!

Xidmətlər:
🔹 Elektrikli xüsusi tros aparatı ilə boruların təmizlənməsi
🔹 Trap, unitaz, çanaq və vanna tıxanmalarının dərhal açılması
🔹 Təzyiqli su ilə boru daxilindəki yağların yuyulması
🔹 Quyuların və həyət xətlərinin təmizlənməsi
🔹 Boru qırılmalarının və nasazlıqların təmiri

Heç bir yeri dağıtmadan səliqəli və zəmanətlə iş təhvil verilir.

Açar sözlər: kanalizasiya ustasi {area}, kanalizasiya borusu tutulub, elektrotros kanalizasiya, trap temizleme, unitaz tutulmasi acilmasi, baki kanalizasiya ustasi, tecili kanalizasiya acan.""",

            """{area} və bütün Bakı qəsəbələrində kanalizasiya xətlərinin aparatla açılması və yuyulması. 

Görülən işlər:
1. Mətbəx və vanna otağı tıxanmalarının sürətli açılması
2. Hidrodinamik üsulla boruların 100% yuyulması
3. Restoran və obyektlərin yağlı xətlərinin təmizlənməsi
4. Lyuk və quyu təmizləmə xidməti
5. Pis qoxunun kökündən həlli

24 saat xidmətinizdəyik. Zəmanətli iş.

Açar sözlər: kanalizasiya acilmasi {area}, kanalizasiya temizleme baki, kanalizasiya aparati, restoran kanalizasiya yuma, unitaz acan usta, zemanetli kanalizasiya xidmeti."""
        ],
        'prices': [20, 25, 30, 35, 40, 50, 60, None],
        'img_prefix': 'kanalizasiya',
        'img_count': 7
    },
]


class Command(BaseCommand):
    help = '500 elan yaradır (kondisioner, kombi, havalandırma, paltaryuyan, qabyuyan, soyuducu, su sızma, kanalizasiya).'

    def handle(self, *args, **options):
        # 1. Check users
        users = list(User.objects.filter(is_active=True))
        if not users:
            self.stdout.write(self.style.ERROR('Aktiv istifadəçi tapılmadı!'))
            return

        self.stdout.write(f'Mövcud aktiv istifadəçilər: {len(users)}')

        # Ensure all profiles have ad / soyad
        for u in users:
            p, _ = Profil.objects.get_or_create(istifadeci=u)
            if not p.ad:
                if u.first_name:
                    p.ad = u.first_name
                    p.soyad = u.last_name or 'Usta'
                else:
                    p.ad = u.username.capitalize()
                    p.soyad = 'Usta'
                p.save()

        # 2. Check categories
        categories_map = {}
        for cfg in SERVICES_CONFIG:
            try:
                cat = Kategori.objects.get(slug=cfg['category_slug'])
                categories_map[cfg['key']] = cat
            except Kategori.DoesNotExist:
                self.stdout.write(self.style.ERROR(f"Kateqoriya tapılmadı: {cfg['category_slug']}"))
                return

        # 3. Prepare list of 500 items to create
        all_items = []
        for cfg in SERVICES_CONFIG:
            count = cfg['count']
            for _ in range(count):
                all_items.append(cfg)

        self.stdout.write(f'Yaradılacaq cəmi elan sayı: {len(all_items)}')
        assert len(all_items) == 500, f'Expected 500 items, got {len(all_items)}'

        # Shuffle deterministically to mix services nicely while preserving counts
        random.seed(42)
        random.shuffle(all_items)

        # Phone distribution: exactly 250 with PHONE_1, 250 with PHONE_2
        phones = [PHONE_1] * 250 + [PHONE_2] * 250
        random.shuffle(phones)

        created_count = 0
        phone_1_count = 0
        phone_2_count = 0
        shekil_count = 0

        now = timezone.now()

        for idx, (cfg, phone) in enumerate(zip(all_items, phones)):
            cat = categories_map[cfg['key']]
            user = users[idx % len(users)]
            area = AREAS[idx % len(AREAS)]

            title_tpl = random.choice(cfg['titles'])
            title = title_tpl.format(area=area)
            if len(title) > 190:
                title = title[:190]

            desc_tpl = random.choice(cfg['descriptions'])
            desc = desc_tpl.format(area=area)

            price = random.choice(cfg['prices'])
            img_idx = (idx % cfg['img_count']) + 1
            img_path = f"elanlar/{cfg['img_prefix']}_{img_idx}.jpg"

            # Create Elan
            elan = Elan.objects.create(
                istifadeci=user,
                kategori=cat,
                bashliq=title,
                acaqlama=desc,
                qiymet=price,
                sheher='Bakı',
                telefon=phone,
                status='aktiv',
                vip_status='normal',
                bitis_tarixi=now + timedelta(days=365),
                baxish_sayi=random.randint(15, 250),
            )

            # Create main photo
            ElanShekil.objects.create(
                elan=elan,
                shekil=img_path,
                esas=True
            )
            shekil_count += 1

            # For some listings, attach a 2nd photo
            if idx % 3 == 0:
                img_idx_2 = ((img_idx) % cfg['img_count']) + 1
                img_path_2 = f"elanlar/{cfg['img_prefix']}_{img_idx_2}.jpg"
                ElanShekil.objects.create(
                    elan=elan,
                    shekil=img_path_2,
                    esas=False
                )
                shekil_count += 1

            created_count += 1
            if phone == PHONE_1:
                phone_1_count += 1
            else:
                phone_2_count += 1

        self.stdout.write(self.style.SUCCESS(
            f'MÜVƏFFƏQİYYƏTLƏ BAŞA ÇATDI!\n'
            f'Cəmi yaradılan elan: {created_count}\n'
            f'{PHONE_1} (051 588 88 84) sayı: {phone_1_count}\n'
            f'{PHONE_2} (070 491-91-04) sayı: {phone_2_count}\n'
            f'Əlavə edilən şəkillər: {shekil_count}\n'
        ))
