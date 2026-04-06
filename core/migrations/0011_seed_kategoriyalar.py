from django.db import migrations


KATEQORIYALAR = [
    {
        'ad': 'Məişət texnikası',
        'slug': 'meiset-texnikasi',
        'ikon': 'fa-blender',
        'alt': [
            ('Kondisioner ustası', 'kondisioner-ustasi'),
            ('Kombi ustası', 'kombi-ustasi'),
            ('Soyuducu ustası', 'soyuducu-ustasi'),
            ('Paltaryuyan ustası', 'paltaryuyan-ustasi'),
            ('Qabyuyan ustası', 'qabyuyan-ustasi'),
            ('Ariston ustası', 'ariston-ustasi'),
            ('Havalandırma ustası', 'havalandirma-ustasi'),
            ('Pitiminutka ustası', 'pitiminutka-ustasi'),
            ('Qaz ustası', 'qaz-ustasi'),
            ('İran peçi ustası', 'iran-peci-ustasi'),
            ('Soba ustası', 'soba-ustasi'),
            ('Su filteri ustası', 'su-filteri-ustasi'),
            ('Tozsoran ustası', 'tozsoran-ustasi'),
            ('Tikiş maşını ustası', 'tikis-masini-ustasi'),
            ('Digər məişət texnikası ustaları', 'diger-meiset-texnikasi'),
        ],
    },
    {
        'ad': 'Elektronika',
        'slug': 'elektronika',
        'ikon': 'fa-laptop',
        'alt': [
            ('Telefon ustası', 'telefon-ustasi'),
            ('Komputer ustası', 'komputer-ustasi'),
            ('Televizor ustası', 'televizor-ustasi'),
            ('Foto və video aparatlar', 'foto-video-aparatlar'),
            ('Planşet təmiri', 'planset-temiri'),
            ('Krosna antena ustası', 'krosna-antena-ustasi'),
            ('Kamera ustası', 'kamera-ustasi'),
            ('Printer ustası', 'printer-ustasi'),
            ('Digər elektronika ustaları', 'diger-elektronika'),
        ],
    },
    {
        'ad': 'Təmir, Tikinti',
        'slug': 'temir-tikinti',
        'ikon': 'fa-hammer',
        'alt': [
            ('Elektrik', 'elektrik'),
            ('Cam balkon', 'cam-balkon'),
            ('Plastik qapı pəncərə', 'plastik-qapi-pencere'),
            ('Sürgü sistemləri', 'surgu-sistemleri'),
            ('Duş kabina', 'dus-kabina'),
            ('Jaluz', 'jaluz'),
            ('Kanalizasiya ustası', 'kanalizasiya-ustasi'),
            ('Su sızma', 'su-sizma'),
            ('Santexnik', 'santexnik'),
            ('Çilingər', 'cilinger'),
            ('Laminat parket ustası', 'laminat-parket-ustasi'),
            ('Dartma tavan ustası', 'dartma-tavan-ustasi'),
            ('Ev təmiri', 'ev-temiri'),
            ('Divar kağızı ustası', 'divar-kagizi-ustasi'),
            ('Lepka ustası', 'lepka-ustasi'),
            ('Kafel-metlax ustası', 'kafel-metlax-ustasi'),
            ('Malyar ustası', 'malyar-ustasi'),
            ('Tol ustası', 'tol-ustasi'),
            ('Məhəccər', 'mehecer'),
            ('Avtomatik qapılar', 'avtomatik-qapilar'),
            ('Beton işləri', 'beton-isleri'),
            ('Asfalt işləri', 'asfalt-isleri'),
            ('Sauna tikintisi', 'sauna-tikintisi'),
            ('Bioklimatik pergola', 'bioklimatik-pergola'),
            ('Hebeşebe sistemi', 'hebesebe-sistemi'),
            ('Anbar tikintisi', 'anbar-tikintisi'),
            ('A frame evlərin tikintisi', 'a-frame-evler'),
            ('Manqal ustası', 'manqal-ustasi'),
            ('Digər təmir ustaları', 'diger-temir'),
        ],
    },
    {
        'ad': 'Reklam və Dizayn',
        'slug': 'reklam-dizayn',
        'ikon': 'fa-palette',
        'alt': [
            ('Çap işləri', 'cap-isleri'),
            ('Reklam xidmətləri', 'reklam-xidmetleri'),
            ('İnteryer dizayn xidməti', 'interyer-dizayn'),
            ('Dizayn xidməti', 'dizayn-xidmeti'),
            ('Vinil bannerlər', 'vinil-bannerler'),
            ('Video xidmətləri', 'video-xidmetleri'),
            ('Foto xidmətləri', 'foto-xidmetleri'),
            ('Digər reklam ustaları', 'diger-reklam'),
        ],
    },
    {
        'ad': 'Mebel və İnteryer',
        'slug': 'mebel-interyer',
        'ikon': 'fa-couch',
        'alt': [
            ('Mətbəx mebelləri quraşdırmaq', 'metbex-mebelleri'),
            ('Vitrin yığmaq', 'vitrin-yigmaq'),
            ('Divan və kreslo ustası', 'divan-kreslo-ustasi'),
            ('Ofis mebelləri', 'ofis-mebelleri'),
            ('Mebel ustası', 'mebel-ustasi'),
            ('Digər mebel ustaları', 'diger-mebel'),
        ],
    },
    {
        'ad': 'Avtomobil təmiri',
        'slug': 'avtomobil-temiri',
        'ikon': 'fa-car',
        'alt': [
            ('Avtomobil ustası', 'avtomobil-ustasi'),
            ('Təkər təmiri ustası', 'teker-temiri-ustasi'),
            ('Avtomobil malyar ustası', 'avtomobil-malyar-ustasi'),
            ('Avtomobil oturacaqlarının üzlənməsi', 'avtomobil-oturacaq'),
            ('Avtomobil təmizliyi', 'avtomobil-temizliyi'),
            ('Avtomobil açar ustası', 'avtomobil-acar-ustasi'),
            ('Digər avtomobil ustaları', 'diger-avtomobil'),
        ],
    },
    {
        'ad': 'Nəqliyyat və texnika',
        'slug': 'neqliyyat-texnika',
        'ikon': 'fa-truck',
        'alt': [
            ('Evakuator xidməti', 'evakuator-xidmeti'),
            ('Zibil daşıma xidməti', 'zibil-dasima'),
            ('Yükdaşıma xidməti', 'yukdasima'),
            ('Avtomobil icarəsi', 'avtomobil-icaresi'),
            ('Qaldırıcı qurğuların icarəsi', 'qaldirici-qurgu-icaresi'),
            ('Texnika icarəsi', 'texnika-icaresi'),
            ('Travego aylıq kirayəsi', 'travego-kirayesi'),
            ('Digər nəqliyyat xidmətləri', 'diger-neqliyyat'),
        ],
    },
    {
        'ad': 'Gözəllik və Sağlamlıq',
        'slug': 'gozellik-saglamliq',
        'ikon': 'fa-spa',
        'alt': [
            ('Fizioterapiya', 'fizioterapiya'),
            ('Masaj xidməti', 'masaj-xidmeti'),
            ('Saç ustası', 'sac-ustasi'),
            ('Lazer epilyasiyası ustası', 'lazer-epilyasiyasi'),
            ('Makiyaj ustası', 'makiyaj-ustasi'),
            ('Dırnaq ustası', 'dirnaq-ustasi'),
            ('Təmizlik xidməti', 'temizlik-xidmeti'),
            ('Dezinfeksiya xidməti', 'dezinfeksiya-xidmeti'),
            ('Digər sağlamlıq ustaları', 'diger-saglamliq'),
        ],
    },
    {
        'ad': 'İT, Biznes xidmətləri',
        'slug': 'it-biznes',
        'ikon': 'fa-briefcase',
        'alt': [
            ('Veb sayt hazırlanması', 'veb-sayt'),
            ('Mobil tətbiq hazırlanması', 'mobil-tetbiq'),
            ('SMM xidməti', 'smm-xidmeti'),
            ('SEO xidməti', 'seo-xidmeti'),
            ('Mühasibatlıq xidməti', 'muhasibatliq'),
            ('Hüquqi xidmətlər', 'huquqi-xidmetler'),
            ('Tərcümə xidməti', 'tercume-xidmeti'),
            ('Repetitor', 'repetitor'),
            ('Digər İT və biznes xidmətləri', 'diger-it-biznes'),
        ],
    },
    {
        'ad': 'Digər ustalar',
        'slug': 'diger-ustalar',
        'ikon': 'fa-tools',
        'alt': [
            ('Usta xidmətləri', 'usta-xidmetleri'),
            ('Metal qəbulu', 'metal-qebulu'),
            ('Trenajor təmiri', 'trenajor-temiri'),
            ('İnşaat materialları', 'insaat-materiallari'),
        ],
    },
]


def seed_kategoriyalar(apps, schema_editor):
    Kategori = apps.get_model('core', 'Kategori')
    for esas in KATEQORIYALAR:
        ust, _ = Kategori.objects.update_or_create(
            slug=esas['slug'],
            defaults={'ad': esas['ad'], 'ikon': esas['ikon'], 'ust_kategori': None},
        )
        for ad, slug in esas['alt']:
            Kategori.objects.update_or_create(
                slug=slug,
                defaults={'ad': ad, 'ikon': '', 'ust_kategori': ust},
            )


def remove_kategoriyalar(apps, schema_editor):
    Kategori = apps.get_model('core', 'Kategori')
    slugs = []
    for esas in KATEQORIYALAR:
        slugs.append(esas['slug'])
        slugs.extend(s for _, s in esas['alt'])
    Kategori.objects.filter(slug__in=slugs).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0010_add_vip_siralama_and_fix_kategori'),
    ]

    operations = [
        migrations.RunPython(seed_kategoriyalar, remove_kategoriyalar),
    ]
