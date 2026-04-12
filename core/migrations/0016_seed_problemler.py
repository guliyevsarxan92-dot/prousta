from django.db import migrations


def seed_problemler(apps, schema_editor):
    Problem = apps.get_model('core', 'Problem')
    Kategori = apps.get_model('core', 'Kategori')

    def get_kat(slug):
        try:
            return Kategori.objects.get(slug=slug)
        except Kategori.DoesNotExist:
            return None

    problemler = [
        # ===== KOMBİ =====
        {
            'bashliq': 'Kombi yanmır — səbəbləri və həll yolu',
            'slug': 'kombi-yanmir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Kombi Yanmır — Səbəbləri və Həll Yolu | Prousta.az',
            'seo_description': 'Kombi niyə yanmır? Ən çox rast gəlinən 7 səbəb və evdə edə biləcəyiniz yoxlamalar. Peşəkar kombi ustası məsləhəti.',
            'metn': """
<h2>Kombi niyə yanmır?</h2>
<p>Qış mövsümündə kombinin yanmaması ən çox rast gəlinən problemlərdən biridir. Səbəblər sadə ola bildiyi kimi, ciddi texniki nasazlıq da ola bilər. Aşağıda ən geniş yayılmış səbəbləri və evdə edə biləcəyiniz ilkin yoxlamaları sıralayırıq.</p>

<h2>Ən çox rast gəlinən səbəblər</h2>
<ol>
<li><strong>Qaz təchizatı kəsilib</strong> — Əvvəlcə mətbəx sobasını yoxlayın. Əgər soba da yanmırsa, qaz kəsilmiş ola bilər. Qaz sayğacının kranını yoxlayın.</li>
<li><strong>Alov elektrodu çirkli və ya xarabdır</strong> — İonizasiya elektrodu qurumla örtülürsə, kombi alovu algılamır və təhlükəsizlik üçün sönür. Elektrod təmizlənməli və ya dəyişdirilməlidir.</li>
<li><strong>Fan (ventilyator) işləmir</strong> — Kombi yanmadan əvvəl fan işə düşməlidir. Fan xarabdırsa, kombi yanmağa başlamayacaq. Kombini yandıranda fan səsi gəlmirsə, bu səbəb ola bilər.</li>
<li><strong>Təzyiq düşüb</strong> — Manometrə baxın. Əgər 1 bar-dan aşağıdırsa, kombi yanmaya bilər. Dolum kranından yavaşca su əlavə edib 1.2–1.5 bar arasına gətirin.</li>
<li><strong>Baca tıxanıb</strong> — Xüsusilə hermetik (turbo) kombilərdə baca tıxanması və ya donması kombini bloklayır. Bacanı yoxlayın.</li>
<li><strong>Plata xarab olub</strong> — Elektron idarəetmə platası xarabdırsa, kombi heç bir əmrə reaksiya vermir. Bu halda mütləq peşəkar usta lazımdır.</li>
<li><strong>Elektrik problemi</strong> — Gərginlik dalğalanması platanı zədələyə bilər. Kombini stabilizator vasitəsilə qoşmaq tövsiyə olunur.</li>
</ol>

<h2>Evdə edə biləcəyiniz yoxlamalar</h2>
<ul>
<li>Qaz kranının açıq olduğunu yoxlayın</li>
<li>Manometrdəki təzyiqi yoxlayın (1–1.5 bar olmalıdır)</li>
<li>Kombini söndürüb 30 saniyə gözləyin, yenidən yandırın (reset)</li>
<li>Ekranda xəta kodu varsa, qeyd edin — usta üçün faydalı olacaq</li>
<li>Elektrik kabelinin qoşulu olduğunu yoxlayın</li>
</ul>

<blockquote>Əgər yuxarıdakı addımlardan sonra da kombi yanmırsa, özünüz müdaxilə etməyin. Qaz cihazı ilə işləmək təhlükəli ola bilər — peşəkar kombi ustası çağırın.</blockquote>
"""
        },
        {
            'bashliq': 'Kombidən su axır — nə etməli?',
            'slug': 'kombiden-su-axir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Kombidən Su Axır — Səbəbləri və Təmir | Prousta.az',
            'seo_description': 'Kombidən su damcılayır və ya axır? Su sızıntısının 5 əsas səbəbi və təcili həll yolları. Bakıda kombi ustası çağırın.',
            'metn': """
<h2>Kombidən su sızması — ciddi problemi göstərir</h2>
<p>Kombinin altından, birləşmə yerlərindən və ya təhlükəsizlik klapanından su axması nadir problem deyil. Kiçik bir damcı belə, zamanla ciddi nəticələrə gətirib çıxara bilər — platanın yanması, döşəmənin zədələnməsi və su itkisi.</p>

<h2>Su sızıntısının əsas səbəbləri</h2>
<ol>
<li><strong>Təzyiq çoxdur</strong> — Sistem təzyiqi 2 bar-dan yuxarıdırsa, təhlükəsizlik klapanı açılıb su buraxır. Bu normal müdafiə mexanizmidir. Dolum kranını bağlayın və təzyiqi 1.2–1.5 bara endirin.</li>
<li><strong>Genişlənmə bakı xarab olub</strong> — Genişlənmə bakının membranı yırtılıbsa, sistem təzyiqi dayanmaz və klapandan su axar. Bak dəyişdirilməlidir.</li>
<li><strong>İstilik dəyişdiricisi (dəmir) deşilib</strong> — Əhəng yığılması və korroziya nəticəsində istilik dəyişdiricisində mikro deşiklər yaranır. Su damcılayır. Dəyişdirmək lazımdır.</li>
<li><strong>Birləşmə yerləri boşalıb</strong> — Zamanla fitinqlər, orinqlər köhnəlir. Sıxmaq və ya orinqi dəyişmək kifayətdir.</li>
<li><strong>3-yollu klapan sızır</strong> — İstilik və isti su rejimi arasında keçid edən klapanın rezini köhnəldikdə su sızır.</li>
</ol>

<h2>Təcili addımlar</h2>
<ul>
<li>Kombinin altına qab qoyun ki, su döşəməyə zərər verməsin</li>
<li>Dolum kranının bağlı olduğunu yoxlayın</li>
<li>Əgər çox su axırsa — kombini söndürün və qaz kranını bağlayın</li>
<li>Mümkünsə sızıntının yerini fotoşəkil çəkin — usta üçün faydalıdır</li>
</ul>

<blockquote>Kombidən su axması zamanla platanı zədələyə bilər ki, bu da ən bahalı təmirdir. Gecikdirməyin — dərhal peşəkar usta çağırın.</blockquote>
"""
        },
        {
            'bashliq': 'Kombi radiatorları qızdırmır — səbəblər',
            'slug': 'kombi-radiatorlari-qizdirmir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Kombi Radiatorları Qızdırmır — Həll Yolu | Prousta.az',
            'seo_description': 'Kombi işləyir amma radiatorlar soyuqdur? Hava yığılması, nasos xarabı, klapan problemi — səbəblər və həllər.',
            'metn': """
<h2>Kombi işləyir, radiatorlar soyuqdur — nə baş verir?</h2>
<p>Kombinin işləməsinə baxmayaraq radiatorların qızmaması və ya bəzi radiatorların isti, bəzilərinin soyuq qalması çox yayılmış problemdir. Bir neçə fərqli səbəbi ola bilər.</p>

<h2>Əsas səbəblər</h2>
<ol>
<li><strong>Radiatorlarda hava yığılıb</strong> — Ən çox rast gəlinən səbəb. Radiatorun üstündəki hava klapanını (blid) açaraq havranı buraxın. Su gələndə bağlayın.</li>
<li><strong>Sirkulyasiya nasosu işləmir</strong> — Nasos suyu sistemdə gəzdirmir. Nasosun işlədiyini səsindən anlaya bilərsiniz. Səs gəlmirsə, nasos xarabdır.</li>
<li><strong>3-yollu klapan isti su rejimində qalıb</strong> — Bu klapan xarabdırsa, kombi yalnız isti su verir, istilik sisteminə su göndərmir.</li>
<li><strong>Filtr tıxanıb</strong> — Sistemdəki çirkli su filtri tıxayıb su axınını azaldır. Filtr təmizlənməlidir.</li>
<li><strong>Termostat düzgün işləmir</strong> — Otaq termostatsı xarabdırsa, kombiyə istilik tələbi göndərmir.</li>
<li><strong>Sistem balanslanmayıb</strong> — Bəzi radiatorlar çox isti, bəziləri soyuqdursa, radiator klapanları ilə balanslanma lazımdır.</li>
</ol>

<h2>Özünüz edə biləcəyiniz</h2>
<ul>
<li>Hər radiatorun hava klapanından havranı buraxın</li>
<li>Manometrdə təzyiqi yoxlayın — 1.2 bar olmalıdır</li>
<li>Kombini istilik rejiminə keçirdiyinizdən əmin olun</li>
<li>Termostatın temperaturunu yuxarı qaldırın</li>
</ul>

<blockquote>Nasos və ya 3-yollu klapan problemi varsa, təmir üçün peşəkar usta lazımdır. Özünüz dəyişdirməyə cəhd etməyin — sistemə hava girə bilər.</blockquote>
"""
        },
        {
            'bashliq': 'Kombi xəta kodu verir — nə etməli?',
            'slug': 'kombi-xeta-kodu',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Kombi Xəta Kodu Verir — Nə Etməli? | Prousta.az',
            'seo_description': 'Kombi ekranında xəta kodu yanır? Ən çox rast gəlinən xəta kodları, mənası və həll yolları.',
            'metn': """
<h2>Kombi ekranında xəta kodu nə deməkdir?</h2>
<p>Müasir kombilərdə nasazlıq baş verdikdə ekranda xəta kodu görünür. Bu kodlar problemi tez müəyyən etməyə kömək edir. Hər markanın öz kod sistemi var, lakin bəzi xətalar universaldır.</p>

<h2>Ən çox rast gəlinən xəta kodları</h2>
<table>
<tr><th>Xəta</th><th>Mənası</th><th>Həll</th></tr>
<tr><td><strong>E01 / F1</strong></td><td>Alov algılanmır — kombi yanmır</td><td>Qaz kranını, elektrodu, bacanı yoxlayın</td></tr>
<tr><td><strong>E02 / F2</strong></td><td>Həddən artıq qızmaq</td><td>Nasosu, filtri, su təzyiqini yoxlayın</td></tr>
<tr><td><strong>E03 / F3</strong></td><td>Baca/fan problemi</td><td>Bacanın tıxanmadığını yoxlayın</td></tr>
<tr><td><strong>E10 / F22</strong></td><td>Su təzyiqi aşağıdır</td><td>Dolum kranından su əlavə edin</td></tr>
<tr><td><strong>E25 / F20</strong></td><td>NTC sensor xətası — temperatur ölçülmür</td><td>Sensor dəyişdirilməlidir</td></tr>
<tr><td><strong>E35</strong></td><td>Yalançı alov — parazit cərəyan</td><td>Torpaqlanmanı yoxlayın</td></tr>
</table>

<h2>Xəta kodu aldıqda nə etməli?</h2>
<ul>
<li>Xəta kodunu qeyd edin (şəkil çəkin)</li>
<li>Kombini söndürüb 30 saniyə gözləyin, yenidən yandırın (reset)</li>
<li>Eyni xəta təkrarlanırsa, peşəkar usta çağırın</li>
<li>Kombinin markası və modelini ustaya bildirin — daha sürətli diaqnoz qoyulacaq</li>
</ul>

<blockquote>Xəta kodlarını dəfələrlə reset etmək problemi həll etmir, əksinə platanı zədələyə bilər. 2-3 dəfə reset etdikdən sonra usta çağırmaq doğru qərardır.</blockquote>
"""
        },
        # ===== BOYLER =====
        {
            'bashliq': 'Boyler su qızdırmır — səbəbləri',
            'slug': 'boyler-su-qizdirmir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Boyler Su Qızdırmır — Səbəbləri və Həlli | Prousta.az',
            'seo_description': 'Boyler su qızdırmır? TEN yanıb, termostat xarab, əhəng yığılıb — ən çox rast gəlinən səbəblər və həll yolları.',
            'metn': """
<h2>Boyler niyə su qızdırmır?</h2>
<p>Elektrikli boyler (su qızdırıcı) gündəlik həyatda ən çox istifadə olunan cihazlardan biridir. Boylerin su qızdırmamasının bir neçə səbəbi ola bilər — bəziləri sadə, bəziləri isə peşəkar müdaxilə tələb edir.</p>

<h2>Əsas səbəblər</h2>
<ol>
<li><strong>TEN (qızdırıcı element) yanıb</strong> — Ən çox rast gəlinən səbəb. TEN əhəng yığılması nəticəsində həddən artıq qızır və yanır. Dəyişdirilməlidir.</li>
<li><strong>Termostat xarab olub</strong> — Termostat temperaturu idarə edir. Xarabdırsa, boyler qızdırma əmri almır. Dəyişdirilməlidir.</li>
<li><strong>Əhəng (kireç) yığılıb</strong> — Bakıda su çox sərtdir. 1-2 ildə bir boyler təmizlənməzsə, əhəng TEN-i örtür, qızdırma effektivliyi aşağı düşür və nəhayət TEN yanır.</li>
<li><strong>Anod çubuq bitib</strong> — Maqnezium anod çubuq tankı korroziyadan qoruyur. Bitdikdə tank daxildən paslanır. Hər 1-2 ildə dəyişdirilməlidir.</li>
<li><strong>Elektrik problemi</strong> — Avtomat açılıb, kabel zədələnib, rozetka xarabdır. Elektrik panelini yoxlayın.</li>
</ol>

<h2>Boylerin ömrünü uzatmaq üçün</h2>
<ul>
<li>İldə 1 dəfə əhəng təmizliyi etdirin</li>
<li>Hər 1-2 ildə anod çubuğu dəyişdirin</li>
<li>Temperaturu 60°C-dən yuxarı qoymayın — əhəng daha sürətli yığılır</li>
<li>Su filtrı quraşdırın — sərt su problemini azaldır</li>
</ul>

<blockquote>Boylerin təmiri zamanı mütləq elektrik və su xəttini söndürün. Elektrik və su birlikdə təhlükəlidir — peşəkar usta çağırmaq daha təhlükəsizdir.</blockquote>
"""
        },
        {
            'bashliq': 'Boyler su sızdırır — təcili həll',
            'slug': 'boyler-su-sizdirir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Boyler Su Sızdırır — Səbəb və Təcili Həll | Prousta.az',
            'seo_description': 'Boylerdən su axır? Tank deşilib, klapan sızır, birləşmə boşalıb — səbəblər və ilk yardım addımları.',
            'metn': """
<h2>Boylerdən su axması — nə etməli?</h2>
<p>Boylerdan su sızması təcili müdaxilə tələb edən problemdir. Su elektrik hissələrinə dəyərsə, qısa qapanma və hətta yanğın riski var.</p>

<h2>Su sızıntısının səbəbləri</h2>
<ol>
<li><strong>Tank daxildən paslanıb (deşilib)</strong> — Anod çubuq vaxtında dəyişdirilməyibsə, tank korroziyaya uğrayır. Bu halda boyler dəyişdirilməlidir — təmir mümkün deyil.</li>
<li><strong>Təhlükəsizlik klapanından su damcılayır</strong> — Qızdırma zamanı az miqdarda su damcılaması normaldır. Amma çox axırsa, klapan dəyişdirilməlidir.</li>
<li><strong>Birləşmə boruları boşalıb</strong> — Giriş-çıxış fitinqləri zamanla boşalır. Sıxmaq və ya teflon lent vurmaq kifayətdir.</li>
<li><strong>Flanş orinqi köhnəlib</strong> — TEN-in bağlandığı flanş hissəsinin rezin orinqi köhnələndə su sızır. Orinq dəyişdirilməlidir.</li>
</ol>

<h2>Təcili addımlar</h2>
<ul>
<li>Dərhal elektrik avtomatını söndürün</li>
<li>Su giriş kranını bağlayın</li>
<li>Sızıntının yerini müəyyən edin və fotoşəkil çəkin</li>
<li>Boylerin altına qab və ya dəsmal qoyun</li>
<li>Peşəkar usta çağırın</li>
</ul>

<blockquote>Paslanmış tankı təmir etmək mümkün deyil. Əgər tank deşilibsə, boyler dəyişdirilməlidir. Yeni boyler alarkən anod çubuğu vaxtında dəyişdirmək yadınızda olsun.</blockquote>
"""
        },
        # ===== SANTEXNİK =====
        {
            'bashliq': 'Kran su buraxır — damcılayan kran təmiri',
            'slug': 'kran-su-buraxir',
            'kategori_slug': 'santexnik',
            'seo_title': 'Kran Su Buraxır — Damcılayan Kran Təmiri | Prousta.az',
            'seo_description': 'Kran bağlı olsa da su damcılayır? Kartric, orinq, klapan — səbəblər və ev şəraitində həll yolları.',
            'metn': """
<h2>Damcılayan kran — kiçik görünür, böyük problem yaradır</h2>
<p>Damcılayan kran ilk baxışda ciddi görünməsə də, ayda 1000 litrə qədər su itkisinə səbəb ola bilər. Həm su hesabını artırır, həm də evaya tıxanma və pas yaradır.</p>

<h2>Kran niyə damcılayır?</h2>
<ol>
<li><strong>Kartric (kartuş) köhnəlib</strong> — Tək qollu qarışdırıcılarda keramik kartric zamanla aşınır. Dəyişdirilməsi asandır və ucuzdur.</li>
<li><strong>Orinqlər (rezinlər) quruub</strong> — İki qollu kranların içindəki rezin orinqlər zamanla bərkiyir və sızdırır. Orinq dəyişdirilməlidir.</li>
<li><strong>Klapan yuvası zədələnib</strong> — Orinq dəyişdikdən sonra da damcılayırsa, klapan yuvası aşınıb. Bütün kran dəyişdirilməlidir.</li>
<li><strong>Birləşmə yeri boşalıb</strong> — Kranın boru ilə birləşdiyi yerdən su axırsa, teflon lent vurmaq və ya fitinq sıxmaq lazımdır.</li>
</ol>

<h2>Kran tipinə görə təmir</h2>
<table>
<tr><th>Kran tipi</th><th>Problem</th><th>Həll</th></tr>
<tr><td>Tək qollu (kartuşlu)</td><td>Su damcılayır</td><td>Kartric dəyişdirilir</td></tr>
<tr><td>İki qollu (ventilli)</td><td>Tam bağlanmır</td><td>Orinq / kəcə dəyişdirilir</td></tr>
<tr><td>Sensorlu</td><td>Özbaşına açılır</td><td>Batareya və ya sensor dəyişdirilir</td></tr>
</table>

<blockquote>Kran təmiri adətən 15-30 dəqiqə çəkir. Amma düzgün ehtiyat hissə seçmək vacibdir — kranın markasını bilmək usta üçün çox faydalıdır.</blockquote>
"""
        },
        {
            'bashliq': 'Tualet su saxlamır — sifon təmiri',
            'slug': 'tualet-su-saxlamir',
            'kategori_slug': 'santexnik',
            'seo_title': 'Tualet Su Saxlamır — Sifon Təmiri | Prousta.az',
            'seo_description': 'Tualet kasası fasiləsiz su axıdır? Sifon klapanı, flotor, orinq — səbəblər və asan həllər.',
            'metn': """
<h2>Tualet kasası niyə fasiləsiz su axıdır?</h2>
<p>Tualetdən daima su axması həm su itkisi, həm narahatedici səs, həm də su hesabının artması deməkdir. Problem adətən sifon mexanizmindədir və əksər hallarda asanlıqla həll olunur.</p>

<h2>Əsas səbəblər</h2>
<ol>
<li><strong>Axıdma klapanı (flapper) köhnəlib</strong> — Sifonun dibindəki rezin klapan zamanla əyilir, çatlar. Su fasiləsiz çənə axır. Dəyişdirilməsi çox asandır.</li>
<li><strong>Flotor (üzgəc) tənzimlənməyib</strong> — Flotor çox yuxarıda qalırsa, su daşma borusundan axır. Flotoru aşağı tənzimləmək lazımdır.</li>
<li><strong>Dolum klapanı xarab</strong> — Su doldurma klapanı tam bağlanmırsa, su daima daxil olur. Klapan dəyişdirilməlidir.</li>
<li><strong>Daşma borusu qısadır</strong> — Bəzi hallarda daşma borusu düzgün uzunluqda deyil və su vaxtından əvvəl boşalır.</li>
</ol>

<h2>Evdə yoxlama</h2>
<ul>
<li>Sifon qapağını açın və suyun haradan axdığını müşahidə edin</li>
<li>Qırmızı/mavi boya damcısı atın — kasaya rəng keçirsə, klapan sızdırır</li>
<li>Flotoru əl ilə yuxarı qaldırın — su dayanırsa, flotor tənzimlənməlidir</li>
</ul>

<blockquote>Sifon dəsti dəyişdirmək 50-100 AZN-ə başa gəlir. Vaxtında həll olunmazsa aylıq su hesabınız 2-3 qat arta bilər.</blockquote>
"""
        },
        {
            'bashliq': 'Evdə su təzyiqi azdır — nə etməli?',
            'slug': 'su-tezyiqi-azdir',
            'kategori_slug': 'santexnik',
            'seo_title': 'Su Təzyiqi Azdır — Səbəb və Həll | Prousta.az',
            'seo_description': 'Evdə su zəif gəlir? Boru tıxanması, filtr çirklənməsi, nasos problemi — su təzyiqini artırma yolları.',
            'metn': """
<h2>Su təzyiqi niyə aşağı düşür?</h2>
<p>Evdə su zəif gəlməsi gündəlik həyatı ciddi şəkildə çətinləşdirir — duş almaq, qazan doldurmaq, paltaryuyan işlətmək çətinləşir. Problemin bir neçə səbəbi ola bilər.</p>

<h2>Ən çox rast gəlinən səbəblər</h2>
<ol>
<li><strong>Magistral təzyiq aşağıdır</strong> — Binanın su xəttində təzyiq azdırsa, bütün evdə su zəif gəlir. Qonşuları soruşun — onlarda da eynidirsə, problem magistraldadır.</li>
<li><strong>Boru tıxanıb / daralmış</strong> — Köhnə metal borularda əhəng və pas yığılır, borunun daxili diametri azalır. Borular dəyişdirilməlidir.</li>
<li><strong>Filtr tıxanıb</strong> — Su sayğacının yanındakı və ya kranın ucundakı filtr çirkləndikdə su axını azalır. Filtri çıxarıb təmizləyin.</li>
<li><strong>Kran aeratoru tıxanıb</strong> — Kranın ucundakı aerator (süzgəc) əhənglə dolursa, su zəif gəlir. Burub çıxarın, sirkə ilə təmizləyin.</li>
<li><strong>Su nasosu zəifləyib</strong> — Nasos quraşdırılıbsa və köhnəlibsə, təzyiq aşağı düşür.</li>
</ol>

<h2>Həll yolları</h2>
<ul>
<li>Kran aeratorlarını mütəmadi təmizləyin</li>
<li>Giriş filtrini ayda 1 dəfə yoxlayın</li>
<li>Köhnə dəmir boruları PPR borulara dəyişdirin</li>
<li>Təzyiq artırıcı nasos quraşdırın (santexnik məsləhəti ilə)</li>
</ul>

<blockquote>Su təzyiqi bütün evdə azdırsa və qonşularda normaldırsa, evin daxili su xəttində problem var. Peşəkar santexnik çağırın.</blockquote>
"""
        },
        # ===== KANALİZASİYA =====
        {
            'bashliq': 'Kanalizasiya tıxanıb — açma üsulları',
            'slug': 'kanalizasiya-tixanib',
            'kategori_slug': 'kanalizasiya-ustasi',
            'seo_title': 'Kanalizasiya Tıxanıb — Açma Üsulları | Prousta.az',
            'seo_description': 'Kanalizasiya tıxanıb, su getmir? Evdə edə biləcəyiniz üsullar və peşəkar kanalizasiya açma xidməti.',
            'metn': """
<h2>Kanalizasiya tıxanması — ən çox baş verən ev problemi</h2>
<p>Kanalizasiyanın tıxanması evdə ən tez-tez rast gəlinən və ən narahatedici problemlərdən biridir. Mətbəx lavabosunda, vanna otağında, tualetdə — istənilən yerdə baş verə bilər.</p>

<h2>Tıxanma səbəbləri</h2>
<ol>
<li><strong>Yağ və qida qalıqları</strong> — Mətbəx lavabosuna tökülən yağ borularda soyuyub qatılaşır, qida qalıqları ilə birləşib tıxac yaradır.</li>
<li><strong>Saç tükləri</strong> — Vanna və duş borusunda ən çox tıxanma saç tüklərindən olur.</li>
<li><strong>Sabun və əhəng yığılması</strong> — Sabun qalıqları borularda bərkiyir, əhənglə birlikdə daralma yaradır.</li>
<li><strong>Yanlış əşyaların atılması</strong> — Yaş salfetlər, gigiyenik məhsullar, pambıq — bunlar tualetə atılmamalıdır.</li>
<li><strong>Boru meyilinin azalması</strong> — Köhnə binalarda boruların meyili zamanla dəyişir, su normal axmır.</li>
</ol>

<h2>Evdə edə biləcəyiniz üsullar</h2>
<ol>
<li><strong>Qaynar su</strong> — Yavaş-yavaş lavaboya qaynar su tökün. Yağ tıxanmasında effektivdir.</li>
<li><strong>Soda + sirkə</strong> — Yarım stəkan soda tökün, üstünə sirkə əlavə edin. 15-20 dəqiqə gözləyin, qaynar su ilə yuyun.</li>
<li><strong>Vakuum (pompa)</strong> — Klasik rezin pompa ilə təzyiq yaradıb tıxacı açmağa cəhd edin.</li>
<li><strong>Boru yılanı (tros)</strong> — Metal spiralı boruya salıb fırladın. Ciddi tıxanmalarda effektivdir.</li>
</ol>

<blockquote>Ev üsulları kömək etmirsə, mütləq peşəkar kanalizasiya ustası çağırın. Müasir ustalar yüksək təzyiqli su ilə (hidrojet) və ya kamera ilə tıxanmanı təmizləyir.</blockquote>
"""
        },
        {
            'bashliq': 'Kanalizasiyadan pis qoxu gəlir — həll yolları',
            'slug': 'kanalizasiya-pis-qoxu',
            'kategori_slug': 'kanalizasiya-ustasi',
            'seo_title': 'Kanalizasiyadan Pis Qoxu — Səbəb və Həll | Prousta.az',
            'seo_description': 'Evdə kanalizasiya qoxusu var? Sifon quruması, boru sızıntısı, ventilyasiya problemi — səbəblər və həllər.',
            'metn': """
<h2>Evdə kanalizasiya qoxusu — nədən qaynaqlanır?</h2>
<p>Kanalizasiya qoxusu həm narahatedici, həm də sağlamlıq üçün zərərlidir — metan və hidrogen sulfid qazları xroniki baş ağrısı, ürəkbulanma yarada bilər. Səbəbi tapmaq və aradan qaldırmaq vacibdir.</p>

<h2>Əsas səbəblər</h2>
<ol>
<li><strong>Sifon quruub</strong> — Hər lavabo və drenajın altında sifon (su qıfılı) var. Uzun müddət istifadə olunmayan lavaboda sifondakı su buxarlanır, qaz geri çıxır. Sadəcə su axıdın.</li>
<li><strong>Sifon yoxdur və ya düzgün quraşdırılmayıb</strong> — Bəzən təmirdə sifon qoyulmur və ya düz boru çəkilir. Bu halda sifon quraşdırılmalıdır.</li>
<li><strong>Boru birləşmələri sızdırır</strong> — Birləşmə yerlərindəki orinqlər köhnəlibsə, qaz sızır. Orinqləri dəyişdirin.</li>
<li><strong>Ventilyasiya borusu tıxanıb</strong> — Dama çıxan ventilyasiya borusu (fayka) tıxanıbsa, qaz geri qayıdır. Boru təmizlənməlidir.</li>
<li><strong>Kanalizasiya tıxanması</strong> — Qismən tıxanma su axınını yavaşladır, stagnasiya qoxuya səbəb olur.</li>
</ol>

<h2>Sürətli həllər</h2>
<ul>
<li>İstifadə olunmayan lavabolara həftədə 1 dəfə su axıdın</li>
<li>Sifon altını yoxlayın — düzgün quraşdırılıbmı?</li>
<li>Boru birləşmə yerlərini silikon ilə möhürləyin</li>
<li>Otağı havalandırın</li>
</ul>

<blockquote>Qoxu davam edirsə, mütləq santexnik/kanalizasiya ustası çağırın. Ventilyasiya borusunun tıxanması dam üstündə iş tələb edir — peşəkar müdaxilə lazımdır.</blockquote>
"""
        },
        # ===== SU SIZMASI =====
        {
            'bashliq': 'Evdə su sızması — aşkarlama və təmir',
            'slug': 'evde-su-sizmasi',
            'kategori_slug': 'su-sizma',
            'seo_title': 'Evdə Su Sızması — Aşkarlama və Təmir | Prousta.az',
            'seo_description': 'Divarda nəmlik, tavanda ləkə, döşəmədə su? Su sızmasının aşkarlanması və təmir üsulları. Peşəkar su sızma ustası.',
            'metn': """
<h2>Su sızması — gizli təhlükə</h2>
<p>Su sızması evdəki ən gizli və ən zərərli problemlərdən biridir. Gözə görünənə qədər divarlarda, döşəmədə ciddi zərər yarada bilər. Vaxtında aşkar edilməzsə küf, paslanma, elektrik qısa qapanması və hətta konstruktiv zəiflik yaradır.</p>

<h2>Su sızmasının əlamətləri</h2>
<ul>
<li>Divar və ya tavanda nəm ləkələr</li>
<li>Boyada qabarma və ya soyulma</li>
<li>Döşəmədə əyilmə və ya şişmə</li>
<li>Su sayğacı istifadə olmadan fırlanır</li>
<li>Su hesabının anormal artması</li>
<li>Küf qoxusu</li>
</ul>

<h2>Sızmanın mənbəyini tapmaq</h2>
<ol>
<li><strong>Sayğac testi</strong> — Evdəki bütün kranları bağlayın. 1 saat gözləyin. Sayğac fırlanıbsa, gizli sızma var.</li>
<li><strong>Vizual yoxlama</strong> — Boru keçən divarları, vannanın ətrafını, kombinin altını yoxlayın.</li>
<li><strong>Termal kamera</strong> — Peşəkar ustalar termal kamera ilə divar arxasındakı sızmanı dağıntısız tapır.</li>
<li><strong>Akustik dinləyici</strong> — Boru daxilindəki su axıntı səsini algılayan cihazla sızma yeri dəqiq müəyyən edilir.</li>
</ol>

<h2>Təmir üsulları</h2>
<ul>
<li><strong>Boru birləşməsini sıxmaq</strong> — Sadə sızmalarda fitinq sıxmaq kifayət edə bilər</li>
<li><strong>Boru hissəsini dəyişmək</strong> — Zədələnmiş boru kəsilir, yenisi qaynaq edilir</li>
<li><strong>Hidroizolyasiya</strong> — Vanna altı, duş kabina — su keçirməyən örtük çəkilir</li>
</ul>

<blockquote>Su sızmasında vaxt çox vacibdir. Hər gecikən gün zərəri artırır. İlk əlaməti gördükdə dərhal peşəkar su sızma ustası çağırın.</blockquote>
"""
        },
        {
            'bashliq': 'Tavandan su damcılayır — təcili həll',
            'slug': 'tavandan-su-damcilayir',
            'kategori_slug': 'su-sizma',
            'seo_title': 'Tavandan Su Damcılayır — Təcili Nə Etməli? | Prousta.az',
            'seo_description': 'Tavandan su gəlir? Üst mərtəbə sızıntısı, dam örtüyü problemi — təcili addımlar və ustaya müraciət.',
            'metn': """
<h2>Tavandan su damcılayır — dərhal nə etməli?</h2>
<p>Tavandan su damcılaması təcili müdaxilə tələb edir. Elektrik naqillərinə su dəyə bilər ki, bu həyat üçün təhlükəlidir. İlk addımlar çox vacibdir.</p>

<h2>Təcili addımlar</h2>
<ol>
<li><strong>Elektrik panelini söndürün</strong> — Əgər su lampanın, rozetkanın yanından gəlirsə, o otağın elektrikini dərhal söndürün.</li>
<li><strong>Qab qoyun</strong> — Su toplayan qablar qoyun, döşəmə zədələnməsin.</li>
<li><strong>Üst qonşuya xəbər verin</strong> — Əksər hallarda problem üst mərtəbədəki sızıntıdandır.</li>
<li><strong>Əşyaları uzaqlaşdırın</strong> — Mebel, elektronika, xalça — su dəyə biləcək əşyaları çəkin.</li>
<li><strong>Foto/video çəkin</strong> — Sığorta və ya mübahisə üçün dəlil olacaq.</li>
</ol>

<h2>Sızıntının səbəbləri</h2>
<ul>
<li><strong>Üst qonşunun su borusu partlayıb</strong> — Ən çox rast gəlinən səbəb</li>
<li><strong>Üst qonşuda vanna/duş sızdırır</strong> — Hidroizolyasiya yoxdur</li>
<li><strong>Dam örtüyü zədələnib</strong> — Son mərtəbədə yaşayırsınızsa</li>
<li><strong>Ortaq stoyak (şaquli boru) sızır</strong> — Binanın ortaq borusundan</li>
</ul>

<blockquote>Tavandan su gəlmə problemi heç vaxt özbaşına həll olmur. Mənbə tapılmalı, su dayandırılmalı, sonra zədələnmiş hissə təmir olunmalıdır. Peşəkar usta çağırın.</blockquote>
"""
        },
        # ===== HAVALANDIRMA =====
        {
            'bashliq': 'Evdə havalandırma işləmir — nə etməli?',
            'slug': 'havalandirma-islemir',
            'kategori_slug': 'havalandirma-ustasi',
            'seo_title': 'Havalandırma İşləmir — Səbəb və Həll | Prousta.az',
            'seo_description': 'Evdə hava dəyişmir, rütubət artır, qoxu gedir? Havalandırma kanalının yoxlanması və təmiri.',
            'metn': """
<h2>Havalandırma niyə vacibdir?</h2>
<p>Düzgün işləyən havalandırma sistemi evdə təmiz hava, normal rütubət və sağlam mühit təmin edir. Havalandırma işləməzsə, rütubət artır, küf yaranır, qoxular çıxmır, pəncərələr tərləyir.</p>

<h2>Havalandırmanın işləmədiyinin əlamətləri</h2>
<ul>
<li>Vanna otağında güzgü daima tərləyir</li>
<li>Mətbəxdə yemək qoxusu saatlarla qalır</li>
<li>Pəncərə şüşələrinin içi tərləyir (kondensasiya)</li>
<li>Divarlarda küf əmələ gəlir</li>
<li>Otaqda havasızlıq, bürkü hissi</li>
</ul>

<h2>Yoxlama üsulu</h2>
<p>Sadə test: bir vərəq kağızı havalandırma dəliyinə yaxınlaşdırın. Kağız yapışmalıdır (sorulmalıdır). Yapışmırsa — hava çəkişi yoxdur.</p>

<h2>Havalandırma işləməməsinin səbəbləri</h2>
<ol>
<li><strong>Kanal tıxanıb</strong> — İnşaat qalıqları, toz, quş yuvası — kanal təmizlənməlidir.</li>
<li><strong>Qonşu kanalı bağlayıb</strong> — Təmir zamanı qonşu havalandırma kanalını kərpiçlə hörüb. Binanın USQ-sinə müraciət lazımdır.</li>
<li><strong>Hermetik pəncərə/qapılar</strong> — Plastik pəncərələr havanın daxil olmasını bağlayır. Hava girişi olmadan çıxış da işləmir.</li>
<li><strong>Ventilyator xarabdır</strong> — Mexaniki ventilyator quraşdırılıbsa və işləmirsə.</li>
</ol>

<h2>Həll yolları</h2>
<ul>
<li>Pəncərədə mikro ventilyasiya rejimini istifadə edin</li>
<li>Divar tipli hava klapanı quraşdırın</li>
<li>Vanna və mətbəxə çıxış ventilyatoru quraşdırın</li>
<li>Havalandırma kanalını peşəkar təmizlətdirin</li>
</ul>

<blockquote>Havalandırma kanalının təmizlənməsi binanın USQ ilə razılaşdırılmalıdır. Peşəkar havalandırma ustası kanalı kamera ilə yoxlayıb problemin yerini müəyyən edir.</blockquote>
"""
        },
        {
            'bashliq': 'Evdə küf yaranır — səbəbi havalandırmadır',
            'slug': 'evde-kuf-yaranir',
            'kategori_slug': 'havalandirma-ustasi',
            'seo_title': 'Evdə Küf Yaranır — Havalandırma Problemi | Prousta.az',
            'seo_description': 'Divarlarda, tavanda küf var? Əsas səbəb havalandırma çatışmazlığıdır. Küfün aradan qaldırılması və qarşısının alınması.',
            'metn': """
<h2>Küf niyə yaranır?</h2>
<p>Küf — rütubətli və havasız mühitdə yaranan göbələkdir. Sağlamlıq üçün ciddi təhlükədir: allergiya, astma, tənəffüs problemləri yarada bilər. Küfün kök səbəbi demək olar ki, həmişə rütubət və havalandırma problemidir.</p>

<h2>Küfün yaranma səbəbləri</h2>
<ol>
<li><strong>Havalandırma işləmir</strong> — Rütubətli hava çıxmır, divarlarda kondensasiya yaranır, küf inkişaf edir.</li>
<li><strong>Su sızması</strong> — Divarın arxasında gizli su sızması küf üçün ideal mühit yaradır.</li>
<li><strong>Termal körpü</strong> — Binanın istilik izolyasiyası zəifdirsə, divarın daxili səthi soyuq olur, kondensasiya toplanır.</li>
<li><strong>Vanna otağının havalandırması yoxdur</strong> — Duşdan sonra rütubət çıxmır, küf yaranır.</li>
<li><strong>Mebellərin divara yapışdırılması</strong> — Hava dövranı pozulur, arxada küf yaranır.</li>
</ol>

<h2>Küfü aradan qaldırmaq</h2>
<ol>
<li>Küflü yeri xüsusi anti-küf məhlulu ilə təmizləyin</li>
<li>Yaxşıca qurudun (hava axını, isidici)</li>
<li>Anti-küf astarla boyayın</li>
<li>Əsas səbəbi həll edin — havalandırma, izolyasiya, su sızması</li>
</ol>

<h2>Qabaqlayıcı tədbirlər</h2>
<ul>
<li>Vanna otağına ventilyator quraşdırın</li>
<li>Gündə 10-15 dəqiqə otaqları havalandırın</li>
<li>Mebeli divardan 3-5 sm aralı qoyun</li>
<li>Rütubət ölçən cihazla (higrometr) yoxlayın — 40-60% normal, 70%-dən yuxarı təhlükəlidir</li>
</ul>

<blockquote>Küfü təkcə təmizləmək kifayət deyil — səbəbi aradan qaldırmazsanız, yenə yaranacaq. Havalandırma ustası + su sızma ustası birlikdə problemi kökündən həll edə bilər.</blockquote>
"""
        },
        # ===== ƏLAVƏLƏRfunc =====
        {
            'bashliq': 'Kombi səs edir — vıyıltı, gurultu, tıqqıltı',
            'slug': 'kombi-ses-edir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Kombi Səs Edir — Səbəbləri və Həlli | Prousta.az',
            'seo_description': 'Kombi qəribə səs çıxarır? Vıyıltı, gurultu, tıqqıltı — hər səsin mənası və həll yolu.',
            'metn': """
<h2>Kombi niyə qəribə səs çıxarır?</h2>
<p>Normal işləyən kombi yalnız yüngül fan səsi çıxarır. Əgər vıyıltı, gurultu, tıqqıltı və ya partlama səsi eşidirsinizsə, bu nasazlıq əlamətidir.</p>

<h2>Səs tipinə görə diaqnoz</h2>
<table>
<tr><th>Səs tipi</th><th>Mümkün səbəb</th><th>Həll</th></tr>
<tr><td><strong>Vıyıltı / fit səsi</strong></td><td>Fan rulmanı köhnəlib</td><td>Fan dəyişdirilməlidir</td></tr>
<tr><td><strong>Gurultu / qaynama səsi</strong></td><td>İstilik dəyişdiricisində əhəng yığılıb</td><td>Kimyəvi yuma lazımdır</td></tr>
<tr><td><strong>Tıqqıltı / metal səsi</strong></td><td>Genişlənmə-daralma (termal)</td><td>Adətən normaldır, amma davam edərsə yoxlayın</td></tr>
<tr><td><strong>Partlama / pop səsi</strong></td><td>Gecikmiş alovlanma</td><td>Qaz klapanı və elektrod yoxlanmalıdır</td></tr>
<tr><td><strong>Sızıltı / su səsi</strong></td><td>Sistemdə hava var</td><td>Hava buraxılmalıdır</td></tr>
</table>

<h2>Nə etməli?</h2>
<ul>
<li>Səsin haradan gəldiyini müəyyən edin (yuxarı, aşağı, arxa)</li>
<li>Səs hansı rejimlərdə olur — istilik, isti su, hər ikisi?</li>
<li>Video çəkin — usta üçün çox faydalıdır</li>
<li>Partlama səsi eşitsəniz, dərhal kombini söndürüb usta çağırın</li>
</ul>

<blockquote>Qaynama/gurultu səsi əhəng yığılmasını göstərir. Bu vəziyyətdə kombi effektiv işləmir, qaz xərcini artırır və TEN-i zədələyir. Kimyəvi yuma ildə 1 dəfə tövsiyə olunur.</blockquote>
"""
        },
        {
            'bashliq': 'Kombi isti su vermir — yalnız soyuq su gəlir',
            'slug': 'kombi-isti-su-vermir',
            'kategori_slug': 'kombi-ustasi',
            'seo_title': 'Kombi İsti Su Vermir — Səbəblər | Prousta.az',
            'seo_description': 'Kombi yanır amma isti su gəlmir? 3-yollu klapan, NTC sensor, plata — ən çox rast gəlinən səbəblər.',
            'metn': """
<h2>Kombi işləyir amma isti su gəlmir</h2>
<p>Kombinin istilik rejiminin normal işləməsinə baxmayaraq isti su verməməsi ayrı bir problemdir. Çünki istilik və isti su rejimi fərqli mexanizmlərlə işləyir.</p>

<h2>Əsas səbəblər</h2>
<ol>
<li><strong>3-yollu klapan xarabdır</strong> — Bu klapan istilik və isti su rejimi arasında keçid edir. Xarabdırsa, su istilik dövranında qalır, krandan soyuq su gəlir. Dəyişdirilməlidir.</li>
<li><strong>NTC sensor xarabdır</strong> — Suyun temperaturunu ölçən sensor səhv göstərirsə, kombi suyu kifayət qədər qızdırmır. Sensor dəyişdirilməlidir.</li>
<li><strong>İkinci istilik dəyişdiricisi tıxanıb</strong> — Bitermik olmayan kombilərdə isti su üçün ayrıca istilik dəyişdiricisi var. Əhəng yığılarsa, su qızmır. Kimyəvi yuma lazımdır.</li>
<li><strong>Su axın sensoru (flow switch) xarab</strong> — Sensor su axınını algılamırsa, kombi isti su rejiminə keçmir.</li>
<li><strong>Qaz klapanı zəifləyib</strong> — Qaz klapanı tam açılmırsa, alov zəif olur, su kifayət qədər qızmır.</li>
</ol>

<h2>Yoxlama</h2>
<ul>
<li>İsti su kranını açanda kombi reaksiya verirmi? (alov yanırsa — problem istilik mübadiləsindədir)</li>
<li>Alov yanmırsa — flow switch və ya plata problemi</li>
<li>Su ilıq gəlirsə — NTC sensor və ya əhəng problemi</li>
</ul>

<blockquote>İsti su problemi əksər hallarda 3-yollu klapan və ya istilik dəyişdiricisi ilə bağlıdır. Təmir peşəkar kombi ustası tərəfindən aparılmalıdır.</blockquote>
"""
        },
        {
            'bashliq': 'Boru partlayıb — təcili nə etməli?',
            'slug': 'boru-partlayib',
            'kategori_slug': 'santexnik',
            'seo_title': 'Boru Partlayıb — Təcili Nə Etməli? | Prousta.az',
            'seo_description': 'Evdə boru partlayıb, su basır? Təcili addımlar, su dayandırma, usta çağırma. Peşəkar santexnik xidməti.',
            'metn': """
<h2>Boru partlayıb — panikaya düşməyin, addımları izləyin</h2>
<p>Borunun partlaması evdə ən təcili problemlərdən biridir. Hər dəqiqə böyük miqdarda su axır, döşəmə, mebel, elektrik avadanlığı zərər görür. Soyuqqanlı davranıb düzgün addımlar atmaq çox vacibdir.</p>

<h2>Təcili addımlar (ilk 5 dəqiqə)</h2>
<ol>
<li><strong>Əsas su kranını bağlayın</strong> — Evin girişindəki (sayğacın yanındakı) əsas kranı dərhal bağlayın. Bu suyu tamamilə dayandıracaq.</li>
<li><strong>Elektrik panelini söndürün</strong> — Su elektrik naqillərinə dəyə bilər. Xüsusilə su çox axırsa, paneldən o otağın avtomatını söndürün.</li>
<li><strong>Boşaltma</strong> — Əsas kranı bağladıqdan sonra borulardakı qalıq suyu boşaltmaq üçün ən aşağı mərtəbədəki bir kranı açın.</li>
<li><strong>Su yığın</strong> — Vedrə, qab, dəsmal — əlinizin altında nə varsa istifadə edin ki, su yayılmasın.</li>
<li><strong>Qonşulara xəbər verin</strong> — Əgər su aşağı axıbsa.</li>
</ol>

<h2>Borunun partlama səbəbləri</h2>
<ul>
<li><strong>Donma</strong> — Qışda izolyasiyasız borular donur, buz genişlənir, boru çatlayır</li>
<li><strong>Korroziya</strong> — Köhnə metal borular daxildən paslanıb zəifləyir</li>
<li><strong>Su təzyiqi çoxdur</strong> — Anormal yüksək təzyiq borunu çatladır</li>
<li><strong>Keyfiyyətsiz birləşmə</strong> — Qaynaq və ya fitinq düzgün edilməyib</li>
</ul>

<blockquote>Əsas su kranının yerini ailənin hər bir üzvünə göstərin. Təcili halda hər kəs bağlaya bilməlidir. Boru partlayanda dərhal peşəkar santexnik çağırın.</blockquote>
"""
        },
        {
            'bashliq': 'Kondisioner soyutmur — səbəbləri',
            'slug': 'kondisioner-soyutmur',
            'kategori_slug': 'havalandirma-ustasi',
            'seo_title': 'Kondisioner Soyutmur — Səbəblər və Həll | Prousta.az',
            'seo_description': 'Kondisioner işləyir amma soyutmur? Freon azalması, filtr tıxanması, kompressor problemi — diaqnoz və həll.',
            'metn': """
<h2>Kondisioner niyə soyutmur?</h2>
<p>Yay aylarında kondisionerin soyutmaması çox narahatedicidir. Cihaz işləyir, fan fırlanır, amma otaq soyumur. Bunun bir neçə səbəbi ola bilər.</p>

<h2>Əsas səbəblər</h2>
<ol>
<li><strong>Freon (soyuducu qaz) azalıb</strong> — Ən çox rast gəlinən səbəb. Freon sızıntı nəticəsində azalır. Doldurma lazımdır, amma əvvəlcə sızıntı yeri tapılıb bağlanmalıdır.</li>
<li><strong>Daxili filtr tıxanıb</strong> — Tozlu filtr hava axınını bloklayır, soyutma effektivliyi aşağı düşür. Filtri çıxarıb su ilə yuyun, qurudun.</li>
<li><strong>Xarici blok çirklidir</strong> — Xarici blokun radiatoru tozla, tüklə örtülürsə, istilik mübadiləsi pozulur. Yüksək təzyiqli su ilə yuyulmalıdır.</li>
<li><strong>Kompressor zəifləyib</strong> — Kompressor kondisionerin "ürəyi"dir. Zəifləyibsə, soyutma gücü azalır. Təmir və ya dəyişdirmə lazımdır.</li>
<li><strong>Termostat/sensor xarabdır</strong> — Otaq temperaturu düzgün ölçülmür, kondisioner vaxtından əvvəl dayanır.</li>
<li><strong>Rejim səhvdir</strong> — Pultda "fan only" və ya "heat" rejimindədirsə, soyutma işləməyəcək. "Cool" rejiminə keçirin.</li>
</ol>

<h2>Özünüz edə biləcəyiniz</h2>
<ul>
<li>Daxili filtri ayda 1 dəfə yuyun</li>
<li>Pultda Cool rejimi və düzgün temperaturu seçin</li>
<li>Xarici blokun önündə maneə olmadığından əmin olun</li>
<li>Kondisioneri söndürüb 5 dəqiqə gözləyin, yenidən yandırın</li>
</ul>

<blockquote>Freon doldurma və kompressor təmiri peşəkar avadanlıq tələb edir. Özünüz müdaxilə etməyin — peşəkar kondisioner ustası çağırın.</blockquote>
"""
        },
    ]

    for p_data in problemler:
        kat = get_kat(p_data['kategori_slug'])
        Problem.objects.create(
            bashliq=p_data['bashliq'],
            slug=p_data['slug'],
            kategori=kat,
            metn=p_data['metn'].strip(),
            seo_title=p_data['seo_title'],
            seo_description=p_data['seo_description'],
            aktiv=True,
        )


def unseed(apps, schema_editor):
    Problem = apps.get_model('core', 'Problem')
    Problem.objects.all().delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0015_problem_modeli'),
    ]

    operations = [
        migrations.RunPython(seed_problemler, unseed),
    ]
