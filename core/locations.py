"""
core/locations.py
Bakı, Abşeron və ətraf şəhərlər üçün Lokal SEO rayon, qəsəbə, mikrorayon və metro kataloqu.
Hər bir lokasiya üzrə xidmət səhifələrinin (/xidmet/<slug>/<lokasiya>/)
və Google Local SEO axtarışlarının optimizasiyası üçün istifadə olunur.
"""

LOKASIYALAR = {
    'yasamal': {
        'slug': 'yasamal',
        'ad': 'Yasamal',
        'tam_ad': 'Yasamal rayonu',
        'erazi': 'Yeni Yasamal, Elmlər Akademiyası, İnşaatçılar, 20 Yanvar, Nizami metrosu, Şamaxinka, Sovetski, Yasamal bazarı, Tbilisi prospekti, Mətbuat prospekti, Şərifzadə küçəsi',
        'qesebeler': [
            'Yeni Yasamal', 'Elmlər Akademiyası', 'İnşaatçılar', '20 Yanvar',
            'Nizami metrosu', 'Şamaxinka', 'Sovetski', 'Tbilisi prospekti',
            'Mətbuat prospekti', 'Şərifzadə', 'Həsən bəy Zərdabi', 'Qələbə dairəsi',
        ],
        'keywords': [
            'yasamal', 'yeni yasamal', 'elmler', 'elmler akademiyasi', 'insaatcilar',
            '20 yanvar', 'samaxinka', 'şamaxinka', 'sovetski', 'serifzade', 'şərifzadə',
            'metbuat', 'mətbuat', 'qelebe dairesi', 'tbilisi prospekti',
        ],
    },
    'nerimanov': {
        'slug': 'nerimanov',
        'ad': 'Nərimanov',
        'tam_ad': 'Nərimanov rayonu',
        'erazi': 'Nəriman Nərimanov metrosu, Gənclik, Ulduz, Montin, Keşlə qəsəbəsi, Böyükşor, Bakmil, Təbriz küçəsi, Ağa Nemətulla, Heydər Əliyev Mərkəzi, Dərnəgül şosesi, Atatürk prospekti',
        'qesebeler': [
            'Nərimanov metrosu', 'Gənclik', 'Montin', 'Keşlə', 'Ulduz metrosu',
            'Bakmil', 'Böyükşor', 'Təbriz küçəsi', 'Ağa Nemətulla', 'Atatürk prospekti',
            'Əhməd Rəcəbli', 'Çermet',
        ],
        'keywords': [
            'nerimanov', 'nərimanov', 'genclik', 'gənclik', 'montin', 'kesle', 'keşlə',
            'ulduz', 'bakmil', 'boyuksor', 'böyükşor', 'tebriz', 'təbriz',
            'aga nemetulla', 'ehmed recebli', 'əhməd rəcəbli', 'cermet',
        ],
    },
    'nesimi': {
        'slug': 'nesimi',
        'ad': 'Nəsimi',
        'tam_ad': 'Nəsimi rayonu',
        'erazi': '28 May, Memar Əcəmi, Cəfər Cabbarlı, 1-ci, 2-ci, 3-cü, 4-cü və 5-ci mikrorayonlar, Xutor, Papanin (8 Noyabr metrosu), Kubinka, Nəsimi bazarı, Tibb Universiteti, Azadlıq prospekti, Səməd Vurğun',
        'qesebeler': [
            '28 May', 'Memar Əcəmi', '1-ci mikrorayon', '2-ci mikrorayon', '3-cü mikrorayon',
            '4-cü mikrorayon', '5-ci mikrorayon', 'Xutor', 'Papanin (8 Noyabr)',
            'Kubinka', 'Cəfər Cabbarlı', 'Nəsimi bazarı', 'Tibb Universiteti', 'Qış parkı',
        ],
        'keywords': [
            'nesimi', 'nəsimi', '28 may', 'ecemi', 'əcəmi', 'memar ecemi',
            '1-ci mkr', '2-ci mkr', '3-cu mkr', '4-cu mkr', '5-ci mkr',
            '1 mkr', '2 mkr', '3 mkr', '4 mkr', '5 mkr',
            'xutor', 'papanin', '8 noyabr', 'kubinka', 'cefer cabbarli', 'tibb universiteti',
        ],
    },
    'xetai': {
        'slug': 'xetai',
        'ad': 'Xətai',
        'tam_ad': 'Xətai rayonu',
        'erazi': 'Əhmədli, Həzi Aslanov, Xətai metrosu, Ağ Şəhər (White City), Köhnə Günəşli, NZS (UPD) qəsəbəsi, Nobel prospekti (8 Noyabr prospekti), Babək prospekti, Ukrayna dairəsi, Gəncə prospekti, Neapol dairəsi, Zığ şosesi',
        'qesebeler': [
            'Əhmədli', 'Həzi Aslanov', 'Xətai metrosu', 'Ağ Şəhər', 'Köhnə Günəşli',
            'NZS qəsəbəsi', 'UPD', 'Babək prospekti', 'Ukrayna dairəsi',
            'Gəncə prospekti', 'Neapol dairəsi', '8 Noyabr prospekti (Nobel)', 'Nargilə',
        ],
        'keywords': [
            'xetai', 'xətai', 'ehmedli', 'əhmədli', 'hezi aslanov', 'həzi aslanov',
            'ag seher', 'ağ şəhər', 'kohne gunesli', 'köhnə günəşli', 'nzs', 'upd',
            'ukrayna dairesi', 'gence prospekti', 'neapol dairesi', 'babek prospekti', 'nargile',
        ],
    },
    'bineqedi': {
        'slug': 'bineqedi',
        'ad': 'Binəqədi',
        'tam_ad': 'Binəqədi rayonu',
        'erazi': '6-cı, 7-ci, 8-ci və 9-cu mikrorayonlar, Azadlıq prospekti metrosu, Dərnəgül, Avtovağzal, Biləcəri qəsəbəsi, M.Ə.Rəsulzadə (Kirov) qəsəbəsi, Xocəsən, Sulutəpə, Binəqədi qəsəbəsi, 28 May qəsəbəsi, Vorovski, Çiçək qəsəbəsi, Motodrom',
        'qesebeler': [
            '6-cı mikrorayon', '7-ci mikrorayon', '8-ci mikrorayon', '9-cu mikrorayon',
            'Biləcəri', 'Rəsulzadə (Kirov)', 'Xocəsən', 'Sulutəpə', 'Binəqədi qəsəbəsi',
            'Azadlıq prospekti', 'Dərnəgül', 'Avtovağzal', 'Vorovski', '28 May qəsəbəsi',
        ],
        'keywords': [
            'bineqedi', 'binəqədi', 'azadliq', 'azadliq prospekti', 'dernegul', 'dərnəgül',
            'avtovagzal', 'avtovağzal', 'bileceri', 'biləcəri', 'resulzade', 'rəsulzadə',
            'kirov', 'xocasen', 'xocəsən', 'sulutepe', 'sulutəpə', 'vorovski',
            '6-ci mkr', '7-ci mkr', '8-ci mkr', '9-cu mkr', '6 mkr', '7 mkr', '8 mkr', '9 mkr',
        ],
    },
    'nizami': {
        'slug': 'nizami',
        'ad': 'Nizami',
        'tam_ad': 'Nizami rayonu',
        'erazi': 'Qara Qarayev, Neftçilər, Xalqlar Dostluğu, Koroğlu metrosu, 8-ci kilometr (8 km / Vasmoy), Keşlə, Babək prospekti, Özbəkistan küçəsi, Şərifli, Çobanzadə küçəsi',
        'qesebeler': [
            'Qara Qarayev', 'Neftçilər', 'Xalqlar Dostluğu', 'Koroğlu metrosu',
            '8-ci kilometr (8 km)', 'Vasmoy', 'Çobanzadə', 'Şərifli', 'Qarayev prospekti',
        ],
        'keywords': [
            'nizami', 'neftciler', 'neftçilər', 'qarayev', 'qara qarayev',
            'xalqlar', 'xalqlar dostlugu', 'koroglu', 'koroğlu', '8 km', '8-ci km',
            '8-ci kilometr', 'vasmoy', 'cobanzade', 'çobanzadə', 'serifli',
        ],
    },
    'sebail': {
        'slug': 'sebail',
        'ad': 'Səbail',
        'tam_ad': 'Səbail rayonu',
        'erazi': 'Sahil metrosu, İçərişəhər, Badamdar qəsəbəsi, Bayıl, Bibiheybət, 20-ci sahə, Şıxov (Şıx), Fəvvarələr meydanı (Tarqovı), Bulvar, Parlament prospekti, Neftçilər prospekti',
        'qesebeler': [
            'Sahil', 'İçərişəhər', 'Badamdar', 'Bayıl', 'Bibiheybət',
            '20-ci sahə', 'Şıxov', 'Fəvvarələr meydanı (Tarqovı)', 'Azneft',
        ],
        'keywords': [
            'sebail', 'səbail', 'sahil', 'iceriseher', 'içərişəhər', 'badamdar',
            'bayil', 'bayıl', 'bibiheybet', 'bibiheybət', '20-ci sahe', '20 ci sahe',
            'sixov', 'şıxov', 'tarqovi', 'tarqovu', 'azneft',
        ],
    },
    'sabuncu': {
        'slug': 'sabuncu',
        'ad': 'Sabunçu',
        'tam_ad': 'Sabunçu rayonu',
        'erazi': 'Bakıxanov (Razin), Sabunçu qəsəbəsi, Zabrat 1 və Zabrat 2, Maştağa, Ramana (Yeni Ramana, Şuşa şəhərciyi), Balaxanı, Bilgəh, Nardaran (Ləhiş bağları), Pirşağı, Kürdəxanı, Savalan, Albalılıq (Vişnyovka)',
        'qesebeler': [
            'Bakıxanov (Razin)', 'Zabrat', 'Maştağa', 'Ramana', 'Yeni Ramana',
            'Sabunçu qəsəbəsi', 'Balaxanı', 'Bilgəh', 'Nardaran', 'Pirşağı',
            'Kürdəxanı', 'Savalan', 'Albalılıq (Vişnyovka)', 'Ləhiş bağları',
        ],
        'keywords': [
            'sabuncu', 'sabunçu', 'bakixanov', 'bakıxanov', 'razin', 'zabrat',
            'mastaga', 'maştağa', 'ramana', 'ramani', 'yeni ramana', 'balaxani', 'balaxanı',
            'bilgeh', 'bilgəh', 'nardaran', 'pirsagi', 'pirşağı', 'kurdexani', 'kürdəxanı',
            'savalan', 'albaliliq', 'visnyovka', 'vişnyovka', 'lehis', 'ləhiş',
        ],
    },
    'suraxani': {
        'slug': 'suraxani',
        'ad': 'Suraxanı',
        'tam_ad': 'Suraxanı rayonu',
        'erazi': 'Qaraçuxur, Yeni Günəşli (A, B, D, V, Q massivləri), Hövsan qəsəbəsi, Əmircan, Bülbülə, Zığ, Yeni Suraxanı, Dədə Qorqud qəsəbəsi, Bahar qəsəbəsi',
        'qesebeler': [
            'Qaraçuxur', 'Yeni Günəşli', 'Hövsan', 'Əmircan', 'Bülbülə',
            'Zığ', 'Yeni Suraxanı', 'Dədə Qorqud', 'Bahar qəsəbəsi',
        ],
        'keywords': [
            'suraxani', 'suraxanı', 'qaracuxur', 'qaraçuxur', 'yeni gunesli',
            'yeni günəşli', 'gunesli', 'günəşli', 'hovsan', 'hövsan', 'emircan', 'əmircan',
            'bulbule', 'bülbülə', 'zig', 'zığ', 'yeni suraxani', 'dede qorqud',
        ],
    },
    'xezer': {
        'slug': 'xezer',
        'ad': 'Xəzər',
        'tam_ad': 'Xəzər rayonu',
        'erazi': 'Mərdəkan, Şüvəlan, Binə qəsəbəsi (Binə Sovxoz, Atçılıq), Buzovna, Qala, Şağan, Türkan, Zirə, Dübəndi, Zağulba',
        'qesebeler': [
            'Mərdəkan', 'Şüvəlan', 'Binə qəsəbəsi', 'Buzovna', 'Qala',
            'Şağan', 'Türkan', 'Zirə', 'Dübəndi', 'Zağulba',
        ],
        'keywords': [
            'xezer', 'xəzər', 'merdekan', 'mərdəkan', 'suvelan', 'şüvəlan',
            'bine', 'binə', 'bine qesebesi', 'buzovna', 'qala', 'sagan', 'şağan',
            'turkan', 'türkan', 'zire', 'zirə', 'dubendi', 'dübəndi', 'zagulba', 'zağulba',
        ],
    },
    'qaradag': {
        'slug': 'qaradag',
        'ad': 'Qaradağ',
        'tam_ad': 'Qaradağ rayonu',
        'erazi': 'Lökbatan, Sahil qəsəbəsi (Primorsk), Müşfiqabad, Qobu, Puta, Ələt, Səngəçal, Qobustan qəsəbəsi, Korgöz, Şubanı, Kızıldaş, Ümid qəsəbəsi, Sədərək və Binə Ticarət Mərkəzi',
        'qesebeler': [
            'Lökbatan', 'Sahil qəsəbəsi', 'Müşfiqabad', 'Qobu', 'Ələt',
            'Səngəçal', 'Qobustan', 'Puta', 'Korgöz', 'Ümid qəsəbəsi', 'Sədərək',
        ],
        'keywords': [
            'qaradag', 'qaradağ', 'lokbatan', 'lökbatan', 'sahil qesebesi', 'primorsk',
            'musfiqabad', 'müşfiqabad', 'qobu', 'elet', 'ələt', 'sengecal', 'səngəçal',
            'qobustan', 'puta', 'korgoz', 'sederek', 'sədərək',
        ],
    },
    'pirallahi': {
        'slug': 'pirallahi',
        'ad': 'Pirallahı',
        'tam_ad': 'Pirallahı rayonu',
        'erazi': 'Pirallahı qəsəbəsi (Artyom), Gürgən, Çilov, Neft Daşları',
        'qesebeler': [
            'Pirallahı qəsəbəsi', 'Gürgən', 'Çilov',
        ],
        'keywords': ['pirallahi', 'pirallahı', 'artyom', 'gurgen', 'gürgən'],
    },
    'xirdalan': {
        'slug': 'xirdalan',
        'ad': 'Xırdalan',
        'tam_ad': 'Xırdalan şəhəri',
        'erazi': 'Xırdalan şəhəri, AAAF Park, Kristal Abşeron, Heydər Əliyev prospekti, Riyad, Sulutəpə dairəsi, Hökməli, Qobu Park, Aşağı Güzdək, Ceyranbatan, Quşçuluq massivi',
        'qesebeler': [
            'Xırdalan mərkəz', 'AAAF Park', 'Kristal Abşeron', 'Hökməli',
            'Ceyranbatan', 'Aşağı Güzdək', 'Qobu Park', 'Riyad', 'Quşçuluq',
        ],
        'keywords': [
            'xirdalan', 'xırdalan', 'aaaf park', 'kristal abseron', 'abseron', 'abşeron',
            'hokmeli', 'hökməli', 'ceyranbatan', 'guzdek', 'güzdək', 'qobu park', 'qusculuq',
        ],
    },
    'masazir': {
        'slug': 'masazir',
        'ad': 'Masazır',
        'tam_ad': 'Masazır qəsəbəsi',
        'erazi': 'Masazır qəsəbəsi, Qurtuluş 93, Yeni Bakı yaşayış kompleksi, Əliağa Vahid, Masazır dairəsi, Duz gölü ətrafı, Villa Badam, Cantəpə',
        'qesebeler': [
            'Masazır mərkəz', 'Qurtuluş 93', 'Yeni Bakı', 'Masazır dairəsi',
            'Duz gölü', 'Cantəpə',
        ],
        'keywords': [
            'masazir', 'masazır', 'qurtulus', 'qurtulus 93', 'yeni baki',
            'duz golu', 'cantepe', 'cantəpə',
        ],
    },
    'sumqayit': {
        'slug': 'sumqayit',
        'ad': 'Sumqayıt',
        'tam_ad': 'Sumqayıt şəhəri',
        'erazi': 'Sumqayıt şəhəri (1-18-ci mikrorayonlar, 1-52-ci məhəllələr), Hacı Zeynalabdin Tağıyev (Nasosnu), Corat, Novxanı bağları, Yaşma, Stansiya Sumqayıt, Kimyaçılar, İnşaatçılar, Yaşıl Dərə, Dənizkənarı bulvar',
        'qesebeler': [
            'Sumqayıt mikrorayonlar', 'Corat', 'H.Z.Tağıyev (Nasosnu)', 'Novxanı',
            'Yaşیل Dərə', 'Stansiya Sumqayıt', 'Kimyaçılar', 'Yaşma',
        ],
        'keywords': [
            'sumqayit', 'sumqayıt', 'sumgayit', 'corat', 'nasosnu', 'tagiyev',
            'novxani', 'novxanı', 'yasil dere', 'yaşıl dərə', 'yasma',
        ],
    },
    'saray': {
        'slug': 'saray',
        'ad': 'Saray',
        'tam_ad': 'Saray qəsəbəsi',
        'erazi': 'Saray qəsəbəsi, Saray MTK, Saray bağları, Yeni Saray, Sumqayıt şosesi, Görədil bağları',
        'qesebeler': [
            'Saray qəsəbəsi', 'Saray MTK', 'Saray bağları', 'Görədil',
        ],
        'keywords': ['saray', 'saray qesebesi', 'saray mtk', 'goredil', 'görədil'],
    },
    'mehdiabad': {
        'slug': 'mehdiabad',
        'ad': 'Mehdiabad',
        'tam_ad': 'Mehdiabad qəsəbəsi',
        'erazi': 'Mehdiabad qəsəbəsi, Digah, Fatmayı, Məmmədli (Məhəmmədli), Гоradil, Binəqədi-Novxanı yolu',
        'qesebeler': [
            'Mehdiabad', 'Digah', 'Fatmayı', 'Məmmədli (Məhəmmədli)', 'Görədil',
        ],
        'keywords': [
            'mehdiabad', 'digah', 'fatmayi', 'fatmayı', 'memmedli', 'məmmədli',
            'mehemmedi', 'məhəmmədi',
        ],
    },
}

POPULAR_LOKASIYALAR = [
    'yasamal', 'nerimanov', 'nesimi', 'xetai', 'bineqedi',
    'nizami', 'xirdalan', 'sumqayit', 'masazir', 'sabuncu',
    'suraxani', 'xezer', 'qaradag', 'sebail', 'saray', 'mehdiabad',
]

BAKI_RAYONLARI = [
    'yasamal', 'nerimanov', 'nesimi', 'xetai', 'bineqedi', 'nizami',
    'sebail', 'sabuncu', 'suraxani', 'xezer', 'qaradag', 'pirallahi',
]

ETRAF_ERAZILER = [
    'xirdalan', 'masazir', 'sumqayit', 'saray', 'mehdiabad',
]


def get_lokasiya(slug: str):
    """Verilmiş slug üzrə lokasiya lüğətini qaytarır."""
    if not slug:
        return None
    return LOKASIYALAR.get(slug.lower().strip())


def grouped_lokasiyalar():
    """Elan forması üçün qruplaşdırılmış rayon və qəsəbə siyahısı."""
    return [
        ('Bakı rayonları', [LOKASIYALAR[s] for s in BAKI_RAYONLARI if s in LOKASIYALAR]),
        ('Abşeron və ətraf ərazilər', [LOKASIYALAR[s] for s in ETRAF_ERAZILER if s in LOKASIYALAR]),
    ]


def all_baku_settlement_groups():
    """Bütün Bakı rayonları və Abşeron üzrə qəsəbə/mikrorayon/metro bələdçisi."""
    return [LOKASIYALAR[s] for s in (*BAKI_RAYONLARI, *ETRAF_ERAZILER) if s in LOKASIYALAR]
