"""
core/locations.py
Bakı, Abşeron və ətraf şəhərlər üçün Lokal SEO rayon və qəsəbələr kataloqu.
Hər bir lokasiya üzrə xidmət səhifələrinin (/xidmet/<slug>/<lokasiya>/)
və Google Local SEO axtarışlarının optimizasiyası üçün istifadə olunur.
"""

LOKASIYALAR = {
    'yasamal': {
        'slug': 'yasamal',
        'ad': 'Yasamal',
        'tam_ad': 'Yasamal rayonu',
        'erazi': 'Elmlər Akademiyası, İnşaatçılar, 20 Yanvar, Yeni Yasamal, Şamaxinka',
        'keywords': ['yasamal', 'elmler', 'insaatcilar', 'yeni yasamal'],
    },
    'nerimanov': {
        'slug': 'nerimanov',
        'ad': 'Nərimanov',
        'tam_ad': 'Nərimanov rayonu',
        'erazi': 'Nərimanov metrosu, Gənclik, Montin, Koroğlu, Təbriz küçəsi',
        'keywords': ['nerimanov', 'nərimanov', 'genclik', 'gənclik', 'montin'],
    },
    'nesimi': {
        'slug': 'nesimi',
        'ad': 'Nəsimi',
        'tam_ad': 'Nəsimi rayonu',
        'erazi': '28 May, Memar Əcəmi, Nəsimi bazarı, Tibb Universiteti, Cəfər Cabbarlı',
        'keywords': ['nesimi', 'nəsimi', '28 may', 'ecemi', 'əcəmi'],
    },
    'xetai': {
        'slug': 'xetai',
        'ad': 'Xətai',
        'tam_ad': 'Xətai rayonu',
        'erazi': 'Əhmədli, Həzi Aslanov, Xətai metrosu, Ağ Şəhər, Köhnə Günəşli',
        'keywords': ['xetai', 'xətai', 'ehmedli', 'əhmədli', 'hezi aslanov', 'həzi aslanov'],
    },
    'bineqedi': {
        'slug': 'bineqedi',
        'ad': 'Binəqədi',
        'tam_ad': 'Binəqədi rayonu',
        'erazi': '6-cı, 7-ci, 8-ci, 9-cu mikrorayonlar, Azadlıq prospekti, Rəsulzadə, Biləcəri',
        'keywords': ['bineqedi', 'binəqədi', 'azadliq', 'mkr', 'bileceri', 'biləcəri'],
    },
    'nizami': {
        'slug': 'nizami',
        'ad': 'Nizami',
        'tam_ad': 'Nizami rayonu',
        'erazi': 'Neftçilər, Qara Qarayev, Xalqlar Dostluğu, 8-ci kilometr',
        'keywords': ['nizami', 'neftciler', 'neftçilər', 'qarayev', 'xalqlar'],
    },
    'sebail': {
        'slug': 'sebail',
        'ad': 'Səbail',
        'tam_ad': 'Səbail rayonu',
        'erazi': 'Sahil, İçərişəhər, Badamdar, Bayıl, Fəvvarələr meydanı',
        'keywords': ['sebail', 'səbail', 'sahil', 'badamdar', 'bayil', 'bayıl'],
    },
    'sabuncu': {
        'slug': 'sabuncu',
        'ad': 'Sabunçu',
        'tam_ad': 'Sabunçu rayonu',
        'erazi': 'Bakıxanov (Razin), Zabrat, Maştağa, Sabunçu qəsəbəsi, Pirşağı',
        'keywords': ['sabuncu', 'sabunçu', 'bakixanov', 'bakıxanov', 'razin', 'zabrat', 'mastaga'],
    },
    'suraxani': {
        'slug': 'suraxani',
        'ad': 'Suraxanı',
        'tam_ad': 'Suraxanı rayonu',
        'erazi': 'Qaraçuxur, Yeni Günəşli, Əmircan, Bülbülə, Hövsan',
        'keywords': ['suraxani', 'suraxanı', 'qaracuxur', 'qaraçuxur', 'yeni gunesli', 'hovsan'],
    },
    'xezer': {
        'slug': 'xezer',
        'ad': 'Xəzər',
        'tam_ad': 'Xəzər rayonu',
        'erazi': 'Mərdəkan, Şüvəlan, Binə, Buzovna, Qala, Şağan',
        'keywords': ['xezer', 'xəzər', 'merdekan', 'mərdəkan', 'suvelan', 'şüvəlan', 'bine', 'buzovna'],
    },
    'qaradag': {
        'slug': 'qaradag',
        'ad': 'Qaradağ',
        'tam_ad': 'Qaradağ rayonu',
        'erazi': 'Lökbatan, Sahil qəsəbəsi, Qobu, Sədərək ərazisi',
        'keywords': ['qaradag', 'qaradağ', 'lokbatan', 'lökbatan', 'sahil qesebesi'],
    },
    'xirdalan': {
        'slug': 'xirdalan',
        'ad': 'Xırdalan',
        'tam_ad': 'Xırdalan şəhəri',
        'erazi': 'Xırdalan şəhəri, AAAF Park, Heydər Əliyev prospekti, Riyad',
        'keywords': ['xirdalan', 'xırdalan', 'aaaf park', 'abseron', 'abşeron'],
    },
    'masazir': {
        'slug': 'masazir',
        'ad': 'Masazır',
        'tam_ad': 'Masazır qəsəbəsi',
        'erazi': 'Qurtuluş 93, Yeni Bakı, Masazır dairəsi, Duz gölü ətrafı',
        'keywords': ['masazir', 'masazır', 'qurtulus', 'yeni baki'],
    },
    'sumqayit': {
        'slug': 'sumqayit',
        'ad': 'Sumqayıt',
        'tam_ad': 'Sumqayıt şəhəri',
        'erazi': 'Sumqayıt şəhəri, bütün mikrorayonlar və məhəllələr, Dənizkənarı bulvar',
        'keywords': ['sumqayit', 'sumqayıt', 'sumgayit'],
    },
    'saray': {
        'slug': 'saray',
        'ad': 'Saray',
        'tam_ad': 'Saray qəsəbəsi',
        'erazi': 'Saray qəsəbəsi, Saray bağları, Sumqayıt şosesi',
        'keywords': ['saray'],
    },
    'mehdiabad': {
        'slug': 'mehdiabad',
        'ad': 'Mehdiabad',
        'tam_ad': 'Mehdiabad qəsəbəsi',
        'erazi': 'Mehdiabad, Digah, Məmmədli ərazisi',
        'keywords': ['mehdiabad', 'digah'],
    },
}

POPULAR_LOKASIYALAR = [
    'yasamal', 'nerimanov', 'nesimi', 'xetai', 'bineqedi',
    'nizami', 'xirdalan', 'sumqayit', 'masazir', 'sabuncu'
]


def get_lokasiya(slug: str):
    """Verilmiş slug üzrə lokasiya lüğətini qaytarır."""
    if not slug:
        return None
    return LOKASIYALAR.get(slug.lower().strip())
