"""Optimize SEO titles, meta descriptions, and category assignments for high-impression problem guides."""
from django.db import migrations


PROBLEM_SEO_UPDATES = {
    'kombi-yanmir': {
        'seo_title': 'Kombi Niyə Yanmır? 7 Əsas Səbəb, Yoxlama və Həlli | Prousta.az',
        'seo_description': 'Kombi yanmır və ya alışmır? Qaz təzyiqi (1.5 bar), alov elektrodu, fan və plata nasazlığının evdə yoxlanması, reset qaydası və kombi ustası.',
    },
    'kombi-isti-su-vermir': {
        'seo_title': 'Kombi İsti Su Vermir (İsitmə İşləyir) — 5 Səbəb və Həlli | Prousta.az',
        'seo_description': 'Kombi işləyir amma krandan isti su gəlmir? 3-yollu klapan, axın sensoru (turbinka), NTC datçik və esenjor ərpinin yoxlanması və təmiri.',
    },
    'kombi-tezyiqi-dusur': {
        'seo_title': 'Kombinin Su Təzyiqi Niyə Düşür? (Bar Düşməsi Səbəbləri) | Prousta.az',
        'seo_description': 'Kombi təzyiqi tez-tez 1 bar-dan aşağı düşür? Genişlənmə çəni (membran), gizli su sızması və qoruyucu klapan yoxlaması və aradan qaldırılması.',
    },
    'kombi-ses-edir': {
        'seo_title': 'Kombi Niyə Səs Edir? Gurultu, Vıyıltı və Tıqqıltı Həlli | Prousta.az',
        'seo_description': 'Kombidən qəribə gurultu, qaynama və ya fan vıyıltısı gəlir? Səs növünə görə dəqiq diaqnoz: esenjor yuyulması, nasos və ventilyator təmiri.',
    },
    'pitiminutka-yanmir-qigildim-vurmur': {
        'seo_title': 'Pitiminutka Niyə Yanmır? Çaxmaq Vurmur və Qaz Açılmır | Prousta.az',
        'seo_description': 'Pitiminutka su açanda alışmır və ya qığılcım vurmur? Batareya yuvası, mikroaçar (mikrik), su membranı və elektromaqnit klapanın yoxlanması.',
    },
    'kombi-e01-xetasi': {
        'seo_title': 'Kombi E01 Xətası Nədir? Alovlanma Problemi və Reset Həlli | Prousta.az',
        'seo_description': 'Baxi, ECA, DemirDöküm və digər kombilərdə E01 xəta kodu: qaz təchizatı, faza-sıfır çevrilməsi, ionizasiya elektrodu və qaz klapanı yoxlaması.',
    },
    'pitiminutka-tez-sonur': {
        'seo_title': 'Pitiminutka Yanıb Tez Sönür? Termopara və Baca Səbəbləri | Prousta.az',
        'seo_description': 'Su qızdırıcısı (pitiminutka) yanıb 1-2 dəqiqəyə sönür? Termopara, baca dartımı, qızma datçiki və su təzyiqi nasazlıqlarının həlli.',
    },
    'tualet-su-saxlamir': {
        'seo_title': 'Unitaz (Tualet) Su Saxlamır və Su Axıdır — Baçok Təmiri | Prousta.az',
        'seo_description': 'Unitaz baçoku daim su buraxır və ya su yığmır? Boşaltma mexanizmi, üzgəc (poplavok) və rezin klapanın tənzimlənməsi və dəyişdirilməsi.',
    },
    'kombi-radiatorlari-qizdirmir': {
        'seo_title': 'Kombi İşləyir Amma Radiatorlar Qızmır — 6 Səbəb və Həlli | Prousta.az',
        'seo_description': 'Kombi yanır lakin radiatorlar (batareyalar) soyuq qalır? Hava buraxılması, 3-yollu klapan, dövriyyə nasosu və abratka filtrinin təmizlənməsi.',
    },
    'kombi-radiatorlarin-alti-qizmir': {
        'seo_title': 'Radiatorun Üstü İsti, Altı Soyuqdur — Niyə Qızmır? | Prousta.az',
        'seo_description': 'Kombi radiatorlarının altı qızmır və ya sonuncu pətək soyuqdur? Sistemdə çöküntü, radiator yuyulması, hava çıxarılması və balanslaşdırma.',
    },
    'kombiden-su-axir': {
        'seo_title': 'Kombidən Su Axır və Damcılayır — 5 Əsas Səbəb və Həlli | Prousta.az',
        'seo_description': 'Kombinin altından su damcılayır? 3 bar təhlükəsizlik klapanı, genişlənmə çəni, doldurma kranı və birləşmə sızmalarının yoxlanması.',
    },
    'kombi-isti-su-dalgalanir': {
        'seo_title': 'Kombidə İsti Su Gah Soyuyur, Gah Qaynarlaşır — Həlli | Prousta.az',
        'seo_description': 'Duşda kombi suyu gah isti, gah soyuq gəlir? İkinci esenjorun ərp bağlaması, NTC temperatur sensoru və su təzyiqi dalğalanmasının təmiri.',
    },
    'gidrofor-su-nasosu-tez-tez-iseyir': {
        'seo_title': 'Gidrofor (Su Nasosu) Niyə Tez-Tez İşə Düşür və Sönmür? | Prousta.az',
        'seo_description': 'Su motoru (gidrofor) fasiləsiz işləyir və ya tez-tez qoşulub-ayrılır? Membran (qruşa) deşilməsi, hava təzyiqi, avtomat və əks-klapan yoxlaması.',
    },
    'kombi-xeta-kodu': {
        'seo_title': 'Kombi Xəta Kodları (E01, E02, E10, F1, F4, F22, 501) | Prousta.az',
        'seo_description': 'Kombi ekranında xəta kodu yanır? Baxi, Ariston, Bosch, Immergas, ECA və Viessmann kombilərində xəta kodlarının mənası və ilk yoxlama addımları.',
    },
    'kanalizasiya-tixanib': {
        'seo_title': 'Kanalizasiya Tıxanıb, Su Getmir — Açma Üsulları və Usta | Prousta.az',
        'seo_description': 'Mətbəx moykası, unitaz və ya hamam trapı tutulub? Evdə tıxanmanı açma üsulları və qırmadan elektrotros/aparatla kanalizasiya açılması.',
    },
    'paltaryuyan-qapisi-acilmir': {
        'seo_title': 'Paltaryuyan Maşının Qapısı Açılmır — Təcili Açma Qaydası | Prousta.az',
        'seo_description': 'Yuma bitib amma paltaryuyanın qapısı kilidli qalıb? İçəridə su qalması, qəza trosu ilə açma və qapı kilidi (UBL zamok) nasazlığının həlli.',
    },
    'kombi-f4-xetasi': {
        'seo_title': 'Kombi F4 / F04 Xətası Nədir? Alov Sönməsi və Həlli | Prousta.az',
        'seo_description': 'Viessmann, Ferroli və DemirDöküm kombilərdə F4 (F04) xətası: qaz klapanı, ionizasiya elektrodu və alovlanma blokirovkasının aradan qaldırılması.',
    },
    'kondisioner-qizdirmir': {
        'seo_title': 'Kondisioner Niyə Qızdırmır (İsti Hava Vurmur)? Səbəbləri | Prousta.az',
        'seo_description': 'Kondisioner HEAT (Günəş) rejimində isti vurmur? Defrost (donma) rejimi, freon qaz azlığı, 4-yollu klapan və kompressor yoxlaması.',
    },
    'kondisioner-soyutmur': {
        'kategori_slug': 'kondisioner-ustasi',
        'seo_title': 'Kondisioner Niyə Soyutmur? 6 Əsas Səbəb və Həlli | Prousta.az',
        'seo_description': 'Kondisioner işləyir amma sərin hava vurmur? Freon qaz çatışmazlığı, filtr və radiator tutulması, kondensator və kompressor diaqnostikası.',
    },
    'boyler-su-qizdirmir': {
        'kategori_slug': 'ariston-ustasi',
        'seo_title': 'Ariston (Boyler) Su Qızdırmır — TEN və Termostat Yoxlaması | Prousta.az',
        'seo_description': 'Elektrikli su qızdırıcısı (Ariston / boyler) suyu isitmir? TEN yanması, termostat atması və ərp təmizlənməsi üzrə təmir bələdçisi.',
    },
    'boyler-su-sizdirir': {
        'kategori_slug': 'ariston-ustasi',
        'seo_title': 'Ariston (Boyler) Su Axıdır və Damcılayır — Təcili Həlli | Prousta.az',
        'seo_description': 'Boylerin altından və ya klapanından su damcılayır? Qoruyucu klapan, flanş rezini (salnik) və çən korroziyasının yoxlanması.',
    },
    'boyler-qoruyucu-klapan-su-axidir': {
        'seo_title': 'Ariston (Boyler) Qoruyucu Klapanından Niyə Su Axır? Həlli | Prousta.az',
        'seo_description': 'Su qızdırıcısının (boylerin) altındakı qoruyucu klapandan su damcılayır? Yüksək su təzyiqi, reduktor quraşdırılması və klapan dəyişdirilməsi.',
    },
    'soyuducu-arxasindan-ses-gelir': {
        'seo_title': 'Soyuducu Niyə Səs Edir? Kompressor, Fan və Qaz Səsləri | Prousta.az',
        'seo_description': 'Soyuducunun arxasından gurultu, tıqqıltı və ya vıyıltı səsi gəlir? No-Frost ventilyatorunun buzlaması, motor rezinləri və freon dövranı yoxlaması.',
    },
    'kombi-501-xetasi-ariston': {
        'seo_title': 'Ariston Kombi 501 Xətası — Alov Yoxdur (Reset və Təmiri) | Prousta.az',
        'seo_description': 'Ariston kombidə 501 xəta kodu yanır? Alov aşkarlanmama səbəbləri: qaz kranı, ionizasiya elektrodu, kondensat sifonu və elektron plata təmiri.',
    },
    'kombi-f5-f05-xetasi': {
        'seo_title': 'Kombi F5 / F05 Xətası — Hava Presostatı və Fan Nasazlığı | Prousta.az',
        'seo_description': 'Kombidə F5 və ya F05 xətası çıxır? Baca tutulması, hava presostatı (hava açarı), kondensat borusu və ventilyator motorunun yoxlanması və təmiri.',
    },
    'paltaryuyan-cox-ses-titreyis': {
        'seo_title': 'Paltaryuyan Sıxanda Çox Səs Edir və Silkələnir — Həlli | Prousta.az',
        'seo_description': 'Paltaryuyan maşın sıxma zamanı güclü gurultu salır və yerindən tərpənir? Baraban podşipniki (topu), amortizator və əks-çəki daşı diaqnostikası.',
    },
    'uzo-diferensial-avtomat-atir': {
        'seo_title': 'UZO (Diferensial Avtomat) Niyə Tez-Tez Atır? Sızma Təyini | Prousta.az',
        'seo_description': 'Elektrik şitində UZO və ya diferensial avtomat işığı kəsir? Məişət cihazlarında (boyler, paltaryuyan) cərəyan sızması və naqil izolyasiyası yoxlaması.',
    },
    'kombi-tezyiqi-qalxir': {
        'seo_title': 'Kombinin Təzyiqi (Bar) Niyə Öz-Özünə Qalxır? 3 Səbəb | Prousta.az',
        'seo_description': 'Kombi təzyiqi 2.5 - 3 bar-a qalxır və altından su atır? Doldurma kranının (podpitka) buraxması, genişlənmə çəni və ikinci esenjor deşilməsi.',
    },
    'kanalizasiya-pis-qoxu': {
        'seo_title': 'Hamam və Mətbəxdə Kanalizasiya Qoxusu — 5 Səbəb və Həlli | Prousta.az',
        'seo_description': 'Evdə trapdan və ya moykadan pis kanalizasiya iyi gəlir? Su qıfılının (sifonun) quruması, boru kipliyi və fan borusu tıxanmasının aradan qaldırılması.',
    },
    'soyuducu-buz-baglayir-no-frost': {
        'seo_title': 'No-Frost Soyuducu Niyə Buz Bağlayır və Soyutmur? Həlli | Prousta.az',
        'seo_description': 'No-Frost soyuducunun dondurucu kamerası buz bağlayır və aşağı soyutmur? Defrost TEN-i, taymer, termosigorta və drenaj kanalının təmiri.',
    },
    'kondisioner-su-damizdirir': {
        'seo_title': 'Kondisionerdən Evin İçinə Niyə Su Axır? Drenaj Təmiri | Prousta.az',
        'seo_description': 'Kondisionerin daxili blokundan otağa su damcılayır? Drenaj şlanqının tutulması, vannanın çatlaması və ya freon azlığı səbəbindən buzlama həlli.',
    },
    'paltaryuyan-altindan-su-axidir': {
        'seo_title': 'Paltaryuyan Maşının Altından Su Axır — Sızma Yeri və Təmiri | Prousta.az',
        'seo_description': 'Paltaryuyan işləyəndə altından su gəlir? Qapı manjeti (rezini), yuyucu toz qabı, drenaj filtr qapağı və daxili patrul şlanqlarının yoxlanması.',
    },
    'soyuducu-asagi-soyudur-yuxari-yox': {
        'seo_title': 'Soyuducunun Bir Gözü Soyudur, Digəri Soyutmur — Səbəbləri | Prousta.az',
        'seo_description': 'Soyuducunun dondurucu hissəsi işləyir amma adi kamera soyutmur? Hava damperi (zaslonka), No-Frost ventilyatoru və qaz sızması diaqnostikası.',
    },
    'su-tezyiqi-azdir': {
        'seo_title': 'Evdə Su Təzyiqi Çox Zəifdir — Su Təzyiqini Artırmaq Üsulları | Prousta.az',
        'seo_description': 'Krandan su zəif gəlir və kombi/pitiminutka yanmır? Giriş su filtri, kran aeratoru, boru ərpi və təzyiq artırıcı nasos (gidrofor) quraşdırılması.',
    },
    'paltaryuyan-su-goturmur': {
        'seo_title': 'Paltaryuyan Maşın Su Yığmır (Su Götürmür) — 5 Səbəb | Prousta.az',
        'seo_description': 'Paltaryuyan proqramı başlayır amma barabana su gəlmir? Giriş su klapanı, torlu filtr, qapı kilidi (UBL) və presostat nasazlığının yoxlanması.',
    },
    'ariston-boyler-isiq-vurur': {
        'seo_title': 'Ariston (Boyler) Su və Kran Tok Vurur — Təcili Həlli | Prousta.az',
        'seo_description': 'Hamamda krandan və ya duşdan elektrik cərəyanı (tok) vurur? Boyler TEN-inin gövdəyə deşilməsi, torpaqlama xətti və UZO yoxlaması.',
    },
    'kran-su-buraxir': {
        'seo_title': 'Su Kranı (Smesitel) Damcılayır və Su Buraxır — Təmiri | Prousta.az',
        'seo_description': 'Mətbəx və ya hamam kranı bağlandıqda belə su damcılayır? Keramik kartric (kartuş), kran-buksa və rezin prokladkanın dəyişdirilməsi qaydası.',
    },
    'su-filtrinden-su-az-gelir': {
        'seo_title': 'Su Filtrindən Su Zəif Gəlir və ya Gəlmir — Çən və Kartric | Prousta.az',
        'seo_description': 'Mətbəx su filtrinin kranından su çox az axır? Ehtiyat çənində hava təzyiqinin düşməsi (0.5 bar), membran və ön kartriclərin tutulması həlli.',
    },
    'kondisioner-buz-baglayir': {
        'seo_title': 'Kondisionerin Daxili Bloku və Borusu Niyə Buz Bağlayır? | Prousta.az',
        'seo_description': 'Kondisionerin mis boruları və iç petəkləri qar/buz tutur? Freon qazının azalması, kapilyar boru tıxanması və toz filtrinin yuyulması.',
    },
    'kondisioner-oz-ozune-sonur': {
        'seo_title': 'Kondisioner İşləyib Öz-Özünə Sönür — Taymer və Plata | Prousta.az',
        'seo_description': 'Kondisioner 5-10 dəqiqə işləyib dayanır və xəta verir? Kompressorun qızması, kondensator, temperatur datçiki və elektron plata diaqnostikası.',
    },
    'tezyiq-reduktoru-nasazligi': {
        'seo_title': 'Su Təzyiq Reduktoru Niyə Xarab Olur? Tənzimləmə və Dəyişmə | Prousta.az',
        'seo_description': 'Mənzil girişindəki su təzyiq reduktoru təzyiqi saxlamır və ya suyu kəsir? Manometr göstəricisi (3-4 bar), membran təmizliyi və santexnik xidməti.',
    },
}


def update_problem_seo(apps, schema_editor):
    Problem = apps.get_model('core', 'Problem')
    Kategori = apps.get_model('core', 'Kategori')
    alias = schema_editor.connection.alias
    categories = {c.slug: c for c in Kategori.objects.using(alias).all()}

    for slug, data in PROBLEM_SEO_UPDATES.items():
        updates = {
            'seo_title': data['seo_title'],
            'seo_description': data['seo_description'],
        }
        cat_slug = data.get('kategori_slug')
        if cat_slug and cat_slug in categories:
            updates['kategori'] = categories[cat_slug]
        Problem.objects.using(alias).filter(slug=slug).update(**updates)


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0035_populate_listing_areas_and_expiry'),
    ]

    operations = [
        migrations.RunPython(update_problem_seo, migrations.RunPython.noop),
    ]
