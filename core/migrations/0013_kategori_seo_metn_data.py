from django.db import migrations


def _seo_html(ad: str) -> str:
    """Hər alt-kateqoriya üçün SEO-ya uyğun HTML mətn generasiya edir."""
    ad_l = ad.lower()
    return f"""
<h2>{ad} — Bakıda Peşəkar Xidmət</h2>
<p><strong>{ad}</strong> axtarırsınız? <strong>Prousta.az</strong> Azərbaycanın ən böyük usta və xidmət platformasıdır. Burada {ad_l} sahəsində işləyən təcrübəli ustaları tapa, qiymətləri müqayisə edə və birbaşa əlaqə saxlaya bilərsiniz. Bütün ustalarımız öz sahələri üzrə peşəkardırlar və göstərdikləri xidmətin keyfiyyətinə zəmanət verirlər.</p>

<p>Müasir həyat tempində vaxt ən dəyərli resursdur. Elə buna görə də, tələb olunan işi mümkün qədər tez və keyfiyyətli görə biləcək <strong>{ad_l}</strong> seçmək çox vacibdir. Prousta.az saytında yerləşdirilmiş hər bir elan real ustalara aiddir — istifadəçi rəyləri, telefon nömrəsi və iş nümunələri açıq şəkildə göstərilir.</p>

<h3>{ad} xidmətinin əhatə dairəsi</h3>
<p>Platformamızda qeydiyyatdan keçmiş <strong>{ad_l}</strong> mütəxəssisləri aşağıdakı işləri görür:</p>
<ul>
  <li>Problemin pulsuz diaqnostikası və ilkin qiymətləndirmə</li>
  <li>Təcili çağırış — eyni gün ərzində ünvana gəlmə imkanı</li>
  <li>Bakı və ətraf rayonlar üzrə tam əhatə</li>
  <li>Keyfiyyətli material və orijinal ehtiyat hissələri ilə işləmə</li>
  <li>Görülən işə yazılı zəmanət verilməsi</li>
  <li>Münasib və şəffaf qiymət siyasəti</li>
</ul>

<h3>Nə üçün Prousta.az-dan {ad_l} seçməlisiniz?</h3>
<p>Prousta.az — sadəcə elan saytı deyil, peşəkarları ilə müştəriləri birləşdirən etibarlı bir körpüdür. Saytımızın üstünlükləri:</p>
<ul>
  <li><strong>Yoxlanılmış ustalar:</strong> Hər elan moderasiyadan keçir, saxta profillərə icazə verilmir.</li>
  <li><strong>Rəylər və reytinq:</strong> Əvvəlki müştərilərin rəylərini oxuyaraq düzgün seçim edə bilərsiniz.</li>
  <li><strong>Birbaşa əlaqə:</strong> Vasitəçi yoxdur — usta ilə birbaşa danışıqlar aparırsınız.</li>
  <li><strong>Pulsuz istifadə:</strong> Saytın bütün imkanlarından ödənişsiz yararlana bilərsiniz.</li>
  <li><strong>Şəffaflıq:</strong> Qiymət, xidmət müddəti və iş şərtləri əvvəlcədən razılaşdırılır.</li>
</ul>

<h3>{ad} qiymətləri — nədən asılıdır?</h3>
<p><strong>{ad}</strong> xidmətinin qiyməti bir neçə amildən asılıdır: işin mürəkkəbliyi, lazım olan materialların maliyyəti, ustanın təcrübəsi, xidmətin göstəriləcəyi ünvanın məsafəsi və işin təcililiyi. Dəqiq qiymət almaq üçün ustaya birbaşa zəng edib vəziyyəti izah etməyiniz tövsiyə olunur. Bəzi ustalar pulsuz baxış təklif edir, bu da sizə əlavə xərclərdən qaçmağa kömək edir.</p>

<h3>Tez-tez verilən suallar</h3>

<div class="faq-item">
  <div class="faq-q">{ad} necə sifariş verə bilərəm?</div>
  <p>Uyğun elanı seçin, elandakı telefon nömrəsi ilə ustaya zəng edin və ya sayt üzərindən mesaj yazın. Problemi izah edərək qiymət və görüş vaxtını razılaşdıra bilərsiniz.</p>
</div>

<div class="faq-item">
  <div class="faq-q">Xidmətin qiyməti nə qədərdir?</div>
  <p>Qiymət işin həcmindən və mürəkkəbliyindən asılıdır. Dəqiq məbləği öyrənmək üçün ustaya zəng edib detalları danışmağınız lazımdır. Bir neçə ustadan qiymət alıb müqayisə etmək də yaxşı fikirdir.</p>
</div>

<div class="faq-item">
  <div class="faq-q">Usta təcili gələ bilərmi?</div>
  <p>Bəli, {ad_l}larımızın əksəriyyəti eyni gün ərzində, bəzən hətta 1-2 saat içində ünvana gələ bilir. Təcili hallar üçün elanda "təcili xidmət" qeydi olan ustalara üstünlük verin.</p>
</div>

<div class="faq-item">
  <div class="faq-q">Görülən işə zəmanət verilirmi?</div>
  <p>Peşəkar ustalar öz işlərinə zəmanət verirlər. Zəmanət müddəti adətən 1 aydan 1 ilə qədər dəyişir və işin növündən asılıdır. Sifariş verməzdən əvvəl zəmanət şərtlərini dəqiqləşdirməyiniz tövsiyə olunur.</p>
</div>

<div class="faq-item">
  <div class="faq-q">Bakının bütün rayonlarına xidmət göstərilirmi?</div>
  <p>Bəli, platformamızdakı ustalar Bakının bütün rayonlarına — Nərimanov, Yasamal, Nəsimi, Səbail, Xətai, Binəqədi, Suraxanı, Sabunçu, Qaradağ, Nizami, Xəzər və Pirallahıya xidmət göstərir. Bəzi ustalar Sumqayıt, Abşeron və digər regionlara da gedir.</p>
</div>

<p><strong>{ad}</strong> lazımdırsa — yuxarıdakı elanlardan uyğun olanı seçin və peşəkarla əlaqə saxlayın. Prousta.az sizə etibarlı və keyfiyyətli xidmət tapmaqda yardımçı olacaq.</p>
""".strip()


# Bəzi əsas kateqoriyalar üçün xüsusi vurğulanmış mətnlər (müstəqil giriş paraqrafı)
CUSTOM_INTROS = {
    'su-sizma': (
        "Evdə və ya ofisdə <strong>su sızması</strong> ciddi problemdir — vaxtında aradan qaldırılmazsa, divarların küflənməsinə, döşəmənin xarab olmasına və qonşuları su basmasına səbəb ola bilər. "
        "Prousta.az-da təcrübəli <strong>su sızması ustaları</strong> müasir avadanlıqla (termal kamera, akustik dinləyici, təzyiq testi) sızmanın mənbəyini dağıntısız aşkarlayır və qısa müddətdə təmir edir."
    ),
    'elektrik': (
        "<strong>Elektrik ustası</strong> axtarırsınız? Prousta.az saytında qeydiyyatdan keçmiş sertifikatlı elektriklər evinizin və ya ofisinizin elektrik sistemində olan istənilən problemi — qısaqapanma, ştepsel dəyişdirilməsi, "
        "avtomatların quraşdırılması, tam elektrik sisteminin yenidən çəkilməsi — peşəkarcasına həll edir. Təhlükəsizlik üçün elektrik işlərini yalnız təcrübəli mütəxəssisə tapşırın."
    ),
    'santexnik': (
        "<strong>Santexnik</strong> — hər evin mütləq ehtiyacı olan mütəxəssisdir. Prousta.az-da Bakının bütün rayonlarından santexniklər toplanıb: kranlar və qarışdırıcıların dəyişdirilməsi, tualet kasasının quraşdırılması, "
        "kanalizasiya borularının təmizlənməsi, qızdırıcı sistemlərin təmiri — bütün işlər peşəkarlıqla görülür."
    ),
    'kombi-ustasi': (
        "<strong>Kombi ustası</strong> çağırmaq üçün Prousta.az ən doğru ünvandır. Soyuq havalarda kombi xarab olanda vaxt itirmək olmaz — saytımızda Baxi, Vaillant, Ferroli, Bosch, Demrad, Ariston və digər markaların rəsmi servisləri ilə işləyən mütəxəssislər var. "
        "Kombinin yanmaması, su sızıntısı, manometrdə təzyiq düşməsi, radiatorların isinməməsi kimi problemlər tez bir zamanda həll olunur."
    ),
    'kondisioner-ustasi': (
        "<strong>Kondisioner ustası</strong> — yay aylarında ən çox axtarılan mütəxəssislərdən biridir. Prousta.az-da kondisionerin quraşdırılması, freon vurulması, filterlərin təmizlənməsi, drenaj borusunun yenilənməsi, "
        "daxili və xarici blokun təmiri kimi bütün xidmətlər üçün təcrübəli ustalar tapa bilərsiniz. Samsung, LG, Midea, Gree, Haier və bütün digər markaların təmiri."
    ),
    'soyuducu-ustasi': (
        "<strong>Soyuducu ustası</strong> Prousta.az-da ünvanınıza gəlir və problemi yerində həll edir. Soyuducunun soyutmaması, dondurucunun işləməməsi, səs çıxarması, "
        "su axıtması, termostatın xarab olması — bütün bu problemlər peşəkar mütəxəssislər tərəfindən qısa müddətdə aradan qaldırılır."
    ),
    'paltaryuyan-ustasi': (
        "<strong>Paltaryuyan ustası</strong> — paltaryuyan maşınınız su almırsa, sıxmırsa, yuyarkən səs çıxarırsa, suyu atmırsa və ya yuyulma proqramı dayanırsa lazımdır. "
        "Prousta.az-da Bosch, Beko, Samsung, LG, Indesit, Ariston və digər markaların təmiri üzrə ixtisaslaşmış mütəxəssislər var. Ehtiyat hissələri orijinal və zəmanətlidir."
    ),
    'telefon-ustasi': (
        "<strong>Telefon ustası</strong> Prousta.az-da — iPhone, Samsung, Xiaomi, Huawei, Honor və bütün markaların ekran dəyişimi, batareya dəyişimi, yuvarlama sonrası təmir, "
        "proqram problemləri, suya düşmə sonrası bərpa və lövhə təmiri xidmətləri. Orijinal hissələr və qısa təmir müddəti."
    ),
    'avtomobil-ustasi': (
        "<strong>Avtomobil ustası</strong> Prousta.az-da — Bakının ən təcrübəli auto-mexanikləri toplanıb. Mühərrik, transmissiya, əyləc sistemi, asqı, elektrik problemləri, kompüter diaqnostikası — "
        "hər növ maşın üçün peşəkar servis. Alman, Yapon, Koreya və Amerika markalarının təmiri üzrə ixtisaslaşmış ustalar."
    ),
    'temizlik-xidmeti': (
        "<strong>Təmizlik xidməti</strong> — ev, ofis, mənzil, villa və tikintidən sonra ümumi təmizlik üçün Prousta.az-da peşəkar briqadalar var. "
        "Müasir avadanlıqlar, ekoloji təmiz kimyəvi maddələr və təcrübəli təmizlikçilərlə hər növ ərazini səliqəyə salırıq."
    ),
    'veb-sayt': (
        "<strong>Veb sayt hazırlanması</strong> — biznesinizi onlayn dünyada görünən etməyin ilk addımıdır. Prousta.az-da sizin üçün korporativ saytlar, onlayn mağazalar, landing page-lər və veb tətbiqlər yaradan "
        "təcrübəli tərtibatçılar və komandalar var. Müasir texnologiyalar, responsiv dizayn və SEO optimallaşdırma daxildir."
    ),
}


def set_seo_metinler(apps, schema_editor):
    Kategori = apps.get_model('core', 'Kategori')
    # Yalnız alt-kateqoriyalar üçün SEO mətn yaz
    for kat in Kategori.objects.filter(ust_kategori__isnull=False):
        if kat.seo_metn:
            continue
        html = _seo_html(kat.ad)
        if kat.slug in CUSTOM_INTROS:
            # Birinci <p>-ni xüsusi intro ilə əvəz et
            import re
            custom = f"<p>{CUSTOM_INTROS[kat.slug]}</p>"
            html = re.sub(r"<p><strong>.*?</p>", custom, html, count=1, flags=re.DOTALL)
        kat.seo_metn = html
        kat.seo_title = f"{kat.ad} — Prousta.az | Bakıda peşəkar xidmət"
        kat.seo_description = f"{kat.ad} axtarırsınız? Prousta.az-da ən yaxşı {kat.ad.lower()} elanları, münasib qiymətlər və təcrübəli mütəxəssislər. Bakı və bütün Azərbaycan."
        kat.save()

    # Əsas (ust) kateqoriyalar üçün də qısa SEO məlumatı
    for kat in Kategori.objects.filter(ust_kategori__isnull=True):
        if not kat.seo_title:
            kat.seo_title = f"{kat.ad} ustaları və xidmətləri — Prousta.az"
            kat.seo_description = f"{kat.ad} sahəsində peşəkar ustalar və xidmətlər Prousta.az-da. Bakıda və Azərbaycanın digər şəhərlərində etibarlı mütəxəssislər tapın."
            kat.save()


def reverse_seo_metinler(apps, schema_editor):
    Kategori = apps.get_model('core', 'Kategori')
    Kategori.objects.update(seo_metn='', seo_title='', seo_description='')


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0012_kategori_seo_fields'),
    ]

    operations = [
        migrations.RunPython(set_seo_metinler, reverse_seo_metinler),
    ]
