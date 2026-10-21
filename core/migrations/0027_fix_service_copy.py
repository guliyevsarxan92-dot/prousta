"""Correct service copy without changing public URLs or replacing custom SEO text."""
import re

from django.db import migrations


NAME_FIXES = {
    'komputer-ustasi': ('Komputer ustası', 'Kompüter ustası'),
    'su-filteri-ustasi': ('Su filteri ustası', 'Su filtri ustası'),
    'dus-kabina': ('Duş kabina', 'Duş kabinəsi'),
    'su-sizma': ('Su sızma', 'Su sızmasının aşkarlanması'),
    'metbex-mebelleri': ('Mətbəx mebelləri quraşdırmaq', 'Mətbəx mebellərinin quraşdırılması'),
    'vitrin-yigmaq': ('Vitrin yığmaq', 'Vitrin yığılması'),
}


def clean_keyword_tail(text):
    # Only remove a final, standalone keyword line; keep the actual description.
    cleaned = re.sub(r'(?:\r?\n)[ \t]*Açar sözlər:[^\r\n]*(?:\r?\n[ \t]*)*\Z', '', text)
    return cleaned.rstrip() if cleaned.strip() and cleaned != text else text


def fix_generated_seo(text, name):
    lower = name.lower()
    replacements = {
        f'{name} xidmətinin əhatə dairəsi': f'{name} üzrə xidmətlər',
        f'Burada {lower} sahəsində işləyən': f'Burada {lower} üzrə xidmət göstərən',
        f'<strong>{lower}</strong> seçmək çox vacibdir.': f'<strong>{lower}</strong> üzrə mütəxəssis seçmək çox vacibdir.',
        f'Nə üçün Prousta.az-dan {lower} seçməlisiniz?': f'{name} üzrə mütəxəssisi niyə Prousta.az-da axtarmalısınız?',
        f'<strong>{lower}</strong> mütəxəssisləri': f'<strong>{lower}</strong> üzrə mütəxəssislər',
        f'{name} necə sifariş verə bilərəm?': f'{name} üzrə xidməti necə sifariş edə bilərəm?',
        f'Bəli, {lower}larımızın əksəriyyəti eyni gün ərzində, bəzən hətta 1-2 saat içində ünvana gələ bilir. Təcili hallar üçün elanda "təcili xidmət" qeydi olan ustalara üstünlük verin.':
            'Xidmətin vaxtını və yerini seçdiyiniz mütəxəssislə birbaşa razılaşdırın. Təcili xidmət lazımdırsa, uyğun elandakı əlaqə nömrəsi ilə müraciət edin.',
        '<div class="faq-q">Usta təcili gələ bilərmi?</div>':
            '<div class="faq-q">Təcili xidmət sifariş etmək olarmı?</div>',
        f'<strong>{name}</strong> xidmətinin qiyməti': f'<strong>{name}</strong> üzrə xidmətin qiyməti',
        '<li>Problemin pulsuz diaqnostikası və ilkin qiymətləndirmə</li>':
            '<li>İşin həcminin və qiymətinin əvvəlcədən razılaşdırılması</li>',
        '<li>Təcili çağırış — eyni gün ərzində ünvana gəlmə imkanı</li>':
            '<li>Xidmətin vaxtı və göstərilmə üsulunun razılaşdırılması</li>',
        '<li>Keyfiyyətli material və orijinal ehtiyat hissələri ilə işləmə</li>':
            '<li>Xidmətə uyğun iş nümunələri və təcrübə barədə məlumat</li>',
        '<li>Görülən işə yazılı zəmanət verilməsi</li>':
            '<li>Xidmət şərtlərinin mütəxəssislə dəqiqləşdirilməsi</li>',
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


def fix_copy(apps, schema_editor):
    Kategori = apps.get_model('core', 'Kategori')
    Elan = apps.get_model('core', 'Elan')
    alias = schema_editor.connection.alias
    for category in Kategori.objects.using(alias).all().iterator():
        old_name = category.ad
        expected, new_name = NAME_FIXES.get(category.slug, (old_name, old_name))
        # Do not overwrite category names that have already been customized.
        if old_name != expected:
            new_name = old_name
        changes = {}
        for field in ('seo_metn', 'seo_title', 'seo_description'):
            original = getattr(category, field)
            corrected = fix_generated_seo(original, old_name)
            if new_name != old_name:
                for old, new in ((old_name, new_name), (old_name.lower(), new_name.lower())):
                    corrected = re.sub(r'(?<!\w)' + re.escape(old) + r'(?!\w)', lambda match: new, corrected)
            if field == 'seo_title' and old_name == 'Digər ustalar':
                corrected = corrected.replace('Digər ustalar ustaları və xidmətləri', 'Digər ustalar və xidmətlər')
            if corrected != original:
                changes[field] = corrected
        if new_name != old_name:
            changes['ad'] = new_name
        if changes:
            Kategori.objects.using(alias).filter(pk=category.pk).update(**changes)

        # Only fix the known generated opening, leaving user descriptions intact.
        old_prefix = f'Peşəkar {old_name.lower()} xidməti Bakıda və ətraf rayonlarda. '
        ads = Elan.objects.using(alias).filter(kategori_id=category.pk, acaqlama__startswith=old_prefix)
        for ad in ads.iterator():
            description = f'{new_name} üzrə peşəkar xidmət Bakıda və ətraf rayonlarda. ' + ad.acaqlama[len(old_prefix):]
            description = description.replace('ünvanınıza usta yönləndiriləcək.', 'xidmətin yeri və vaxtı sizinlə razılaşdırılacaq.')
            Elan.objects.using(alias).filter(pk=ad.pk).update(acaqlama=description)

    for ad in Elan.objects.using(alias).filter(acaqlama__contains='Açar sözlər:').iterator():
        cleaned = clean_keyword_tail(ad.acaqlama)
        if cleaned != ad.acaqlama:
            Elan.objects.using(alias).filter(pk=ad.pk).update(acaqlama=cleaned)


class Migration(migrations.Migration):
    dependencies = [('core', '0026_shikayet_bloklama')]
    operations = [migrations.RunPython(fix_copy, migrations.RunPython.noop)]
