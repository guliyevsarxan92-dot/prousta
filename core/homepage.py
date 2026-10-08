"""Presentation data for the reference homepage; examples never enter the database."""
CATEGORIES = [
    ('Elektrik', 'elektrik', '⚡'), ('Santexnika', 'santexnik', '🚰'),
    ('Kombi', 'kombi-ustasi', '♨'), ('Kondisioner', 'kondisioner-ustasi', '❄'),
    ('Mebel ustası', 'mebel-interyer', '🛋️'), ('Boya', 'malyar-ustasi', '🖌️'),
    ('Telefon təmiri', 'telefon-ustasi', '📱'), ('Tikinti', 'temir-tikinti', '🧱'),
]
EXAMPLE_SERVICES = [
    {'title': 'Kombi təmiri və yuyulması', 'description': 'Bütün növ kombilərin təmiri, yuyulması və quraşdırılması. Peşəkar xidmət.', 'district': 'Yasamal', 'price': 30, 'rating': '4.9', 'reviews': 124, 'slug': 'kombi-ustasi'},
    {'title': 'Peşəkar elektrik xidməti', 'description': 'Elektrik işləri, avtomatların quraşdırılması, priz və işıq sistemləri.', 'district': 'Nərimanov', 'price': 20, 'rating': '4.9', 'reviews': 98, 'slug': 'elektrik'},
    {'title': 'Kondisioner quraşdırılması', 'description': 'Kondisioner satışı, quraşdırılması, texniki servis və təmiri.', 'district': 'Xətai', 'price': 25, 'rating': '4.8', 'reviews': 76, 'slug': 'kondisioner-ustasi'},
    {'title': 'Mebel yığılması və təmiri', 'description': 'Mebellərin sökülməsi, yığılması və təmiri. Hər növ mebel üçün.', 'district': 'Nəsimi', 'price': 30, 'rating': '4.9', 'reviews': 111, 'slug': 'mebel-interyer'},
]
EXAMPLE_PROFESSIONALS = [
    {'name': 'Elçin Usta', 'job': 'Kombi ustası', 'rating': '4.9', 'reviews': 142, 'jobs': 320, 'slug': 'kombi-ustasi'},
    {'name': 'Ramin Usta', 'job': 'Elektrikçi', 'rating': '4.8', 'reviews': 96, 'jobs': 280, 'slug': 'elektrik'},
    {'name': 'Murad Usta', 'job': 'Santexnik', 'rating': '4.9', 'reviews': 118, 'jobs': 350, 'slug': 'santexnik'},
]
EXAMPLE_REVIEWS = [
    {'name': 'Nigar Məmmədova', 'when': '2 həftə əvvəl', 'text': 'Kombi ustasını çox rahat tapdım. Usta vaxtında gəldi və işi peşəkar şəkildə gördü. Çox razı qaldım!'},
    {'name': 'Tural İsmayılov', 'when': '1 ay əvvəl', 'text': 'Sayt çox rahatdır, istədiyim xidməti tez tapdım. Usta ilə birbaşa WhatsApp ilə əlaqə saxlamaq çox rahat oldu.'},
    {'name': 'Aysel Kərimova', 'when': '3 həftə əvvəl', 'text': 'Mebel ustası super idi! Gəldiyi gün bütün mebelləri yığdı. Peşəkar və mehriban xidmət. Tövsiyə edirəm.'},
]


def presentation_context(cards):
    professionals = []
    seen = set()
    for card in cards:
        if card.istifadeci_id not in seen:
            seen.add(card.istifadeci_id)
            professionals.append(card)
    return {
        'home_categories': CATEGORIES,
        'home_cards': cards,
        'home_professionals': professionals[:3],
        'home_is_demo': not cards,
        'example_services': EXAMPLE_SERVICES,
        'example_professionals': EXAMPLE_PROFESSIONALS,
        'example_reviews': EXAMPLE_REVIEWS,
    }
