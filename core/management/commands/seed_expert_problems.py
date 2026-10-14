"""
core/management/commands/seed_expert_problems.py

Prousta.az üçün 55+ yüksək axtarış tələbli, peşəkar texniki diaqnostika bələdçilərini (Problem modeli)
bazaya daxil edən idarəetmə əmri.

İstifadə:
    python manage.py seed_expert_problems
"""

from django.core.management.base import BaseCommand
from core.models import Problem, Kategori


PROBLEMLER_DATA = [
    # ---------------- KOMBI ----------------
    {
        'bashliq': 'Kombi E01 xətası — Alovlanma baş vermir (Səbəbi və Həlli)',
        'slug': 'kombi-e01-xetasi',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi E01 Xətası Nədir? Alovlanma Probleminin Səbəbi və Həlli | Prousta.az',
        'seo_description': 'Kombi E01 xətası niyə yaranır? Qaz klapanı, ionizasiya elektrodu və qaz təzyiqi nasazlıqlarının diaqnostikası və aradan qaldırılma yolları.',
        'metn': '''<h2>Kombi E01 xətası nədir və niyə baş verir?</h2>
<p>Baxi, DemirDöküm, ECA və digər bir çox kombi markalarında <strong>E01 xətası</strong> alovun yaranmadığını və ya ana platanın alovu hiss etmədiyini göstərir. Kombi işə düşməyə cəhd edir, bir neçə saniyə qığılcım vurur, lakin alov tutmadıqda təhlükəsizlik blokadasına keçir.</p>

<h2>E01 xətasının əsas səbəbləri</h2>
<ul>
<li><strong>Qaz təchizatının kəsilməsi və ya qaz kranının bağlı olması:</strong> Sayğacda qazın bitməsi, qaz tənzimləyicisinin (reduktor) ilişməsi və ya kombinin altındakı sarı qaz kranının qapalı qalması.</li>
<li><strong>İonizasiya və alovlanma elektrodunun çirklənməsi:</strong> Elektrodun üzərində his və karbon təbəqəsi yarandıqda alovun mövcudluğunu plataya ötürə bilmir.</li>
<li><strong>Qaz klapanının (qaz valfı) sıradan çıxması:</strong> Bobinlər yanmış və ya mexaniki olaraq tıxanmış ola bilər.</li>
<li><strong>Elektron ana plata nasazlığı:</strong> Alov hissiyyat mikrosxeminin zədələnməsi.</li>
<li><strong>Faza-sıfır qütbləşməsi:</strong> Xüsusilə Baxi və İtaliya istehsalı kombilərdə vilkanın yuvaya tərsinə taxılması E01 verə bilər.</li>
</ul>

<h2>Evdə nələri yoxlaya bilərsiniz?</h2>
<ol>
<li>Mətbəxdə qaz plitəsini yandıraraq mənzildə qazın olub-olmadığını yoxlayın.</li>
<li>Kombiyə gələn sarı qaz kranının boruya paralel (açıq) vəziyyətdə olduğuna əmin olun.</li>
<li>Kombinin elektrik çəngəlini (vilkasını) yuvadan çıxarıb 180 dərəcə çevirərək yenidən taxın.</li>
<li>Kombinin idarəetmə panelində "R" (Reset) düyməsini 3 saniyə basıb saxlayın.</li>
</ol>

<blockquote><strong>Diqqət:</strong> Əgər bu addımlardan sonra da E01 xətası təkrarlanırsa, qaz klapanı və elektron plata yoxlanmalıdır. Qaz sisteminə qeyri-peşəkar müdaxilə təhlükəlidir, dərhal sertifikatlı kombi ustasına müraciət edin.</blockquote>''',
    },
    {
        'bashliq': 'Kombi F4 xətası — Alov sönməsi və təhlükəsizlik blokirovkası',
        'slug': 'kombi-f4-xetasi',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi F4 Xətası Niyə Yaranır? Səbəbləri və Usta Tövsiyələri | Prousta.az',
        'seo_description': 'Kombi F4 xətası alov aşkarlanmama xətasıdır. Viessmann, DemirDöküm və digər kombilərdə F4 kodunun təmiri və aradan qaldırılması.',
        'metn': '''<h2>Kombi F4 xətası nə deməkdir?</h2>
<p>Xüsusilə <strong>Viessmann Vitopend</strong> və bir sıra müasir kombilərdə <strong>F4 xətası</strong> brülördə (ocaqda) yanmanın baş tutmadığını və ya qəfil kəsildiyini bildirir. Cihaz 3 uğursuz alışdırma cəhdindən sonra özünü qəza rejiminə keçirir.</p>

<h2>F4 xətasının ən çox rast gəlinən səbəbləri</h2>
<ul>
<li>Mənzildə və ya binada qaz təzyiqinin həddən artıq aşağı olması.</li>
<li>Alov sensorunun (ionizasiya çubuğunun) paslanması və ya zədələnməsi.</li>
<li>Qığılcım transformatorunun zəifləməsi.</li>
<li>Tüstü bacasının (koaksial borunun) çıxışında buz bağlama və ya daxili borunun ayrılması.</li>
<li>Ana idarəetmə modulunda alışdırma relesinin xarab olması.</li>
</ul>

<h2>İlk yardım addımları</h2>
<ol>
<li>Qaz sayğacınızın klapanını və mənzilə daxil olan əsas kranı yoxlayın.</li>
<li>Bacanın bayır tərəfdən qar və ya buzla tutulmadığına əmin olun.</li>
<li>Cihazı söndürüb 5 dəqiqə gözləyin və yenidən "Reset" edin.</li>
</ol>
<p>Əgər xəta silinmirsə, yanma kamerasının profilaktik təmizliyi və sensor diaqnostikası üçün usta çağırılmalıdır.</p>''',
    },
    {
        'bashliq': 'Kombi F5 / F05 xətası — Hava presostatı və tüstü çıxışı problemi',
        'slug': 'kombi-f5-f05-xetasi',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi F5 və F05 Xətası: Hava Təzyiq Açarı və Ventilyator Nasazlığı | Prousta.az',
        'seo_description': 'Kombidə F5 və ya F05 xətası hava axını çatışmazlığını göstərir. Presostat, ventilyator və baca problemlərinin aradan qaldırılması qaydaları.',
        'metn': '''<h2>Kombi F5 / F05 xətası nədir?</h2>
<p>Hermetik (bağlı kameralı) kombilərdə dəm qazının xaricə atılması və təmiz havanın içəri çəkilməsi ventilyator vasitəsilə həyata keçirilir. <strong>F5 (və ya F05) xətası</strong> hava axını sensorunun (diferensial hava presostatının) dövrəni qapamadığını bildirir.</p>

<h2>Əsas yaranma səbəbləri</h2>
<ul>
<li><strong>Küləkli hava:</strong> Güclü külək bacanın ağzına əks təzyiq vurduqda hava releləri kontaktı aça bilmir.</li>
<li><strong>Bacada silikon boruların içində kondensat (su) yığılması:</strong> Presostata gedən nazik şəffaf borucuqlarda su damcıları yarandıqda membran tərpənmir.</li>
<li><strong>Ventilyatorun pərlərinin tozla dolması və ya motorun ilişməsi:</strong> Kifayət qədər dövriyyə yığa bilmir.</li>
<li><strong>Venturi borusunun əriməsi və ya çatlaması:</strong> Bacadan gələn yüksək temperatur plastik venturi borusunu deformasiyaya uğrada bilər.</li>
<li><strong>Presostatın mexaniki köhnəlməsi:</strong> Daxili membranın elastikliyini itirməsi.</li>
</ul>

<h2>Necə həll etmək olar?</h2>
<p>Güclü külək zamanı kombini 15 dəqiqəlik söndürüb yenidən yandırmaq bəzən kömək edir. Lakin daimi təkrarlanırsa, ventilyator rulmanlarının yağlanması, venturi borusunun yenilənməsi və presostatın dəyişdirilməsi tələb olunur.</p>''',
    },
    {
        'bashliq': 'Ariston kombi 501 xətası — Alov aşkarlanmadı (Dəqiq həlli)',
        'slug': 'kombi-501-xetasi-ariston',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Ariston Kombi 501 Xətası Nədir? Səbəbi və Təmiri | Prousta.az',
        'seo_description': 'Ariston Clas, Genus və Cares kombilərində 501 xətası: Alovun olmaması səbəbləri, Reset qaydası və elektron plata təmiri haqqında.',
        'metn': '''<h2>Ariston 501 xətası nəyi bildirir?</h2>
<p>Ariston kombilərinin rəqəmsal ekranında <strong>501 xəta kodu</strong> "Mancanza Fiamma" – yəni yanma kamerasında alovun yaranmadığını və ya elektrod tərəfindən oxunmadığını göstərir. Bu, Ariston modellərində ən populyar təhlükəsizlik xətasıdır.</p>

<h2>Niyə baş verir?</h2>
<ol>
<li><strong>Kondensat çıxışı tutulub:</strong> Xüsusilə kondensasiyalı Ariston kombilərində sifon su ilə dolub boşala bilmədikdə ocaq kamerası boğulur.</li>
<li><strong>İonizasiya elektrodunun hislə örtülməsi:</strong> İncə zımpara kağızı ilə elektrodun ucu təmizlənməlidir.</li>
<li><strong>Qaz tənzimləyicisinin (valfın) minimum modulyasiya nasazlığı:</strong> İlk alışma üçün qaz klapanı lazımi mikromillimetr açılmır.</li>
<li><strong>Topraqlama (torpaqlama) xəttinin olmaması:</strong> Torpaqlama olmadıqda alov siqnalı korpusa qaçır və plata alovu görmür.</li>
</ol>

<h2>Tövsiyə olunan addımlar</h2>
<p>Panelin mərkəzindəki "Reset" düyməsini bir dəfə basın. Əgər cihaz ard-arda 3 dəfə 501 verirsə, "Reset" etməyi dayandırın, çünki qaz klapanının bobini qıza bilər. Peşəkar Ariston kombi ustasını dəvət edin.</p>''',
    },
    {
        'bashliq': 'Baxi kombi E25 xətası — Həddindən artıq qızma və sirkulyasiya problemi',
        'slug': 'kombi-e25-xetasi-baxi',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Baxi Kombi E25 Xətası: Sirkulyasiya Nasosu və Qızma Səbəbləri | Prousta.az',
        'seo_description': 'Baxi kombidə E25 xətası nədir? Nasos ilişməsi, sistemdə hava və filtr tıxanması hallarında nə etməli? Ətraflı usta məlumatı.',
        'metn': '''<h2>Baxi E25 xətası nədir?</h2>
<p><strong>Baxi E25 xətası</strong> istilik dövranında suyun hərəkət etmədiyini və temperaturun saniyələr içində kritik həddi aşdığını (pompa blokirovkası və ya qızma) xəbərdar edir.</p>

<h2>Səbəbləri:</h2>
<ul>
<li><strong>Sirkulyasiya nasosunun ilişməsi:</strong> Yay aylarından sonra nasosun mili ərplə tutularaq fırlanmaya bilər.</li>
<li><strong>Radiator filtrinin (patronun) palçıqla dolması:</strong> Kombinin altına quraşdırılmış çirktutan filtr tıxandıqda su dövranı dayanır.</li>
<li><strong>İstilik sistemində hava tıxacı:</strong> Radiatorlarda və ya kombinin avtomatik hava atıcısında hava qaldıqda nasos quru fırlanır.</li>
<li><strong>Bütün radiator kranlarının qapalı olması:</strong> Dövriyyə qapalı qaldığı üçün su kombi daxilində qaynayır.</li>
</ul>

<h2>Ev şəraitində həlli:</h2>
<p>Bütün radiatorların alt və üst kranlarının açıq olduğunu yoxlayın. Kombinin altındakı fitr vintini açıb təmizləmək mümkündür. Nasos ilişibsə, usta nasosun arxasındakı vinti açıb mili əl ilə fırladaraq blokadadan çıxarır.</p>''',
    },
    {
        'bashliq': 'Kombi su təzyiqi niyə düşür? (Su azalmasının səbəbləri və aradan qaldırılması)',
        'slug': 'kombi-tezyiqi-dusur',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombinin Su Təzyiqi Niyə Düşür? Gizli Sızma və Çən Problemi | Prousta.az',
        'seo_description': 'Kombidə təzyiq 1 barın altına düşür və sistem sönür? Təzyiq azalmasının 5 əsas səbəbi, genləşmə çəni havası və radiator sızmaları.',
        'metn': '''<h2>Kombi təzyiqinin norması nə qədərdir?</h2>
<p>Standart mənzillərdə kombi manometrində soyuq halda su təzyiqi <strong>1.2 – 1.5 bar</strong> aralığında olmalıdır. Əgər təzyiq hər gün və ya həftədə bir neçə dəfə 0.5-0.8 bara enirsə, bu sistemdə ciddi nasazlıqdan xəbər verir.</p>

<h2>Təzyiqin düşməsinin 5 əsas səbəbi</h2>
<ol>
<li><strong>Genləşmə çəninin havasının bitməsi və ya membranın cırılması:</strong> Çəndə hava (azot) qalmadıqda su genişlənərkən 3 bar təhlükəsizlik klapanından çölə tökülür, soyuduqda isə təzyiq sıfıra enir.</li>
<li><strong>Döşəməaltı (isti pol) və ya borularda gizli su sızması:</strong> Divar içi boru birləşmələrində mikro sızmalar suyu buxarlandırır və gözlə görünmür.</li>
<li><strong>Radiator ventillərindən və pürjordan su damcılaması:</strong> Radiator kranlarının kipkəcləri köhnəldikdə su damcılayır.</li>
<li><strong>3 bar qəza klapanının boşalması:</strong> Əvvəllər klapandan su axıbsa, daxilinə qum dənəciyi düşərək kip bağlanmaya bilər.</li>
<li><strong>Kombinin əsas istilik dəyişdiricisində (eşanjör) mikrocüt:</strong> Su yanma kamerasında alovun içinə buxarlanır.</li>
</ol>

<h2>Nə etməli?</h2>
<p>Əvvəlcə bütün radiatorları quru salfetlə silərək nəmlik olub-olmadığını yoxlayın. Genləşmə çəninin havası xüsusi manometrlə yoxlanılmalı və 0.8-1.0 bar hava vurulmalıdır. Problemi təyin etmək üçün təcrübəli kombi ustası çağırmaq tövsiyə olunur.</p>''',
    },
    {
        'bashliq': 'Kombi su təzyiqi niyə qalxır? (Təzyiqin 3 bara çatması)',
        'slug': 'kombi-tezyiqi-qalxir',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi Su Təzyiqi Niyə Öz-özünə Qalxır? 3 Bar Klapanı Niyə Axıdır? | Prousta.az',
        'seo_description': 'Kombidə bar təzyiqi 2.5 - 3 bara qalxır və kombinin altından su axır? Doldurma kranı, plitəli eşanjör və genləşmə çəni nasazlıqları.',
        'metn': '''<h2>Kombi təzyiqi niyə artır?</h2>
<p>Kombinin manometri 2.5 - 3 barı keçdikdə təhlükəsizlik klapanı sistemi qorumaq üçün artıq suyu kombinin altından boşaltmağa başlayır. Təzyiqin öz-özünə qalxması təhlükəli haldır və iki əsas qrup səbəbə bölünür:</p>

<h2>Əsas səbəblər</h2>
<ul>
<li><strong>Doldurma kranının sıradan çıxması:</strong> Kombiyə su vurduğunuz plastik və ya kran başlığı yivdən qaçıb, kran kip bağlanmır və şəhər su xəttindən fasiləsiz su sızır.</li>
<li><strong>İkinci dərəcəli (plitəli) eşanjörün deşilməsi:</strong> İsti su eşanjörünün daxili arakəsməsi çürüdükdə yüksək təzyiqli krant suyu kombinin qapalı radiator dövriyyəsinə qarışır və təzyiqi qaldırır.</li>
<li><strong>Genləşmə çəninin tamamilə su ilə dolması:</strong> Su qızdıqda genişlənmə həcmi tapmır və təzyiq dərhal kəskin sıçrayış edir.</li>
</ul>

<h2>Necə müəyyən etməli?</h2>
<p>Kombi sönük və soyuq vəziyyətdə belə təzyiq qalxırsa — günahkar doldurma kranı və ya plitəli eşanjördür. Əgər təzyiq ancaq kombi yananda və su qızanda qalxırsa — səbəb genləşmə çəninin havasız olmasıdır.</p>''',
    },
    {
        'bashliq': 'Kombi partlayışla və ya tappıltı ilə yanır — Səbəbi və təhlükəsi',
        'slug': 'kombi-partlayisla-yanir',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi Niyə Tappıltı və Partlayış Səsi ilə Yanır? | Prousta.az',
        'seo_description': 'Kombi alışarkən qorxulu səs çıxarır? Gecikmiş alovlanma, çirkli forsunkalar və elektrod məsafəsi haqqında usta diaqnostikası.',
        'metn': '''<h2>Partlayışla alışma nədir?</h2>
<p>Kombidə isti su açıldıqda və ya radiator dövriyyəsi işə düşdükdə qaz kameraya daxil olur. Əgər qığılcım vaxtında verilmirsə və ya qaz yanma kamerasında həddən artıq toplanırsa, alışma ani partlayış səsi (tappıltı) ilə baş verir. Bu zaman hətta cihazın korpusu silkələnə bilər.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Alışdırma elektrodunun uzaqlaşması və ya hislənməsi:</strong> Qığılcım zəif vurur və ya qaz çıxan dəlikdən çox uzaqda yerləşir.</li>
<li><strong>Qaz forsunkalarının (jiklörlərin) tozla tutulması:</strong> Qazın paylanması qeyri-bərabər olur.</li>
<li><strong>Tüstü borusunda geriyə sovrulma (hava çatışmazlığı):</strong> Kamera daxilində oksigen azlığı yanmanı gecikdirir.</li>
<li><strong>Qaz klapanının ilkin açılma təzyiqinin həddindən artıq yüksək olması.</strong></li>
</ul>

<blockquote><strong>Vacib:</strong> Gecikmiş alışma yanma kamerasının hermetikliyini poza bilər və dəm qazı sızmasına səbəb ola bilər. Belə halda kombini istifadə etməyi dayandırıb təcili usta çağırın.</blockquote>''',
    },
    {
        'bashliq': 'Kombidən isti su gah isti, gah soyuq gəlir — Dalğalanma səbəbləri',
        'slug': 'kombi-isti-su-dalgalanir',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi Suyu Gah İsti, Gah Soyuq Gəlir? Səbəbləri və Həlli | Prousta.az',
        'seo_description': 'Çimərkən suyun qəfil soyuması və dalğalanması problemi. NTC sensoru, kran su təzyiqi və ərp bağlamış eşanjör təmiri.',
        'metn': '''<h2>İsti suyun sabit gəlməməsi problemi</h2>
<p>Hamamda duş qəbul edərkən suyun bir neçə dəqiqədən bir qəfil qaynar, sonra isə buz kimi soyuq olması ən çox şikayət edilən problemlərdəndir. Bu, istifadəçi üçün böyük narahatlıq yaradır.</p>

<h2>Əsas səbəblər:</h2>
<ol>
<li><strong>Şəbəkədə su təzyiqinin qeyri-sabit olması:</strong> Evdə hidrofor və ya su nasosu yoxdursa və su xəttində təzyiq enib-qalxırsa, kombinin axın sensoru alovu söndürüb-yandırır.</li>
<li><strong>İkinci eşanjörün ərplə tutulması:</strong> Bakı suları çox cod olduğu üçün mis/paslanmaz polad lövhələrin arası ərp qatı ilə örtülür. İstilik ötürülmür, kombi həddindən artıq qızaraq alovu söndürür, su soyuduqda isə yenidən yandırır.</li>
<li><strong>İsti su NTC temperatur sensorunun nasazlığı:</strong> Sensor temperaturu düzgün ölçə bilmir və plataya yalnış siqnal göndərir.</li>
<li><strong>Üçyollu klapanın (3 yollu vana) motorunun tam keçid etməməsi:</strong> İsti suyun bir hissəsi radiatorlara qaçır.</li>
</ol>

<h2>Həlli:</h2>
<p>İkinci dərəcəli eşanjör xüsusi kimyəvi məhlul və aparat vasitəsilə ərpdən yuyulmalıdır. NTC sensorları multimetrlə test edilərək lazım gələrsə dəyişdirilməlidir.</p>''',
    },
    {
        'bashliq': 'Radiatorların altı soyuq, üstü isti qalır — Səbəbi və açılması',
        'slug': 'kombi-radiatorlarin-alti-qizmir',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Radiatorun Altı Niyə Qızmır? Batareyaların Yuyulması və Balanslaşdırma | Prousta.az',
        'seo_description': 'Kombi radiatorlarının alt hissəsi soyuq qalır? Palçıq tıxanması, hava tıxacı və tərs dövriyyə problemlərinin peşəkar həlli.',
        'metn': '''<h2>Batareyaların alt hissəsinin soyuq qalması</h2>
<p>Kombi radiatorunun üst hissəsi qaynar olduğu halda alt hissəsinin ilıq və ya tamamilə soyuq qalması otağın qızmamasına və qaz sərfiyyatının artmasına səbəb olur.</p>

<h2>Bu halın başlıca səbəbləri:</h2>
<ul>
<li><strong>Palçıq və qara lil çökməsi:</strong> İllər ərzində radiatorların daxilində yaranan metal korroziyası və palçıq ən ağır çəki ilə radiatorun alt kanallarına çökərək suyun axınına mane olur.</li>
<li><strong>Sistemdə balansın pozulması:</strong> Kombiyə yaxın olan radiatorlar isti suyu dərhal geri qaytarır, ən uzaq radiatorlara isə dövriyyə çatmır.</li>
<li><strong>Sirkulyasiya nasosunun gücünün zəifləməsi:</strong> Nasos kondensatoru zəiflədikdə lazımi axın sürətini təmin edə bilmir.</li>
<li><strong>Giriş-çıxış borularının səhv qoşulması:</strong> İsti suyun alt kranla, qayıdışın isə üst kranla birləşdirilməsi tərs dövriyyə yaradır.</li>
</ul>

<h2>Necə düzəltmək olar?</h2>
<p>Kombiyə yaxın radiatorların alt kranlarını bir az qısaraq uzaq radiatorlara təzyiq ötürün (balanslaşdırma). Əgər radiatorlar 3 ildən çoxdur yuyulmayıbsa, xüsusi kompressorla radiator yuma xidməti sifariş edilməlidir.</p>''',
    },
    {
        'bashliq': 'Kombi və borular donub — Təhlükəsiz qızdırma və açılma qaydaları',
        'slug': 'kombi-donub',
        'kategori_slug': 'kombi-ustasi',
        'seo_title': 'Kombi Donduqda Nə Etməli? Donmuş Boruların Açılması Qaydaları | Prousta.az',
        'seo_description': 'Şaxtalı havalarda balkondakı kombi və plastik su boruları donubsa nə etməli? Partlamanın qarşısını almaq üçün təhlükəsiz üsullar.',
        'metn': '''<h2>Balkondakı kombinin donması</h2>
<p>Qış aylarında şaxtalı gecələrdə balkonda quraşdırılmış açıq tipli kombilər və onlara gələn su boruları dona bilər. Donmuş kombini qətiyyən dərhal işə salmaq olmaz, çünki bu nasosun yanmasına və eşanjörün partlamasına səbəb olar.</p>

<h2>Addım-addım təhlükəsiz açılma qaydaları:</h2>
<ol>
<li>Kombini elektrik şəbəkəsindən tam ayırın və qaz kranını bağlayın.</li>
<li>Kombinin altına daxil olan soyuq su və isti su borularını fen (saç feni və ya texniki fen) vasitəsilə tədricən qızdırın.</li>
<li>Açıq alovdan (qaz lampası, alışqan) qətiyyən istifadə etməyin — plastik borular əriyə və yanğın çıxa bilər.</li>
<li>Təzyiq manometrinə nəzarət edin; buz əridikcə manometr 0-a düşə bilər. Doldurma kranı ilə sistemi 1.5 bara qaldırın.</li>
<li>Sirkulyasiya nasosunun pərlərinin buzdan azad olub-olmadığını yoxlamadan kombini yandırmayın.</li>
</ol>

<blockquote><strong>Qabaqlayıcı tədbir:</strong> Gələcəkdə donmanın qarşısını almaq üçün balkondakı borular mütləq izolyasiya edilməli və kombiyə xüsusi qoruyucu şkaf quraşdırılmalıdır.</blockquote>''',
    },

    # ---------------- KONDISIONER ----------------
    {
        'bashliq': 'Kondisionerin daxili blokundan içəri su damcılayır — Səbəbi və həlli',
        'slug': 'kondisioner-su-damizdirir',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisionerdən İçəri Su Axır? Səbəbləri və Drenaj Təmiri | Prousta.az',
        'seo_description': 'Kondisioner niyə otağa su damladır? Drenaj borusunun tıxanması, bucaq maililiyinin səhv olması və freon azlığı halları.',
        'metn': '''<h2>Kondisioner otağın içinə niyə su axıdır?</h2>
<p>Kondisioner soyutma rejimində işləyərkən otaqdakı havanın nəmini radiator lövhələrində kondensasiya edir və bu su drenaj qabı vasitəsilə boru ilə bayıra axmalıdır. Su içəri damcılayırsa, drenaj sistemində problem yaranıb.</p>

<h2>Əsas səbəblər:</h2>
<ul>
<li><strong>Drenaj borusunun tutulması:</strong> Bayıra çıxan borunun ucuna toz, kir və ya həşəratlar (arılar) yuva qura bilər. Nəticədə su geri daşır.</li>
<li><strong>Daxili blokun mailliyinin pozulması:</strong> Divara quraşdırılma zamanı blok su axını tərəfinə yox, əks tərəfə əyri vurulubsa, su vannasından daşır.</li>
<li><strong>Drenaj vannasında çat və ya çıxış şlanqının ayrılması:</strong> Vibrasiya və ya zədələnmə səbəbindən şlanq yuvadan çıxır.</li>
<li><strong>Freon qazının kəskin azalması:</strong> Radiator qismən donur, kompressor sönəndə buz sürətlə əriyir və vanna bu həcmdə suyu qəbul edə bilmir.</li>
</ul>

<h2>Nə etmək lazımdır?</h2>
<p>Cihazı dərhal söndürün ki, divar kağızı və parket zədələnməsin. Drenaj borusunun çıxışını yoxlayın, tıxanıbsa təzyiqli hava və ya məftillə təmizləyin. Problem davam edərsə, daxili blok sökülüb yuyulmalıdır.</p>''',
    },
    {
        'bashliq': 'Kondisionerin boruları və daxili bloku buz bağlayır',
        'slug': 'kondisioner-buz-baglayir',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisioner Niyə Buz Bağlayır? Boruların Buzlaması və Freon Əskikliyi | Prousta.az',
        'seo_description': 'Kondisionerin mis boruları və radiatoru niyə qarla örtülür? Filtr çirklənməsi, ventilyator nasazlığı və freon qazı çatışmazlığı.',
        'metn': '''<h2>Buz bağlama nə üçün baş verir?</h2>
<p>Kondisionerin mis borularında və ya daxili blokun metal pətəklərində qalın qar və buz qatının əmələ gəlməsi normal hal deyil. Bu, buxarlandırıcıda istilik mübadiləsinin pozulduğunu göstərir.</p>

<h2>Səbəblər:</h2>
<ol>
<li><strong>Filtrlərin ifrat dərəcədə tozla dolması:</strong> Hava pətəklərdən keçə bilmir, soyuq pətəyin üzərində toplanır və sıfır dərəcədən aşağı düşərək nəmi dondurur.</li>
<li><strong>Freon (qaz) çatışmazlığı:</strong> Təzyiq düşdüyü üçün buxarlanma temperaturu mənfiyə düşür və nazik boru dərhal buz tutur.</li>
<li><strong>Daxili blok ventilyatorunun (turbin) yavaş fırlanması:</strong> Turbin motorunun kondensatoru xarab olduqda hava sirkulyasiyası öləziyir.</li>
<li><strong>Kapilyar borunun tıxanması:</strong> Freon dövriyyəsi məhdudlaşır.</li>
</ol>

<h2>Usta müdaxiləsi:</h2>
<p>Filtrləri çıxarıb ilıq su ilə yuyun. Əgər pətəklər hələ də buz tutursa, kondisioneri "Fan" (sadə ventilyator) rejiminə qoyaraq buzu əridin və freon təzyiqini ölçdürmək üçün mütəxəssis çağırın.</p>''',
    },
    {
        'bashliq': 'Kondisionerdən gələn pis və nəm qoxusunun aradan qaldırılması',
        'slug': 'kondisioner-pis-qoxu-verir',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisionerdən Gələn Pis İy Niyə Olur? Antibakterial Təmizləmə | Prousta.az',
        'seo_description': 'Kondisioner işə düşəndə kəskin kif və nəm qoxusu gəlir? Bakteriyaların məhv edilməsi, dərin kimyəvi yuma və profilaktika.',
        'metn': '''<h2>Kondisionerdən gələn pis qoxu sağlamlığa ziyandırmı?</h2>
<p>Kondisioner işə düşərkən otağa nəm, kif və ya çürüntü qoxusunun yayılması daxili blokda göbələk və bakteriyaların (o cümlədən Legionella) çoxaldığını göstərir. Bu qoxu nəfəs yolları allergiyasına səbəb ola bilər.</p>

<h2>Qoxunun səbəbləri:</h2>
<ul>
<li>Pətəklərdə və drenaj vannasında daimi rütubətli mühitin qalması.</li>
<li>İllərlə yuyulmayan hava filtrləri və pər turbini.</li>
<li>Drenaj borusunun birbaşa kanalizasiya xəttinə süzgəcsiz (sifonsuz) qoşulması — kanalizasiya qoxusu birbaşa otağa sovrulur.</li>
</ul>

<h2>Necə təmizlənməlidir?</h2>
<p>Sadəcə ətir vurmaq kömək etmir. Kondisioner xüsusi çətir (yuma örtüyü) geyindirilərək kimyəvi dezinfeksiya məhlulu və buxar generatoru vasitəsilə yuyulmalıdır.</p>''',
    },
    {
        'bashliq': 'Qışda kondisioner otağı qızdırmır — Səbəbləri və qaydaları',
        'slug': 'kondisioner-qizdirmir',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisioner Qızdırmır? İsti Hava Vurmamasının Səbəbləri | Prousta.az',
        'seo_description': 'Qışda kondisioner niyə isti hava üfürmür? 4 yollu klapan, defrost rejimi və aşağı temperatur hədləri haqqında məlumat.',
        'metn': '''<h2>Kondisioner isti vurmur: Niyə?</h2>
<p>Qış aylarında kondisioneri "Heat" (isti) rejiminə keçirdikdə dərhal isti hava gəlmir. Lakin 10-15 dəqiqə keçməsinə baxmayaraq hava ilıq və ya soyuq qalırsa, problem var.</p>

<h2>Əsas səbəblər:</h2>
<ol>
<li><strong>Rejim səhvi:</strong> Pultda günəş işarəsi ("Heat") yerinə qar dənəciyi ("Cool") və ya damcı ("Dry") seçilib.</li>
<li><strong>İlkin qızma gecikməsi (Defrost):</strong> Bayırdakı blok buz bağladıqda cihaz özünü qorumaq üçün defrost rejiminə keçir və daxili blok fanını dayandırır. Bu 10 dəqiqə çəkə bilər.</li>
<li><strong>Dördyollu klapanın (4-way valve) ilişməsi:</strong> Freonun axın istiqamətini istiliyə çevirən maqnit klapan işləmir.</li>
<li><strong>Freon azlığı:</strong> Qaz az olduqda istilik ötürmə qabiliyyəti kəskin zəifləyir.</li>
<li><strong>Bayırda temperaturun çox aşağı olması:</strong> Standart (on/off) kondisionerlər -5 dərəcədən aşağı temperaturda effektiv işləmir.</li>
</ol>''',
    },
    {
        'bashliq': 'Kondisionerdən güclü səs, vıyıltı və silkələnmə gəlir',
        'slug': 'kondisioner-ses-kuy-edir',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisionerdən Narahatedici Səs Gəlir? Daxili və Çöl Blok Səsi | Prousta.az',
        'seo_description': 'Kondisioner işləyərkən cingilti, fit və silkələnmə səsi çıxarır? Kompressor podşipniki, rezin yastıqlar və balans nasazlıqları.',
        'metn': '''<h2>Kondisionerin səs-küylü işləməsi</h2>
<p>Kondisionerin həm daxili, həm də çöl blokundan gələn kənar səslər mexaniki aşınmanın və ya montaj səhvinin göstəricisidir.</p>

<h2>Səslərin növləri və mənaları:</h2>
<ul>
<li><strong>Çöl blokun divarı titrətməsi (uğultu):</strong> Çöl blokun kronşteynlərinin altına antivibrasiya rezin yastıqları qoyulmayıb və ya kompressor boltları boşalıb.</li>
<li><strong>Daxili blokdan cırıldayan plastik səsi:</strong> İstilik dəyişməsi zamanı keyfiyyətsiz plastik korpusun genişlənməsi.</li>
<li><strong>Sürtünmə və vıyıltı səsi:</strong> Turbin ventilyatorunun podşipniki sıradan çıxıb və ya plastik pər gövdəyə sürtünür.</li>
<li><strong>Fışıltı və qaz axını səsi:</strong> Borularda freonun kəskin çatışmazlığı və ya boruların əzilməsi.</li>
</ul>''',
    },
    {
        'bashliq': 'Kondisionerdə freon qazının sızmasını necə bilmək olar?',
        'slug': 'kondisioner-freon-sizmasi',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisionerdə Freon Sızması Əlamətləri və Qaz Vurulması | Prousta.az',
        'seo_description': 'Kondisionerin qazı qurtarıb? Freon sızmasının əsas simptomları, boruların yağlanması və vakuumla yoxlama qaydaları.',
        'metn': '''<h2>Freon öz-özünə bitə bilərmi?</h2>
<p>Normal halda kondisionerin soyutma sistemi tam hermetikdir və freon qazı illərlə "bitmir". Əgər qaz azalıbsa, deməli boru xəttində və ya birləşmə valslarında <strong>sızma (qaçaq)</strong> var. Sadəcə qaz vurmaq müvəqqəti təsirlidir, əsas sızma nöqtəsi tapılmalıdır.</p>

<h2>Freon sızmasının 4 əsas əlaməti:</h2>
<ol>
<li>Cihaz soyutmur, ancaq otaq temperaturunda hava vurur.</li>
<li>Çöl blokdakı nazik mis borunun çıxışında qrov və buz əmələ gəlir.</li>
<li>Mis boruların fitinq birləşmələrində yağ ləkələri görünür (freon kompressor yağı ilə birlikdə sızır).</li>
<li>Kompressor fasiləsiz işləyir və həddindən artıq qızaraq termik mühafizəyə düşür.</li>
</ol>
<p>Peşəkar usta sistemi elektron sızma axtaran cihaz və ya sabun köpüyü ilə yoxlayır, sızmanı ləğv edir, sistemi vakuumlayır və tərəzi ilə qramla freon (R410A, R32) doldurur.</p>''',
    },
    {
        'bashliq': 'Kondisioner işə düşdükdən bir neçə dəqiqə sonra öz-özünə sönür',
        'slug': 'kondisioner-oz-ozune-sonur',
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisioner Bir Neçə Dəqiqədən Sonra Sönür? Səbəbləri | Prousta.az',
        'seo_description': 'Kondisioner açılır, bir az işləyib sönür və işıqları yanıb-sönür? Termistor, kompressor qızması və plata xətaları.',
        'metn': '''<h2>Kondisionerin qəfil sönməsi</h2>
<p>Cihaz işə salındıqdan 2-5 dəqiqə sonra kompressorun dayanması və panel işıqlarının (taymer / run) yanıb-sönməsi özünüqoruma rejiminin aktivləşdiyini göstərir.</p>

<h2>Əsas səbəblər:</h2>
<ul>
<li><strong>Çöl blok pətəklərinin kir və qovaq tükü ilə dolması:</strong> İstilik bayıra atıla bilmir, qaz təzyiqi kəskin artır və yüksək təzyiq sensoru kompressoru söndürür.</li>
<li><strong>Kompressor işəsalma kondensatorunun (kapasitor) sıradan çıxması:</strong> Kompressor güc yığa bilmir və qızır.</li>
<li><strong>Temperatur sensorlarının (termistor) müqavimətinin pozulması:</strong> Boru sensoru plataya yanlış yüksək istilik məlumatı ötürür.</li>
<li><strong>Şəbəkədə gərginliyin aşağı olması:</strong> Gərginlik 190V-dan aşağı düşdükdə inverter olmayan cihazlar dayana bilər.</li>
</ul>''',
    },

    # ---------------- PALTARYUYAN ----------------
    {
        'bashliq': 'Paltaryuyan maşın suyu boşaltmır — Drenaj nasosu nasazlığı',
        'slug': 'paltaryuyan-suyu-bosaltmir',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyan Suyu Niyə Boşaltmır? Pompa Təmiri və Filtr Təmizlənməsi | Prousta.az',
        'seo_description': 'Paltaryuyan maşında su qaldı və sıxmaya keçmir? Drenaj filtri, nasos çarxı və xəta kodları haqqında ətraflı bələdçi.',
        'metn': '''<h2>Paltaryuyan su ilə dolu qaldıqda nə etməli?</h2>
<p>Proqramın ortasında və ya yaxalama mərhələsində paltaryuyan maşının suyu çənində saxlaması və sıxmaya keçməməsi ən məşhur problemlərdəndir (Samsung "5E/5C", LG "OE", Bosch "E18").</p>

<h2>Əsas səbəblər:</h2>
<ol>
<li><strong>Drenaj filtrinin tutulması:</strong> Aşağı sağ küncdəki filtr qapağının içinə qəpik, sancaq, düymə və ya corab ilişmiş ola bilər.</li>
<li><strong>Drenaj nasosunun (pompa) yanması:</strong> Pompanın pəri ilişib fırlanmaya bilər və ya motorun sarğıları qopub.</li>
<li><strong>Kanalizasiya çıxış şlanqının əzilməsi və ya tıxanması:</strong> Divara birləşən xortum qatlanıb.</li>
<li><strong>Səviyyə sensorunun (presostat) borusunun palçıqlanması:</strong> Sensor suyun boşaldığını görə bilmir.</li>
</ol>

<h2>Təcili həll addımı:</h2>
<p>Paltaryuyanın aşağı sağ hissəsindəki balaca qapağı açın, qabaqcadan yerə qab və ya dəsmal qoyaraq filtri saat əqrəbinin əksinə burub çıxarın və daxilindəki yad cisimləri təmizləyin.</p>''',
    },
    {
        'bashliq': 'Paltaryuyan maşın suyu qızdırmır — Ten (qızdırıcı element) xətası',
        'slug': 'paltaryuyan-suyu-qizdirmir',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyan Suyu Qızdırmır? Ten Nasazlığı və Termostat Dəyişdirilməsi | Prousta.az',
        'seo_description': 'Paltaryuyan soyuq su ilə yuyur və paltarlar təmizlənmir? Ten yanması, ərp bağlama və elektron plata təmiri.',
        'metn': '''<h2>Paltaryuyanın soyuq su ilə yuması problemi</h2>
<p>Paltaryuyanın şüşə qapısına yuma başlanandan 20-30 dəqiqə sonra toxunduqda şüşə isti deyilsə, maşın suyu qızdırmır. Bu zaman paltarlar yaxşı təmizlənmir və yuyucu toz ərimir.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Qızdırıcı elementin (Ten) sıradan çıxması:</strong> Suyun codluğuna görə tenin üzəri qalın ərp təbəqəsi ilə örtülür, istiliyi ötürə bilmir və partlayır.</li>
<li><strong>Temperatur sensorunun (NTC) zədələnməsi:</strong> Tenin üzərində yerləşən sensor platanı aldadır.</li>
<li><strong>İdarəetmə platasında qızdırıcı relesinin yanması:</strong> Platadan tenə 220V gərginlik ötürülmür.</li>
<li><strong>Presostat nasazlığı:</strong> Maşın suyun dolduğunu tam təsdiqləmədən teni işə salmır.</li>
</ul>
<p>Nasaz ten multimetrlə yoxlanılmalı və əgər müqavimət sonsuzluq göstərirsə, yeni orijinal tenlə əvəzlənməlidir.</p>''',
    },
    {
        'bashliq': 'Paltaryuyan maşın sıxmır və baraban fırlanmır',
        'slug': 'paltaryuyan-sixma-etmir',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyan Niyə Sıxmır? Baraban Fırlanmır və Paltarlar Yaş Qalır | Prousta.az',
        'seo_description': 'Paltaryuyan sıxma mərhələsində dayanır? Qayış qırılması, motor kömürləri, taxoqenerator və balans disbalansı haqqında.',
        'metn': '''<h2>Paltarlar niyə sıxılmır və yaş qalır?</h2>
<p>Proqram bitdikdən sonra paltarların su içində qalması barabanın yüksək dövriyyə (800-1200 dövr/dəq) yığa bilməməsindən qaynaqlanır.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Paltarların bir yerə toplanması (disbalans):</strong> Yorğan, örtük kimi iri əşyalar tək yuyulduqda baraban bir tərəfə ağırlaşır və maşın silkələnməmək üçün sıxmanı dayandırır.</li>
<li><strong>Motor kömürlərinin (şotkaların) yeyilməsi:</strong> Kollektorlu mühərriklərdə kömürlər sürtülüb qurtardıqda motor güc yığa bilmir.</li>
<li><strong>Ötürücü qayışın (kəmərin) çıxması və ya qırılması:</strong> Motor fırlansa da baraban tərpənmir.</li>
<li><strong>Taxosensorun nasazlığı:</strong> Motorun dövriyyə sayını ölçən maqnit sensoru boşalıb.</li>
</ul>''',
    },
    {
        'bashliq': 'Paltaryuyan maşın sıxarkən tullanır və dəhşətli səs çıxarır',
        'slug': 'paltaryuyan-cox-ses-titreyis',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyan Sıxarkən Niyə Tullanır və Qışqırır? Podşipnik və Amortizator | Prousta.az',
        'seo_description': 'Paltaryuyan yerindən tərpənir, vertolyot səsi çıxarır? Podşipnik (rulman) dağılması, amortizator və tənzimləmə ayaqları.',
        'metn': '''<h2>"Təyyarə qalxış səsi" və şiddətli vibrasiya</h2>
<p>Sıxma zamanı paltaryuyanın bərk cingiltili səs çıxarması və vanna otağında yerindən hərəkət etməsi maşının mexaniki dayaq sisteminin sıradan çıxdığını bildirir.</p>

<h2>Əsas səbəblər:</h2>
<ol>
<li><strong>Çənin podşipniklərinin (rulman) və salnikinin dağılması:</strong> Su salnikdən keçib podşipniki paslandırır. Boş halda barabanı əl ilə yuxarı qaldırdıqda lüft varsa və fırlatdıqda metal səsi gəlirsə, rulmanlar dəyişməlidir.</li>
<li><strong>Amortizatorların (demfer) boşalması:</strong> Çənin titrəyişini boğan amortizatorlar yağını itirdikdə çən divarlara çırpılır.</li>
<li><strong>Nəqliyyat boltlarının açılmaması:</strong> Yeni alınan maşınlarda arxadakı 4 ədəd daşınma boltu açılmadıqda maşın dərhal tullanır.</li>
<li><strong>Döşəmənin hamar olmaması və ayaqların düzgün tənzimlənməməsi.</strong></li>
</ol>''',
    },
    {
        'bashliq': 'Paltaryuyan maşın su götürmür — Səbəbi və kran yoxlanışı',
        'slug': 'paltaryuyan-su-goturmur',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyan Niyə Su Yığmır? Giriş Klapanı və Şəbəkə Təzyiqi | Prousta.az',
        'seo_description': 'Paltaryuyan işə düşür, amma su gəlmir? Giriş filtri, su klapanı və qapı kilidi (UBL) nasazlıqlarının izahı.',
        'metn': '''<h2>Paltaryuyan su almır: İlk nəyi yoxlamalı?</h2>
<p>Start düyməsini basdıqdan sonra cihazdan xırıltı səsi gəlir, lakin barabana su tökülmürsə, bu addımları yoxlayın:</p>

<h2>Səbəblər:</h2>
<ul>
<li>Divardakı su kranının bağlı olması və ya şəhər su təchizatının kəsilməsi.</li>
<li><strong>Giriş şlanqının süzgəcinin tutulması:</strong> Şlanqın maşına birləşdiyi yerdəki kiçik plastik setka qum və pasla tutulur. Pəncə ilə çıxarılıb yuyulmalıdır.</li>
<li><strong>Giriş elektro-maqnit klapanının yanması:</strong> Klapanın sarğısı sıradan çıxdıqda su yolunu aça bilmir.</li>
<li><strong>Qapı kilidinin (UBL) tam qapanmaması:</strong> Qapı bağlanmayıbsa, təhlükəsizlik məqsədilə su klapanına cərəyan verilmir.</li>
</ul>''',
    },
    {
        'bashliq': 'Paltaryuyan maşının qapısı kilidlənib açılmır — Təhlükəsiz açılma',
        'slug': 'paltaryuyan-qapisi-acilmir',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyanın Qapısı Açılmır? Təcili Açma Üsulları və Qapı Kilidi | Prousta.az',
        'seo_description': 'Yuma bitdi, amma qapı açılmır? Tutacaq qırıldıqda və ya kilid ilişdikdə qapını zədələmədən açmağın yolları.',
        'metn': '''<h2>Qapı niyə ilişib qalır?</h2>
<p>Yuma bitdikdən sonra kilid 2-3 dəqiqə ərzində avtomatik açılmalıdır. Açılmırsa, qapını zorla dartmaq qətiyyən olmaz — plastik tutacaq dərhal sınar.</p>

<h2>Nə üçün açılmır?</h2>
<ol>
<li>Maşının daxilində su qalıb (su tam boşalmayınca kilid açılmır).</li>
<li>Termik qapı kilidinin (UBL bimetal lövhəsi) soyumaması və ya ilişməsi.</li>
<li>Plastik dəstəyin daxili qarmağının qırılması.</li>
</ol>

<h2>Qapını sındırmadan necə açmaq olar?</h2>
<p><strong>İp üsulu:</strong> İncə və möhkəm ipi (və ya sintetik tilişkəni) qapı ilə gövdə arasındakı boşluğa keçirin və qıfıl dilinin istiqamətinə doğru dartın. Dil içəri basılacaq və qapı açılacaq. Maşında su varsa, əvvəlcə alt filtrdən suyu boşaltmağı unutmayın.</p>''',
    },
    {
        'bashliq': 'Paltaryuyan maşının altından su axır — Sızma yerinin tapılması',
        'slug': 'paltaryuyan-altindan-su-axidir',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyanın Altından Su Sızır? Qapı Manjeti və Boru Deşilməsi | Prousta.az',
        'seo_description': 'Paltaryuyan otağa su axıdır? Qapı rezin manjeti, toz qutusunun xortumu və çənin çatlaması diaqnostikası.',
        'metn': '''<h2>Paltaryuyanın su buraxması</h2>
<p>Döşəmədə su gölməçəsinin yaranması həm qonşuya su sızması, həm də elektrik vurma təhlükəsi yaradır. Dərhal maşını elektrikdən ayırın.</p>

<h2>Ən çox sızan hissələr:</h2>
<ul>
<li><strong>Qapı rezin manjetinin yırtılması:</strong> Paltarın zənciri və ya yad cisim rezin manjeti deşir və qabaqdan su süzülür.</li>
<li><strong>Yuyucu toz qutusunun borusunun tıxanması:</strong> Yuyucu toz daşlaşaraq borunu bağlayır və su qutudan çölə daşır.</li>
<li><strong>Drenaj pompasının korpusu və ya xortumunun deşilməsi.</strong></li>
<li><strong>Giriş şlanqının arxadan boşalması.</strong></li>
</ul>''',
    },
    {
        'bashliq': 'Paltaryuyan yuyucu tozu və yumşaldıcını qutudan götürmür',
        'slug': 'paltaryuyan-tozu-goturmur',
        'kategori_slug': 'paltaryuyan-ustasi',
        'seo_title': 'Paltaryuyan Niyə Tozu Götürmür? Toz Qutusunun Təmizlənməsi | Prousta.az',
        'seo_description': 'Yuma bitir, amma poroşok və yumşaldıcı ləyəndə qalır? Su püskürdücü forsunka və klapan nasazlıqları.',
        'metn': '''<h2>Yuyucu toz niyə yuvada qalır?</h2>
<p>Yuma bitdikdən sonra bölmədə yuyucu tozun daş kimi qalması və ya lenorun (yumşaldıcının) toxunulmaz qalması paltarların keyfiyyətsiz yuyulmasına səbəb olur.</p>

<h2>Səbəblər:</h2>
<ul>
<li>Şəbəkədə su təzyiqinin çox zəif olması — su şırnağı tozu yuva boyu yuya bilmir.</li>
<li>Toz qutusunun yuxarı tavanındakı su püskürdən dəliklərin ərp və kirlə tutulması.</li>
<li>Yumşaldıcı bölməsinin sifon borusunun qurumuş qalıqlarla tıxanması.</li>
<li>İkitərəfli giriş klapanının ikinci bölməsinin açılmaması.</li>
</ul>
<p>Toz çəkməcəsini ortasındakı qapağa basaraq tam çıxarın, ilıq sirkəli su və diş fırçası ilə yuyub yerinə quraşdırın.</p>''',
    },

    # ---------------- QABYUYAN ----------------
    {
        'bashliq': 'Qabyuyan maşın qabları təmiz yumur və ağ ləkələr qoyur',
        'slug': 'qabyuyan-qablari-temiz-yumur',
        'kategori_slug': 'qabyuyan-ustasi',
        'seo_title': 'Qabyuyan Qabları Niyə Kirli Çıxarır? Ağ Ərp Ləkələri və Pər Tıxanması | Prousta.az',
        'seo_description': 'Qabyuyan qabları yaxşı yumur, stəkanlarda ləkə qalır? Duz tənzimlənməsi, süzgəc təmizliyi və fırlanan qolların təmiri.',
        'metn': '''<h2>Qabların çirkli qalmasının səbəbləri</h2>
<p>Qabyuyan maşından qabların üzərində yemək qalıqları, yağ təbəqəsi və ya mat ağ ərpli ləkələrlə çıxması cihazın funksiyasını itirməsi deməkdir.</p>

<h2>Əsas səbəblər:</h2>
<ol>
<li><strong>Fırlanan su pərlərinin (koromislo) deşiklərinin tutulması:</strong> Limon tumu, çəyirdək və ya qida qırıntıları pərin kiçik dəliklərini bağlayır və pər fırlanmır.</li>
<li><strong>Xüsusi regenerasiya duzunun (duzun) olmaması:</strong> Bakı suyunda duzsuz yuma şüşə qablarda ağ ərp ləkələri yaradır.</li>
<li><strong>Aşağı filtrin yağla örtülməsi:</strong> Çirkli su təkrar qabların üzərinə fırlanır.</li>
<li><strong>Qabların səhv yığılması:</strong> İri qazanlar pərin fırlanmasına mane olur və ya qablar bir-birini örtür.</li>
</ol>''',
    },
    {
        'bashliq': 'Qabyuyan maşında su qızmır — Soyuq su ilə yuma problemi',
        'slug': 'qabyuyan-suyu-qizdirmir',
        'kategori_slug': 'qabyuyan-ustasi',
        'seo_title': 'Qabyuyan Suyu Qızdırmır? Qızdırıcı Nasos (Ten) Nasazlığı | Prousta.az',
        'seo_description': 'Bosch, Siemens, Beko qabyuyan maşınlarında suyun qızmaması: İstilik nasosu təmiri və E09 xəta kodu.',
        'metn': '''<h2>Qabyuyan maşın soyuq su ilə yuyur</h2>
<p>Qabyuyan dövrü bitirdikdə qapını açanda içəridən buxar çıxmırsa, qablar soyuq və nəm qalırsa, maşında su qızdırılmır. Yağlar soyuq suda ərimədiyi üçün qablar çirkli qalır.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Qızdırıcı blokun (sirkulyasiya nasosu ilə inteqrasiya olunmuş ten) yanması:</strong> Müasir Bosch/Siemens maşınlarında <strong>E09 xətası</strong> məhz tenin sıradan çıxdığını göstərir.</li>
<li><strong>Temperatur sensorunun sıradan çıxması.</strong></li>
<li><strong>Elektron platada ten relesinin kontaktlarının yanması.</strong></li>
</ul>''',
    },
    {
        'bashliq': 'Qabyuyan maşında E15 / E4 daşma (AquaStop) xətası',
        'slug': 'qabyuyan-e4-e15-xetasi',
        'kategori_slug': 'qabyuyan-ustasi',
        'seo_title': 'Qabyuyan E15 və E4 Xətası Nədir? AquaStop Təhlükəsizlik Sistemi | Prousta.az',
        'seo_description': 'Qabyuyan maşın dayanmadan nasos işlədir və E15 xətası verir? Alt poddona su sızmasının səbəbləri və qurudulması.',
        'metn': '''<h2>E15 xətası nədir və nasos niyə dayanmır?</h2>
<p>Bosch və digər qabyuyanlarda <strong>E15 (və ya E4)</strong> təhlükəsizlik sisteminin (AquaStop) işə düşdüyünü bildirir. Maşının ən alt tənəkə altlığına su sızıb və oradakı penoplast üzgəc qalxaraq mikro-açarı sıxıb. Nəticədə maşın sönmür və durmadan drenaj pompasını işlədir.</p>

<h2>Haradan sızır?</h2>
<ul>
<li>Paslanmaz polad çənin küncündən (duz səbəbindən yaranan mikrodeşik).</li>
<li>Qapı altı rezin kipgəcdən.</li>
<li>Sirkulyasiya nasosunun rezin birləşməsindən.</li>
<li>Həddindən artıq köpüklənən yuyucu vasitə istifadəsi nəticəsində köpüyün alt qaba daşması.</li>
</ul>

<h2>Müvəqqəti həll:</h2>
<p>Cihazı şəbəkədən ayırın və maşını 45 dərəcə bucaq altında qabağa və ya arxaya əyərək alt qabdakı suyu yerə boşaldın. Lakin sızma səbəbi aradan qaldırılmasa, E15 bir neçə gündən sonra yenidən təkrarlanacaq.</p>''',
    },
    {
        'bashliq': 'Qabyuyan maşın yuyucu tableti açmır və əritmir',
        'slug': 'qabyuyan-tabletkani-eridmir',
        'kategori_slug': 'qabyuyan-ustasi',
        'seo_title': 'Qabyuyan Niyə Tabletkanı Əritmir? Dərman Qapağının Açılmaması | Prousta.az',
        'seo_description': 'Yuma bitir, amma tabletka bütöv qalır və ya qapaq açılmır? Dispenser mexanizmi və su təzyiqi problemləri.',
        'metn': '''<h2>Tabletka niyə bütöv qalır?</h2>
<p>Proqram tamamlandıqda yuyucu tabletin qutusunda toxunulmaz qalması və ya alt qabda yarı-ərimiş vəziyyətdə tapılması tez-tez baş verir.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Qabaq səbətdə böyük boşqabın qapağın qarşısını kəsməsi:</strong> Dispenser qapağı yay vasitəsilə sıçrayıb açıla bilmir.</li>
<li><strong>Dispenser aktivatorunun (solenoid və ya termo-rele) xarab olması:</strong> Platadan əmr gəlsə də qapağın mexanizmi dartılmır.</li>
<li><strong>Suyun qızmaması:</strong> Soyuq suda müasir bərk tabletlər əriyə bilmir.</li>
<li><strong>Üst pərin fırlanmaması:</strong> Dispenserin qapağına su şırnağı dəymir.</li>
</ul>''',
    },
    {
        'bashliq': 'Qabyuyan maşın yuduqdan sonra qabları qurutmur',
        'slug': 'qabyuyan-qurutmur',
        'kategori_slug': 'qabyuyan-ustasi',
        'seo_title': 'Qabyuyan Niyə Qurutmur? Yaş Qablar və Qurutma Fanı Nasazlığı | Prousta.az',
        'seo_description': 'Qabyuyandan çıxan qablar niyə nəm qalır? Parladıcı (rinse aid) çatışmazlığı, turbo qurutma və ten problemləri.',
        'metn': '''<h2>Qabların yaş qalması səbəbləri</h2>
<p>Qabyuyan yumanı bitirdikdə qablar quru və parıldayan olmalıdır. Əgər qabların üzərində su damcıları qalırsa, bu amilləri yoxlayın:</p>

<h2>Əsas səbəblər:</h2>
<ul>
<li><strong>Qabyuyan parıldadıcısının (rinse aid) bitməsi:</strong> Parladıcı suyun səthi gərilməsini azaldaraq damcıların sürüşüb axmasını təmin edir. İstifadə olunmadıqda qablar qurutmada nəm qalır.</li>
<li><strong>Plastik qabların çoxluğu:</strong> Plastik qablar istiliyi saxlamadığı üçün kondensasiyalı qurutmada quruması çətindir.</li>
<li><strong>Turbo qurutma fanının yanması:</strong> Aktiv havalandırma fanı olan modellərdə fan motoru sıradan çıxıb.</li>
<li><strong>Yuma sonunda qapının açılmaması.</strong></li>
</ul>''',
    },

    # ---------------- SOYUDUCU ----------------
    {
        'bashliq': 'Soyuducunun dondurucusu işləyir, amma alt kamera soyutmur',
        'slug': 'soyuducu-asagi-soyudur-yuxari-yox',
        'kategori_slug': 'soyuducu-ustasi',
        'seo_title': 'Soyuducunun Altı Niyə Soyutmur? Dondurucu Buzlayır, Alt İlıq Qalır | Prousta.az',
        'seo_description': 'No-Frost soyuducularda dondurucu buz bağlayır, aşağı hissə isə soyutmur? Defrost teni, hava damperi və fan motoru təmiri.',
        'metn': '''<h2>No-Frost soyuducularda ən məşhur nasazlıq</h2>
<p>İstifadəçilər tez-tez bildirir: <em>"Soyuducunun dondurucu kamerası buz kimidir, ətləri dondurur, amma aşağı soyuducu kamerada yeməklər xarab olur və istidir."</em> Bu, No-Frost sisteminin avtomatik don açma (defrost) sisteminin nasazlığından xəbər verir.</p>

<h2>Səbəb necə formalaşır?</h2>
<ol>
<li>Dondurucunun arxasında yerləşən buxarlandırıcı radiator hər gün donur və defrost teni vasitəsilə əridilməlidir.</li>
<li><strong>Defrost teni (qızdırıcı), bi-metal termostat və ya istilik qoruyucusu yandıqda</strong> buz ərimir və hava kanallarını tamamilə tıxayır.</li>
<li>Dondurucudakı soyuq havanı aşağı kameraya üfürən ventilyator və ya hava qapağı (damper) donmuş buzun içində sıxılıb qalır və aşağıya soyuq hava keçə bilmir.</li>
</ol>

<h2>Təcili addım:</h2>
<p>Soyuducunu elektrikdən ayırın, qapılarını tam açıq qoyaraq <strong>24-48 saat</strong> tam əriməsini gözləyin. Ərimədən sonra işə saldıqda alt kamera bir neçə gün normal soyudacaq, lakin defrost sistemi təmir olunmasa 1-2 həftəyə kanal yenidən buz bağlayacaq.</p>''',
    },
    {
        'bashliq': 'Soyuducunun motoru durmadan işləyir və sönmür',
        'slug': 'soyuducu-motor-durmadan-isleyir',
        'kategori_slug': 'soyuducu-ustasi',
        'seo_title': 'Soyuducunun Kompressoru Niyə Sönmür? Fasiləsiz İşləmə Səbəbləri | Prousta.az',
        'seo_description': 'Soyuducu fasiləsiz işləyir, motor həddindən artıq qızır? Freon sızması, termostat və qapı rezini problemləri.',
        'metn': '''<h2>Motorun sönməməsi nə üçün təhlükəlidir?</h2>
<p>Normalda soyuducu kompressoru 15-25 dəqiqə işləyib, tələb olunan temperatura çatdıqdan sonra 15-30 dəqiqə sönük qalmalıdır. Motor 24 saat fasiləsiz uğuldayırsa, tezliklə sarğıları yanıb sıradan çıxa bilər.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Freon qazının mikro-sızması:</strong> Qaz azaldığı üçün soyuducu təyin edilmiş dərəcəyə çata bilmir və kompressor istiliyi endirmək üçün durmadan çalışır.</li>
<li><strong>Qapı rezinlərinin (maqnit contanın) aralı qalması:</strong> Otağın isti havası fasiləsiz içəri daxil olur.</li>
<li><strong>Termostatın və ya elektron temperatur sensorunun yapışması:</strong> Plataya söndürmə əmri göndərmir.</li>
<li><strong>Kondensator barmaqlığının qalın tozla örtülməsi:</strong> Motor istiliyi bayıra ata bilmir.</li>
</ul>''',
    },
    {
        'bashliq': 'Soyuducudan qəribə səslər gəlir — Qaz qaynaması, tıqqıltı və uğultu',
        'slug': 'soyuducu-arxasindan-ses-gelir',
        'kategori_slug': 'soyuducu-ustasi',
        'seo_title': 'Soyuducudan Gələn Səslər Nədir? Qaz Qaynaması və Titrəyiş Səsi | Prousta.az',
        'seo_description': 'Soyuducu şaqqıldayır, qaz qaynama səsi gəlir? Hansı səslər normaldır, hansılar isə kompressor nasazlığıdır?',
        'metn': '''<h2>Hansı səslər normaldır, hansılar təhlükəlidir?</h2>
<p>Müasir soyuducularda (xüsusilə R600a izobutan freonla işləyənlərdə) bəzi səslər təbii qəbul edilir, lakin mexaniki cingiltilər xəbərdarlıq siqnalıdır.</p>

<h2>Səslərin təhlili:</h2>
<ul>
<li><strong>Şırıltı və qaz qaynama səsi:</strong> Borularda maye freonun buxarlanaraq hərəkət etməsidir — tamamilə normaldır.</li>
<li><strong>Plastik şaqqıltısı:</strong> Temperatur dəyişəndə daxili korpusun genişlənib-yığılması — normaldır.</li>
<li><strong>Kompressor işə düşəndə və sönəndə bərk zərbə səsi:</strong> Kompressorun daxili amortizator yayları qopub və porşen gövdəyə dəyir.</li>
<li><strong>Cırıldayan ventilyator səsi:</strong> No-Frost fanının pəri ətrafda yığılmış buza sürtünür.</li>
</ul>''',
    },
    {
        'bashliq': 'No-Frost soyuducunun meyvə qutusunun altına su yığılır',
        'slug': 'soyuducu-icinde-su-yigilir',
        'kategori_slug': 'soyuducu-ustasi',
        'seo_title': 'Soyuducunun İçinə Niyə Su Yığılır? Drenaj Dəliyi Təmizlənməsi | Prousta.az',
        'seo_description': 'Soyuducunun alt rəfinə və tərəvəz qutusunun altına su axır? Drenaj borusunun tutulması və asan açılma qaydası.',
        'metn': '''<h2>Soyuducunun daxilində gölməçə yaranması</h2>
<p>Soyuducunun ən aşağı şüşə rəfində və tərəvəz yeşiklərinin altında daimi su toplanması daxili drenaj çıxışının tıxandığını bildirir.</p>

<h2>Necə baş verir?</h2>
<p>Ərimə zamanı yaranan kondensat arxa divardakı balaca novdan keçərək arxadakı mühərrikin üzərindəki qaba axmalıdır. Qida qırıntıları, toz və ya kif bu kiçik nov dəliyini bağlayanda su daxildə qalır və aşağıya süzülür.</p>

<h2>Həlli:</h2>
<p>Arxa divarın aşağı hissəsindəki dəliyi tapın. Xüsusi plastik təmizləyici mil və ya şprisə doldurulmuş ilıq su vasitəsilə dəliyə təzyiqlə su vurun. Su arxadakı qaba rahat axana qədər prosesi təkrarlayın.</p>''',
    },
    {
        'bashliq': 'No-Frost soyuducu niyə qar və buz bağlayır?',
        'slug': 'soyuducu-buz-baglayir-no-frost',
        'kategori_slug': 'soyuducu-ustasi',
        'seo_title': 'No-Frost Soyuducu Niyə Buz Bağlayır? Səbəbləri və Diaqnostika | Prousta.az',
        'seo_description': 'Qarsız işləməli olan No-Frost soyuducunun divarları qarla örtülür? Qapı kipgəci və havalandırma nasazlıqları.',
        'metn': '''<h2>No-Frost soyuducuda buz olmalıdırmı?</h2>
<p>"No-Frost" texnologiyasının əsas üstünlüyü daxildə görünən qarın olmamasıdır. Əgər divarlarda qalın qar və qrov təbəqəsi yaranırsa, sistemin iş rejimi pozulub.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Qapı rezinlərinin köhnəlməsi və yırtılması:</strong> Otaqdakı nəm hava kamerasının içinə sovrulur və dərhal qara çevrilir.</li>
<li><strong>Qapının uzun müddət açıq qalması və ya qapı bağlayıcısının əyilməsi.</strong></li>
<li><strong>Daxilə qaynar qazan və sulu yeməklərin üstüaçıq qoyulması:</strong> Buxar dərhal divarlara hopur.</li>
<li><strong>Defrost sensorunun sıradan çıxması.</strong></li>
</ul>''',
    },
    {
        'bashliq': 'Soyuducu qapısının rezinləri (maqnit conta) yapışmır və hava buraxır',
        'slug': 'soyuducu-qapisi-kip-baglanmir',
        'kategori_slug': 'soyuducu-ustasi',
        'seo_title': 'Soyuducunun Qapı Rezini Yapışmır? Qapı Contasının Bərpası və Dəyişdirilməsi | Prousta.az',
        'seo_description': 'Soyuducu qapısı öz-özünə açılır və hava buraxır? Maqnit rezinlərinin isti su və fenlə bərpası qaydası.',
        'metn': '''<h2>Qapı kip bağlanmadıqda nə baş verir?</h2>
<p>Soyuducu qapısının rezini köhnəldikdə və ya deformasiyaya uğradıqda maqnit gövdəyə yapışmır. Bu zaman motor sönmür, elektrik xərci ikiqat artır və yeməklər tez xarab olur.</p>

<h2>Evdə bərpa üsulu (Fenlə qızdırma):</h2>
<ol>
<li>Qapı rezinlərini kağız pul (manat) ilə yoxlayın: Pulu qapı ilə gövdə arasına qoyub bağlayın. Əgər pul müqavimətsiz rahat çıxırsa, həmin hissədə aralıq var.</li>
<li>Rezinin əyilmiş və sıxılmış yerinə saç feni ilə orta temperaturda isti hava vurun.</li>
<li>Rezin qızıb yumşaldıqda əlinizlə dartaraq düzəldin və qapını bağlayaraq soyuyana qədər bağlı saxlayın.</li>
<li>Rezin cırılıb və ya maqnit xassəsini tam itiribsə, yenisi ilə əvəzlənməlidir.</li>
</ol>''',
    },

    # ---------------- SANTEXNİK & KANALİZASİYA ----------------
    {
        'bashliq': 'Kranlar bağlı olduğu halda su sayğacı niyə fırlanır?',
        'slug': 'su-saygaci-firlanir-su-islenmir',
        'kategori_slug': 'santexnik',
        'seo_title': 'Kranlar Bağlıdır, Amma Su Sayğacı Fırlanır? Gizli Su Sızması | Prousta.az',
        'seo_description': 'Evdə heç kim su işlətmir, lakin sayğac fırlanır? Unitaz bakın sızması, divar içi boru çatı və təzyiq klapanı yoxlanışı.',
        'metn': '''<h2>Bütün kranlar bağlıdır, amma sayğac yazır?</h2>
<p>Mənzildə və ya həyət evində heç bir kran açıq olmadığı halda su sayğacının pəri asta-asta fırlanırsa, bu evdə <strong>gizli su itkisinin</strong> olduğunu göstərir. Bu hal həm yüksək su puluna, həm də qonşuların tavanının nəmlənməsinə səbəb olur.</p>

<h2>İlk növbədə hara baxmalı?</h2>
<ol>
<li><strong>Unitazın baçoku (su çəni):</strong> Ən çox rast gəlinən səbəbdir. Armaturun rezin membranından unitazın içinə nazik, güclə görünən su axır. Unitazın daxilinə quru tualet kağızı yapışdırın — kağız dərhal islanarsa, səbəbkar baçokdur.</li>
<li><strong>Kombi və ya boylerin 3 bar təhlükəsizlik klapanı:</strong> Kanalizasiyaya birləşdirilmiş drenaj borusundan su axıb gedir.</li>
<li><strong>İçməli su filtrinin tullantı (drenaj) klapanı:</strong> Avtomatik klapan xarab olduqda membran suyu durmadan kanalizasiyaya axıdır.</li>
<li><strong>Divar və ya döşəmə altındakı borularda çatlar:</strong> Gizli santexnika borusu deşilib.</li>
</ol>''',
    },
    {
        'bashliq': 'Su təzyiq tənzimləyicisi (reduktor) niyə sıradan çıxır?',
        'slug': 'tezyiq-reduktoru-nasazligi',
        'kategori_slug': 'santexnik',
        'seo_title': 'Su Təzyiq Reduktoru Nasazlıqları: Yüksək Təzyiq və Tənzimləmə | Prousta.az',
        'seo_description': 'Mənzildə su reduktoru su buraxmır və ya təzyiqi saxlamır? Reduktorun quruluşu, təmiri və filtr təmizliyi.',
        'metn': '''<h2>Su reduktoru nə üçün vacibdir?</h2>
<p>Bakıdakı çoxmərtəbəli binalarda şəhər xəttindən gələn suyun təzyiqi 6-8 bara qədər yüksələ bilər. Su reduktoru bu təzyiqi təhlükəsiz <strong>3-3.5 bara</strong> endirərək kombini, filtrləri və kranları partlamaqdan qoruyur.</p>

<h2>Reduktorun nasazlıq əlamətləri:</h2>
<ul>
<li>Kranı açanda su əvvəlcə güclü fışqırır, sonra dərhal zəifləyir.</li>
<li>Reduktorun manometri 6-7 barı göstərir və təzyiqi endirmir (membran yırtılıb).</li>
<li>Kranlardan su ümumiyyətlə çox zəif axır (reduktorun daxili setkası qumla tutulub).</li>
</ul>''',
    },
    {
        'bashliq': 'Hidrofor su nasosu su açılmadan öz-özünə işə düşür',
        'slug': 'gidrofor-su-nasosu-tez-tez-iseyir',
        'kategori_slug': 'santexnik',
        'seo_title': 'Hidrofor Niyə Öz-özünə İşə Düşür? Qayıdış Klapanı və Membran Nasazlığı | Prousta.az',
        'seo_description': 'Su nasosu kranlar bağlı olanda da hər 5 dəqiqədən bir vurur? Çek-valf, təzyiq relesi və hidrofor qabının təmiri.',
        'metn': '''<h2>Hidrofor niyə qəfil qoşulur və sönür?</h2>
<p>Həyət evlərində və binalarda quraşdırılan hidrofor nasosunun su istifadə edilmədiyi vaxtda saniyəlik işə düşüb sönməsi ("təzyiq itkisi") ciddi narahatlıq yaradır.</p>

<h2>Səbəblər:</h2>
<ol>
<li><strong>Əks-klapanın (çek-valf / obratnı klapan) sıradan çıxması:</strong> Nasos suyu vurduqdan sonra klapan kip bağlamır və su təkrar çənə qayıdır, təzyiq düşdüyü üçün rele nasosu yenidən işə salır.</li>
<li><strong>Hidrofor çəninin daxili rezin membranın deşilməsi:</strong> Çəndə hava qalmadıqda təzyiq kompensasiya olunmur və hər damcı itkisində nasos işə düşür.</li>
<li><strong>Sistemdə gizli mikro-sızma (unitaz baçoku və s.).</strong></li>
<li><strong>Avtomatik idarəetmə platasının (press-kontrol) elektron xətası.</strong></li>
</ol>''',
    },
    {
        'bashliq': 'Kanalizasiya borusu donub — Qışda xarici xətlərin açılması',
        'slug': 'kanalizasiya-borusu-donub',
        'kategori_slug': 'kanalizasiya-ustasi',
        'seo_title': 'Kanalizasiya Borusu Donduqda Nə Etməli? Donmuş Boruların Açılması | Prousta.az',
        'seo_description': 'Şaxtada həyət və ya bina kanalizasiya borusu donub? Təhlükəsiz isti su və buxar üsulları ilə buzun əridilməsi.',
        'metn': '''<h2>Kanalizasiya boruları niyə donur?</h2>
<p>Kanalizasiya suları isti olsa da, boru torpağın donma dərinliyindən yuxarı basdırıldıqda və ya maillik düzgün verilməyib su boruda durğun qaldıqda şaxtada buz tıxacı yarana bilər.</p>

<h2>Buzu necə əritmək olar?</h2>
<ul>
<li><strong>Qaynar duzlu su:</strong> Güclü qatılıqlı qaynar duz məhlulu hazırlayıb boruya tökün (duz buzun ərimə temperaturunu aşağı salır).</li>
<li><strong>İçəridən şlanqla qaynar su vurmaq:</strong> Kanalizasiya borusunun içinə elastik nazik şlanq itələyərək buz tıxacına çatdırın və təzyiqlə qaynar su verin.</li>
<li>Qətiyyən xaricdən blowtorch (alov lampası) ilə plastik borunu qızdırmayın, boru deformasiyaya uğrayıb partlayar.</li>
</ul>''',
    },
    {
        'bashliq': 'Mətbəx moykasının altındakı qofra və sifon su damladır',
        'slug': 'moyka-sifonu-damizdirir',
        'kategori_slug': 'santexnik',
        'seo_title': 'Moyka Sifonu Niyə Su Buraxır? Qofra Dəyişdirilməsi və Birləşmə Təmiri | Prousta.az',
        'seo_description': 'Mətbəx şkafının içinə su damır? Qofra boru, rezin contaların köhnəlməsi və sifonun düzgün yığılması bələdçisi.',
        'metn': '''<h2>Mətbəx şkafında nəm və su sızması</h2>
<p>Qab yuyarkən moykanın altındakı dolabın içinə su süzülməsi gigiyenik baxımdan ziyanlıdır və mebelin şişib sıradan çıxmasına gətirib çıxarır.</p>

<h2>Səbəblər və Həlli:</h2>
<ul>
<li><strong>Qofra borusunun qatlanması və ya deşilməsi:</strong> Ucuz elastik qofra boruları qaynar sudan kövrəkləşir və qırılır.</li>
<li><strong>Sifonun yivli birləşmələrindəki rezin kipgəclərin (prokladka) çürüməsi:</strong> Sifon sökülməli, köhnə contalar silikonlu yeniləri ilə əvəzlənməlidir.</li>
<li><strong>Moyka boğazının boşalması:</strong> Paslanmaz moyka ilə sifonun metal qəfəsini birləşdirən mərkəzi vint boşalır. İri vintaçanla bərkidilməlidir.</li>
</ul>''',
    },
    {
        'bashliq': 'Cakkuzi və hidromasajlı vanna işləmir — Forsunkaların təmizlənməsi',
        'slug': 'jakuzi-hidromasaj-islemir',
        'kategori_slug': 'santexnik',
        'seo_title': 'Cakkuzi Hidromasaj Niyə İşləmir? Motor və Forsunka Təmiri | Prousta.az',
        'seo_description': 'Cakkuzi vannanın su şırnaqları zəif vurur və ya motor qoşulmur? Pnevmo-düymə, ərp təmizlənməsi və nasos diaqnostikası.',
        'metn': '''<h2>Cakkuzi masaj sistemi niyə zəifləyir?</h2>
<p>Hidromasajlı vannalar vaxtaşırı profilaktika tələb edir. Əgər forsunkalardan hava və su gəlmirsə və ya su qəhvəyi çirklə gəlirsə:</p>

<h2>Əsas nasazlıqlar:</h2>
<ol>
<li><strong>Pnevmatik işəsalma düyməsinin borusu çıxıb:</strong> Düymə basılır amma hava impulsunu motor relesinə çatdıra bilmir.</li>
<li><strong>Forsunkaların ərplə tutulması:</strong> Vannaya xüsusi hidromasaj təmizləyici kimyəvi vasitə tökülərək 20 dəqiqə dövriyyə etdirilməlidir.</li>
<li><strong>Su səviyyə sensorunun çirklənməsi:</strong> Vannada su az olduqda motorun yanmaması üçün sensor işə düşməyə icazə vermir.</li>
</ol>''',
    },
    {
        'bashliq': 'Gizli su sızmasını tapmaq üsulları — Termovizor və akustik axtarış',
        'slug': 'gizli-su-sizmasi-axtarisi',
        'kategori_slug': 'su-sizma',
        'seo_title': 'Divar İçi Gizli Su Sızması Necə Tapılır? Dağıntısız Cihazla Axtarış | Prousta.az',
        'seo_description': 'Qonşunun tavanı nəmlənir, amma evdə boru görünmür? Termovizor və ultrasəs korrelyatorla nöqtəvi su sızması tərifi.',
        'metn': '''<h2>Kafel və döşəməni dağıtmadan sızmanı necə tapmaq olar?</h2>
<p>Müasir mənzillərdə bütün borular kafel, divar və parket altında gizlədilir. Sızma baş verdikdə bütün evi sökmək böyük maliyyə itkisidir.</p>

<h2>Peşəkar cihazlarla diaqnostika metodları:</h2>
<ul>
<li><strong>Termovizor (İstilik kamerası):</strong> İsti su boruları və kombi istipol sistemlərində sızan suyun yayılma nöqtəsini millimetrinə qədər infraqırmızı rənglərlə göstərir.</li>
<li><strong>Akustik dinləmə cihazı (Geofon):</strong> Təzyiqli soyuq su borularında mikrodeşikdən çıxan suyun yaratdığı ultrasəs dalğalarını xüsusi qulaqlıq vasitəsilə təyin edir.</li>
<li><strong>Rütubətölçən (Hiqrometr):</strong> Beton daxilində nəmliyin ən yüksək olduğu mərkəz nöqtəsini aşkarlayır.</li>
</ul>''',
    },

    # ---------------- PİTİMİNUTKA & ARİSTON ----------------
    {
        'bashliq': 'Pitiminutka xodlanmır, batareya qığılcım vurmur — Səbəbi və həlli',
        'slug': 'pitiminutka-yanmir-qigildim-vurmur',
        'kategori_slug': 'pitiminutka-ustasi',
        'seo_title': 'Pitiminutka Niyə Yanmır? Çaxmaq Vurmur və Qaz Açılmır | Prousta.az',
        'seo_description': 'Qaz su qızdırıcısı (pitiminutka) krantı açanda işə düşmür? Batareya, su membranı və mikroyandırıcı təmiri.',
        'metn': '''<h2>Kranı açanda pitiminutka niyə reaksiya vermir?</h2>
<p>Qaz kolonkasında (pitiminutka) isti su kranını açdıqda çırt-çırt qığılcım səsi gəlmirsə və alov yanmırsa, səbəb su və ya elektrik blokundadır.</p>

<h2>Yoxlanmalı 4 vacib nöqtə:</h2>
<ol>
<li><strong>Batareyaların enerjisinin tükənməsi:</strong> Ən sadə və ən çox rast gəlinən səbəb. Cihazın altındakı iri "D" tipli batareyalar keyfiyyətli qələvi (alkaline) batareyalarla əvəz olunmalıdır.</li>
<li><strong>Su reduktorunun rezin membranın cırılması:</strong> Su axarkən membranı itələyib qaz klapanını və mikro-düyməni aça bilmir. Membran dəyişdirilməlidir.</li>
<li><strong>Mikro-sviç (balaca elektron düymə) kontaktlarının paslanması:</strong> Əl ilə itələdikdə qığılcım vurursa, deməli problem su blokunun milindədir.</li>
<li><strong>Mənzildə su təzyiqinin normadan aşağı olması.</strong></li>
</ol>''',
    },
    {
        'bashliq': 'Pitiminutka yandıqdan 10-15 saniyə sonra qəfil sönür',
        'slug': 'pitiminutka-tez-sonur',
        'kategori_slug': 'pitiminutka-ustasi',
        'seo_title': 'Pitiminutka Niyə Tez Sönür? Termopara və Baca Sensoru Problemi | Prousta.az',
        'seo_description': 'Pitiminutka yanır, amma bir azdan sönür? Dəm qazı sensoru, termopara və zəif çəkim nasazlıqlarının izahı.',
        'metn': '''<h2>Pitiminutkanın alovunun dərhal kəsilməsi</h2>
<p>Cihaz işə düşür, lakin bir neçə saniyə sonra qaz kəsilir və alov sönür. Bu halda ardıcıl cəhdlər etmək qaz dolmasına səbəb ola bilər.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Bacadakı çəkimin zəif olması (Dəm qazı təhlükəsizlik relesi):</strong> Bacada hava çəkmirsə, dəm qazı sensoru qızaraq təhlükəsizlik məqsədilə qazı dərhal bağlayır.</li>
<li><strong>İonizasiya elektrodunun (və ya termoparanın) alovdan kənarda qalması:</strong> Sensor alovun istisini hiss etmir və sistem qəza rejiminə keçir.</li>
<li><strong>Qaz batareyasının zəifləməsi:</strong> Qığılcım vurmağa gücü çatsa da, qaz maqnit valfını açıq saxlamağa cərəyanı çatmır.</li>
</ul>''',
    },
    {
        'bashliq': 'Pitiminutkanın radiatoru (qazanı) deşilib su sızdırır — Qaynaq və təmiri',
        'slug': 'pitiminutka-radiatoru-desilib',
        'kategori_slug': 'pitiminutka-ustasi',
        'seo_title': 'Pitiminutkanın Qazanı Niyə Deşilir? Mis Radiator Qaynağı | Prousta.az',
        'seo_description': 'Pitiminutkadan su damır? Mis radiator borularının lehimlənməsi, korroziya səbəbləri və bərpa xidməti.',
        'metn': '''<h2>Radiatordan su damcılaması</h2>
<p>Pitiminutkanın altından şorhaşor su axması daxildəki mis istilik dəyişdiricisinin (radiator borusunun) deşildiyini göstərir.</p>

<h2>Deşilmə səbəbləri:</h2>
<ul>
<li>Keyfiyyətsiz nazik divarlı mis ərintisi.</li>
<li>Aşağı temperaturda balkonda donma nəticəsində borunun partlaması.</li>
<li>Həddindən artıq yüksək qaz alovu ilə qazanın qaynadılması.</li>
</ul>
<p>Mis borular xüsusi gümüş lehim və qaz lampası vasitəsilə etibarlı şəkildə qaynaq oluna bilər. Lakin əgər boru tam çürüyübsə, radiator yenisi ilə əvəzlənməlidir.</p>''',
    },
    {
        'bashliq': 'Ariston su qızdırıcısı gövdəyə və ya suya cərəyan (tok) vurur',
        'slug': 'ariston-boyler-isiq-vurur',
        'kategori_slug': 'ariston-ustasi',
        'seo_title': 'Ariston (Boyler) Tok Vurur? Həyati Təhlükə! Ten Deşilməsi və Torpaqlama | Prousta.az',
        'seo_description': 'Ariston işləyəndə su və ya kran adamı vurur? Təcili addımlar: Ten partlaması, UZO qoruyucusu və torpaqlama mütləqiyyəti.',
        'metn': '''<h2>DİQQƏT: HƏYATİ TƏHLÜKƏ!</h2>
<p>Əgər kranı açanda su adamı çimdikləyirsə və ya Aristonun gövdəsinə toxunduqda elektrik cərəyanı hiss olunursa, <strong>dərhal Aristonun avtomatını şitdən söndürün və cihazı elektrikdən ayırın!</strong></p>

<h2>Niyə elektrik suya keçir?</h2>
<ol>
<li><strong>Tenin metal qabığının partlaması:</strong> Ərp qatından həddən artıq qızan ten deşilir və 220V gərginlik birbaşa suyun daxilinə keçir.</li>
<li><strong>Mənzildə torpaqlama (yerlənmə) xəttinin olmaması:</strong> Normalda cərəyan torpağa axmalı və avtomat atmalı idi.</li>
<li><strong>Diferensial avtomatın (UZO) quraşdırılmaması.</strong></li>
</ol>
<p>Bu nasazlıqda ten təcili dəyişdirilməli və xəttə mütləq qalıq cərəyan rölesi (UZO) qoyulmalıdır.</p>''',
    },
    {
        'bashliq': 'Aristonun qoruyucu klapanından (obratnı) daimi su axır',
        'slug': 'boyler-qoruyucu-klapan-su-axidir',
        'kategori_slug': 'ariston-ustasi',
        'seo_title': 'Ariston Qoruyucu Klapanından Su Axır? Normal Hal və Nasazlıq | Prousta.az',
        'seo_description': 'Su qızdırıcısının altındakı balaca klapandan su damır? Yüksək şəbəkə təzyiqi və klapan nasazlığının fərqi.',
        'metn': '''<h2>Qoruyucu klapan nə üçündür?</h2>
<p>Aristonun soyuq su girişinə quraşdırılan yaylı klapan iki funksiyanı yerinə yetirir: suyun geri qayıtmasının qarşısını alır və su qızarkən genişlənən artıq təzyiqi damcı şəklində çölə buraxır.</p>

<h2>Nə vaxt problem sayılır?</h2>
<ul>
<li><strong>Su qızarkən bir neçə damcı axması:</strong> Tamamilə normal fiziki prosesdir. Klapanın burnuna nazik şəffaf boru taxılaraq kanalizasiyaya yönəldilməlidir.</li>
<li><strong>Ariston sönük olanda da şırnaqla su axması:</strong> Bu nasazlıqdır. Səbəb ya binada su təzyiqinin 6 bardan yuxarı olmasıdır (reduktor tələb olunur), ya da klapanın daxili yayı zibillənərək ilişib.</li>
</ul>''',
    },

    # ---------------- ELEKTRİK ----------------
    {
        'bashliq': 'Elektrik şitində avtomat şalter niyə tez-tez atır?',
        'slug': 'avtomat-tez-tez-atir',
        'kategori_slug': 'elektrik',
        'seo_title': 'Elektrik Avtomatı Niyə Atır? Həddindən Artıq Yüklənmə və Qısa Qapanma | Prousta.az',
        'seo_description': 'Evdə elektrik avtomatı qəfil düşür? Güclü cihazlar, naqil qızması və qısa qapanmanın aradan qaldırılması.',
        'metn': '''<h2>Avtomat şalter niyə dövrəni ayırır?</h2>
<p>Avtomat şalterin (avtomatın) atması naqilləri yanğından, mənzili isə qəzadan qoruyan əsas təhlükəsizlik tədbiridir.</p>

<h2>Avtomatın atmasının 3 əsas səbəbi:</h2>
<ol>
<li><strong>Xəttin həddindən artıq yüklənməsi:</strong> Eyni xəttə eyni vaxtda paltaryuyan, ütü, çaynik və kondisioner qoşulduqda cərəyan şiddəti avtomatın nominalını (məs. 16 Amper) aşır və termik qoruyucu xətti söndürür.</li>
<li><strong>Qısa qapanma:</strong> Faza ilə sıfır naqili birbaşa toxunur. Bu zaman avtomat dərhal saniyənin onda birində "tık" edərək atır və qaldırdıqda yenidən düşür.</li>
<li><strong>Avtomatın özünün daxili kontaktlarının yanması və köhnəlməsi:</strong> Yiv boltları boşaldıqda avtomat qızır və nominaldan tez atır.</li>
</ol>''',
    },
    {
        'bashliq': 'UZO (Qalıq cərəyan rölesi) niyə atır? Sızma cərəyanı axtarışı',
        'slug': 'uzo-diferensial-avtomat-atir',
        'kategori_slug': 'elektrik',
        'seo_title': 'UZO Niyə Atır? Diferensial Avtomat Sızma Xətası və Təmiri | Prousta.az',
        'seo_description': 'Evdə UZO (diferensial avtomat) qaldırılmır? Torpağa cərəyan sızması, cihaz gövdəsində qəza və xətlərin yoxlanması.',
        'metn': '''<h2>UZO ilə sadə avtomatın fərqi nədir?</h2>
<p>Sadə avtomat naqilləri qoruyur, <strong>UZO (Qalıq Cərəyan Rölesi)</strong> isə insan həyatını elektrik vurmasından qoruyur. İnsan cərəyan keçirən hissəyə toxunduqda və ya cihazın daxilində elektrik gövdəyə sızdıqda (30 milliAmper fərqdə) UZO dərhal atır.</p>

<h2>UZO atdıqda nasaz cihazı necə tapmaq olar?</h2>
<ol>
<li>UZO-nun altındakı bütün kiçik avtomatları aşağı endirin.</li>
<li>UZO-nu yuxarı qaldırın.</li>
<li>Kiçik avtomatları bir-bir yuxarı qaldırın. Hansı avtomatı qaldıranda UZO atırsa, problem məhz həmin otağın və ya həmin cihazın xəttindədir.</li>
<li>Həmin xətdəki bütün cihazları (soyuducu, kombi, paltaryuyan) rozetkadan çıxarıb tək-tək yoxlayın.</li>
</ol>''',
    },
    {
        'bashliq': 'Rozetkadan yanıq iyi gəlir, qığılcım çıxır və ya əriyir',
        'slug': 'rozetka-eriyir-qigilcim-alir',
        'kategori_slug': 'elektrik',
        'seo_title': 'Rozetka Niyə Əriyir və Qığılcım Verir? Yanğın Təhlükəsi və Təmiri | Prousta.az',
        'seo_description': 'Rozetkadan tüstü və qoxu çıxır? Boş kontaktlar, həddindən artıq güc və təhlükəsiz rozetka dəyişdirilməsi qaydaları.',
        'metn': '''<h2>Əriyən rozetka — yanğın riskidir!</h2>
<p>Rozetkanın plastik qapağının qaralması, vilkanı çıxaranda uclarının isti olması və ya içərisindən cızıltı səsinin gəlməsi dərhal müdaxilə tələb edən qəza vəziyyətidir.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Kontakt sıxaclarının boşalması:</strong> Naqili tutan vint boşaldıqda keçid müqaviməti kəskin artır və nöqtəvi qızma nəticəsində plastik əriyir.</li>
<li><strong>Alüminium və mis naqillərin birbaşa burulması:</strong> Qalvanik cütlük yaranır, naqil oksidləşir və qızır.</li>
<li><strong>Ucuz üçlük (troyik) və uzadıcıların istifadəsi:</strong> Yüksək vatlı qızdırıcılar üçün nəzərdə tutulmayıb.</li>
</ul>''',
    },
    {
        'bashliq': 'Evdə işıqlar titrəyir və yanıb-sönür — Gərginlik dalğalanması',
        'slug': 'evde-isiqlar-titreyir',
        'kategori_slug': 'elektrik',
        'seo_title': 'Evdə Lampalar Niyə Titrəyir? Gərginlik Düşməsi və Sıfır Kontaktı | Prousta.az',
        'seo_description': 'Evdə işıqlar yanıb-sönür, cihazlar qəribə işləyir? Sıfır naqilinin yanması, transformator zəifliyi və stabilizator seçimi.',
        'metn': '''<h2>İşıqların öləziməsi və titrəməsi</h2>
<p>Otaqdakı LED və ya közərmə lampalarının qəfil parlaqlaşıb, sonra zəifləməsi məişət texnikasının (xüsusilə soyuducu və televizorların ana platalarının) sıradan çıxmasına səbəb ola bilər.</p>

<h2>Əsas təhlükə: Sıfırın (Nol) qopması</h2>
<p>Əgər bütün binada və ya mənzildə sıfır naqili zəifləyibsə, 220V yerinə xəttə 380V qədər yüksək gərginlik sıçraya bilər. Bu zaman evdəki bütün elektronika eyni anda yanar.</p>

<h2>Nə etməli?</h2>
<p>Multimetr ilə rozetkadakı gərginliyi ölçün. Gərginlik 200V-dan aşağı və ya 240V-dan yuxarı dalğalanırsa, mənzilə ümumi gərginlik tənzimləyicisi (stabilizator) və ya rəqəmsal gərginlik relesi quraşdırılmalıdır.</p>''',
    },
    {
        'bashliq': 'Gərginlik qoruyucu rele xətaları — Bakıda gərginliyin düşməsi',
        'slug': 'voltaj-qoruyucu-rele-xetalari',
        'kategori_slug': 'elektrik',
        'seo_title': 'Gərginlik Relesi Niyə İşığı Kəsir? Bakıda Aşağı Voltaj Problemi | Prousta.az',
        'seo_description': 'Şitdəki rəqəmsal rele qırmızı yanır və cərəyanı kəsir? Voltaj hədlərinin sazlanması və qoruyucu rele quraşdırılması.',
        'metn': '''<h2>Rəqəmsal gərginlik relesi nə üçün sönür?</h2>
<p>Müasir elektrik şitlərində məişət texnikasını qorumaq üçün Zubr, DigiTOP kimi rəqəmsal voltaj releləri qoyulur. Rele gərginliyi kəsirsə, deməli şəbəkədə gərginlik təyin edilmiş təhlükəsizlik hədlərindən çıxıb.</p>

<h2>Standart düzgün parametrlər:</h2>
<ul>
<li><strong>Aşağı hədd:</strong> 180V - 190V (aşağı düşərsə kombi və soyuducu motoru yana bilər).</li>
<li><strong>Yuxarı hədd:</strong> 245V - 250V (yüksək olarsa plata kondensatorları partlayır).</li>
<li><strong>Gecikmə taymeri (Delay):</strong> Ən azı 180-300 saniyə (kompressorlu cihazların qaz təzyiqi bərabərləşmədən dərhal qoşulmaması üçün).</li>
</ul>''',
    },

    # ---------------- PLASTİK QAPI-PƏNCƏRƏ & MEBEL ----------------
    {
        'bashliq': 'Plastik pəncərədən fit səsi və soyuq külək keçir — Qış rejimi və rezinlər',
        'slug': 'plastik-pencere-kulek-buraxir',
        'kategori_slug': 'plastik-qapi-pencere',
        'seo_title': 'Plastik Pəncərədən Külək Niyə Əsir? Pəncərənin Qış Rejiminə Keçirilməsi | Prousta.az',
        'seo_description': 'Bağlı pəncərədən soyuq hava və fit səsi gəlir? Eksentriklərin qış rejiminə tənzimlənməsi və rezin fitillərin dəyişdirilməsi.',
        'metn': '''<h2>Bağlı pəncərədən otağa niyə soyuq daxil olur?</h2>
<p>Bakının güclü xəzri küləklərində plastik pəncərələrin kənarlarından fit səsi eşidilməsi və əli yaxınlaşdırdıqda soyuq hava axınının hiss olunması pəncərənin kip bağlanmamasından qaynaqlanır.</p>

<h2>Necə həll etmək olar?</h2>
<ol>
<li><strong>Pəncərəni Qış rejiminə keçirin:</strong> Pəncərə tayının yan metal mexanizmində yerləşən dairəvi və ya oval tənzimləyici boltları (eksentrikləri) 4 mm-lik altıbucaqlı açar (alyan) ilə rezinə tərəf sıxın. Bu, tayın çərçivəyə basılma gücünü artırır.</li>
<li><strong>Qara rezin fitillərin (elastik contaların) bərpası:</strong> İllərlə quru qalan rezinlər bərkiyir və çatlayır. Rezinləri silikon spreylə yağlayın, əgər tam quruyubsa, yeni keyfiyyətli kauçuk rezinlərlə əvəz edin.</li>
<li><strong>Çərçivə ətrafında montaj köpüyünün dağılması:</strong> Bayır tərəfdən günəş vuran köpük çürüyür və divarla çərçivə arasından külək keçir.</li>
</ol>''',
    },
    {
        'bashliq': 'Plastik pəncərənin dəstəyi ilişib fırlanmır və ya tam bağlanmır',
        'slug': 'plastik-pencere-tutacaq-firlanmir',
        'kategori_slug': 'plastik-qapi-pencere',
        'seo_title': 'Plastik Pəncərə Dəstəyi Niyə Fırlanmır? Kilid Mexanizmi və Qol Təmiri | Prousta.az',
        'seo_description': 'Pəncərə tutacağı yarıda ilişib qalır, bağlanmır? Blokirator nasazlığı, furnitur yağlanması və tənzimləmə qaydaları.',
        'metn': '''<h2>Dəstək yarıda ilişib qaldıqda nə etməli?</h2>
<p>Dəstəyi zorla fırlatmağa çalışmayın — daxili ötürücü zamok dişləri silumin olduğu üçün dərhal qırıla bilər.</p>

<h2>Ən çox rast gəlinən səbəb: Blokiratorun ilişməsi</h2>
<p>Pəncərə açıq vəziyyətdə olanda dəstək təsadüfən aşağı salındıqda pəncərə həm açılma, həm havalandırma (ikiqat) rejiminə düşür və ilişir. Tayın yan hissəsindəki yaylı metal dili (blokiratoru) barmağınızla şaquli vəziyyətə gətirib sıxın və dəstəyi üfüqi vəziyyətə qaytarın.</p>

<h2>Digər səbəblər:</h2>
<ul>
<li>Furnitur mexanizminin toz və qumla dolması (yağlanma tələb edir).</li>
<li>Pəncərə tayının ağırlıqdan aşağı sallanması və kilid qarmaqlarının qarşıdakı dəmirə ilişməsi.</li>
</ul>''',
    },
    {
        'bashliq': 'Plastik pəncərənin şüşələri niyə tərləyir və su axıdır?',
        'slug': 'plastik-pencere-terleyir-su-alir',
        'kategori_slug': 'plastik-qapi-pencere',
        'seo_title': 'Pəncərə Niyə Tərləyir? Şüşələrdə Nəm və Kifin Qarşısının Alınması | Prousta.az',
        'seo_description': 'Qışda plastik pəncərələrdən su damır və divarlarda kif yaranır? Otaq rütubəti, ikiqat şüşəpakət və havalandırma həlləri.',
        'metn': '''<h2>Şüşələrin su içində qalması problemi</h2>
<p>Soyuq havada şüşəpakətlərin üzərində su damcılarının toplanması və pəncərəaltı taxtaya axması pəncərənin "xarab" olmasından daha çox otaq mikroiqliminin pozulmasından xəbər verir.</p>

<h2>Səbəblər və Həlli:</h2>
<ul>
<li><strong>Otaqda yüksək rütubət və zəif havalandırma:</strong> Paltarların içəridə qurudulması, yemək bişirilərkən aspiratorun yandırılmaması rütubəti 70%-dən yuxarı qaldırır və nəm soyuq şüşədə şeh nöqtəsinə çevrilir. Otağı gündə 2-3 dəfə 10 dəqiqə şırnaqla havalandırın.</li>
<li><strong>Geniş pəncərəaltı taxtanın radiator istiliyini kəsməsi:</strong> Radiatorun isti havası şüşəyə qalxa bilmir. Pəncərəaltı taxtaya xüsusi ventilyasiya barmaqlıqları quraşdırılmalıdır.</li>
<li><strong>Tək kameralı adi şüşəpakət:</strong> Şüşə daxildən çox soyuq qalır. Enerjiyə qənaət edən (Low-E) şüşəpakətlərlə əvəz edilməlidir.</li>
</ul>''',
    },
    {
        'bashliq': 'Kupe şkafın qapısı relsdən çıxır və çətin sürüşür',
        'slug': 'kupe-qapi-relsden-cixir',
        'kategori_slug': 'mebel-ustasi',
        'seo_title': 'Kupe Şkaf Qapısı Niyə İlişir? Relsdən Çıxma və Təkər Təmiri | Prousta.az',
        'seo_description': 'Sürgülü şkaf qapısı relsdən çıxır, ağır gedir? Aşağı və yuxarı təkər diyircəklərinin tənzimlənməsi və təmiri.',
        'metn': '''<h2>Kupe qapılarının nasazlıqları</h2>
<p>Şkaf-kupenin böyük güzgülü qapısının yoldan çıxması təkcə narahatlıq deyil, həm də təhlükəsizlik problemidir.</p>

<h2>Səbəblər:</h2>
<ol>
<li><strong>Aşağı relsin içinə toz və sapların dolması:</strong> Relsin kanallarını tozsoranla və nəm əski ilə təmizləyin.</li>
<li><strong>Aşağı təkər mexanizminin (rolik) aşınması:</strong> Plastik diyircək qırıldıqda metal metalın üstündə sürtünür. Təkər cütü yenilənməlidir.</li>
<li><strong>Tənzimləmə vintinin boşalması:</strong> Qapı bir tərəfə əyilir və yuxarı bələdçidən çıxır. Aşağı təkərin yanındakı tənzimləyici vinti 4 mm alyanla buraraq qapının hündürlüyünü bərabərləşdirin.</li>
<li><strong>Relsin əyilməsi və ya qopması.</strong></li>
</ol>''',
    },
    {
        'bashliq': 'Mətbəx mebeli qapıları əyilib, petlələr (şarnirlər) boşalıb',
        'slug': 'metbex-mebeli-mexanizm-sallanir',
        'kategori_slug': 'mebel-ustasi',
        'seo_title': 'Mətbəx Şkafı Qapıları Niyə Əyilir? Petlə Tənzimlənməsi və Bərkidilməsi | Prousta.az',
        'seo_description': 'Mətbəx dolabının qapıları bir-birinə sürtünür və sallanır? Şarnir petlələrinin 3 istiqamətdə düzəldilməsi və MDF bərpası.',
        'metn': '''<h2>Sallanan şkaf qapılarını necə düzəltmək olar?</h2>
<p>Zaman keçdikcə mətbəx qapıları ağırlıqdan aşağı enir, aralarında əyri yarıqlar yaranır və ya bir-birinə dəyərək örtülmür.</p>

<h2>Petlələrin vintaçanla tənzimlənməsi:</h2>
<ul>
<li><strong>Hündürlüyü (yuxarı-aşağı) tənzimləmək:</strong> Petlənin korpusa bərkidilən iki uzunsov vintini azca boşaldıb qapını qaldırın və yenidən bərkidin.</li>
<li><strong>Dərinliyi (irəli-geri) tənzimləmək:</strong> Petlənin ən arxasındakı fiksator vinti ilə qapının korpusa kip oturmasını təmin edin.</li>
<li><strong>Sağa-sola meyillənməni düzəltmək:</strong> Petlənin ön tərəfindəki mərkəzi vinti saat əqrəbi istiqamətində burduqda qapı kənara, əksinə burduqda mərkəzə doğru meyil edir.</li>
<li><strong>Şurup yerinin boşalması (MDF/Laminatın yeyilməsi):</strong> Əgər taxta deşiyi genəlibsə, taxta çöp və PVA yapışqanı ilə deşiyi doldurub quruduqdan sonra vinti bərkidin.</li>
</ul>''',
    },
    {
        'bashliq': 'Laminat parket qabarır, şişir və basdıqda cırıldayır',
        'slug': 'laminat-qabarir-ses-cixarir',
        'kategori_slug': 'laminat-parket-ustasi',
        'seo_title': 'Laminat Niyə Şişir və Cırıldayır? Qabarma Səbəbləri və Düzəldilməsi | Prousta.az',
        'seo_description': 'Döşənmiş laminat ortadan təpə kimi qalxır və ayaq basanda səs çıxarır? Divar arası kompensasiya boşluğu və nəmlik təmiri.',
        'metn': '''<h2>Laminatın ortadan şişməsinin səbəbi nədir?</h2>
<p>Laminat "üzən döşəmə" prinsipi ilə vurulur — yəni otağın temperatur və rütubətindən asılı olaraq təbii şəkildə genişlənir və yığılır.</p>

<h2>Əsas səbəb: Divar arası boşluğun (zazorun) buraxılmaması</h2>
<p>Laminat vurularkən divarla laminat arasında ən azı <strong>10-15 mm</strong> genişlənmə boşluğu qalmalıdır. Əgər usta laminatı divara dirəyibsə, yayda və ya nəm havada laminat genişlənərkən divara dirənir və yer tapmadığı üçün otağın ortasından dalğa şəklində yuxarı qalxır.</p>

<h2>Necə düzəltmək olar?</h2>
<p>Bütün plintusları çıxarın. Divara dirənən kənarları xüsusi kəsici ilə 1-1.5 sm kəsin. Boşluq yaranan kimi laminat dərhal yerinə oturacaq. Altlıq döşəmə nahamardırsa və ya şap nəm qalıbsa, xüsusi usta baxışı tələb olunur.</p>''',
    },

    # ---------------- SU FİLTRİ ----------------
    {
        'bashliq': 'Osmos su filtrinin membran və kartricləri niyə tez tutulur?',
        'slug': 'su-filteri-tez-tutulur',
        'kategori_slug': 'su-filteri-ustasi',
        'seo_title': 'Su Filteri Niyə Tez Tıxanır? Membran Ömrünün Uzadılması və Dəyişmə | Prousta.az',
        'seo_description': 'Tərs osmos su filtrinin kartricləri 2 aya tutulur? Bakı suyunun codluğu, ilkin polipropilen filtrlər və dəyişmə vaxtları.',
        'metn': '''<h2>Kartriclər niyə vaxtından tez çirklənir?</h2>
<p>Normalda ilkin 3 filtr 6 aydan bir, əsas membran isə 1.5 - 2 ildən bir dəyişdirilməlidir. Kartriclərin 1-2 aya sıradan çıxması bir neçə amillə bağlıdır:</p>

<h2>Səbəblər:</h2>
<ul>
<li>Şəbəkədə boru təmiri zamanı pas və lil axınının filtrlərə dolması.</li>
<li>1 mikronluq və kömür filtrlərinin vaxtında dəyişdirilməməsi nəticəsində xlorun birbaşa membranı məhv etməsi.</li>
<li>Təzyiq nasosunun zəifləməsi — təzyiq 3 bardan aşağı olanda tullantı klapanı işləmir və membran yuyula bilmir.</li>
</ul>''',
    },
    {
        'bashliq': 'Su filtrindən su çox zəif və damcı-damcı gəlir — Bak təzyiqi',
        'slug': 'su-filtrinden-su-az-gelir',
        'kategori_slug': 'su-filteri-ustasi',
        'seo_title': 'Su Filterindən Su Niyə Zəif Gəlir? Çən Havasının Vurulması Qaydası | Prousta.az',
        'seo_description': 'Kranı açanda su filtrindən ancaq 1 stəkan su gəlir sonra damcılayır? Hidrofor bakına hava vurulması və dördyollu klapan.',
        'metn': '''<h2>Kranı açanda su niyə dərhal kəsilir?</h2>
<p>İstifadəçilərin ən çox rastlaşdığı hal: Kranı açırsınız, yarım stəkan su sürətlə axır, sonra isə nazik damcıya çevrilir. Çəni əllə yoxladıqda isə onun ağır və su ilə dolu olduğu hiss olunur.</p>

<h2>Əsas səbəb: Su çəninin (bakın) havasının bitməsi</h2>
<p>Filtrin yığma çəninin içində rezin membran və alt hissəsində hava kamerası var. Zamanla hava çıxdıqda membranı sıxıb suyu kranadək qaldıra bilmir.</p>

<h2>Necə düzəltməli?</h2>
<ol>
<li>Çənin altındakı velosiped tipli hava ventilini tapın.</li>
<li>Çənin üstündəki mavi su kranını açıq qoyun ki, daxildəki su xaric olsun.</li>
<li>Sadə velosiped və ya maşın nasosu ilə ventildən çənə <strong>0.5 - 0.6 bar (7-8 PSI)</strong> hava vurun. Artıq hava vurmaq membranı partlada bilər!</li>
</ol>''',
    },
    {
        'bashliq': 'Təmizlənmiş içməli suyun dadı acı və ya qoxulu gəlir',
        'slug': 'su-filtrinden-su-dada-pis-gelir',
        'kategori_slug': 'su-filteri-ustasi',
        'seo_title': 'Filtrdən Gələn Su Niyə Dadını Dəyişir? Post-Karbon və Minerallaşdırıcı | Prousta.az',
        'seo_description': 'Filtr suyu acıyır, kükürd qoxusu verir? Bak daxilində bakteriya yığılması, post-karbon filtrin köhnəlməsi və dezinfeksiya.',
        'metn': '''<h2>İçməli suyun dadının pisləşməsi</h2>
<p>Əgər osmos filtrindən gələn suyun dadında acılıq, rezin iyi və ya nəm qoxusu hiss olunursa, filtri belə vəziyyətdə içmək qətiyyən tövsiyə olunmur.</p>

<h2>Səbəblər:</h2>
<ul>
<li><strong>Post-karbon (dad tənzimləyici) filtrin köhnəlməsi:</strong> Kokos kömüründən hazırlanan sonuncu filtr doymuş və qoxu hopdurma xüsusiyyətini itirmişdir.</li>
<li><strong>Yığma çənində bakteriya çoxalması:</strong> Əgər evdən 1-2 həftəlik uzaqlaşmısınızsa və su çəndə durğun qalıbsa, çən daxilində bio-təbəqə formalaşır. Çən xüsusi qida spirti və ya hidrogen peroksidlə dezinfeksiya edilməlidir.</li>
<li><strong>Minerallaşdırıcı kartricin keyfiyyətsiz olması.</strong></li>
</ul>''',
    },
]


class Command(BaseCommand):
    help = '55+ peşəkar texniki problem və bələdçi məqaləsini (Problem modeli) bazaya daxil edir və ya yeniləyir.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Ekspert problem bələdçilərinin bazaya daxil edilməsi başladı..."))
        created_count = 0
        updated_count = 0

        # Kategori lüğəti
        kategoriyalar = {k.slug: k for k in Kategori.objects.all()}

        for item in PROBLEMLER_DATA:
            kategori = kategoriyalar.get(item.get('kategori_slug'))
            if not kategori and item.get('kategori_slug'):
                self.stdout.write(self.style.WARNING(f"Kateqoriya tapılmadı: {item.get('kategori_slug')}"))

            problem, created = Problem.objects.update_or_create(
                slug=item['slug'],
                defaults={
                    'bashliq': item['bashliq'],
                    'metn': item['metn'],
                    'seo_title': item['seo_title'],
                    'seo_description': item['seo_description'],
                    'kategori': kategori,
                    'aktiv': True,
                }
            )

            if created:
                created_count += 1
            else:
                updated_count += 1

        total = Problem.objects.count()
        self.stdout.write(self.style.SUCCESS(
            f"Uğurla tamamlandı! Yaradıldı: {created_count}, Yeniləndi: {updated_count}. Ümumi aktiv problem sayı: {total}"
        ))
