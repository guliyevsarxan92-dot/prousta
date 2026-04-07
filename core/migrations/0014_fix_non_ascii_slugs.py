from django.db import migrations


def fix_slugs(apps, schema_editor):
    """Non-ASCII slug-ları ASCII-yə çevirir (Azərbaycan hərflərini map edir)."""
    Kategori = apps.get_model('core', 'Kategori')

    # Azərbaycan → ASCII mapping
    mapping = str.maketrans({
        'ə': 'e', 'Ə': 'e',
        'ı': 'i', 'İ': 'i',
        'ö': 'o', 'Ö': 'o',
        'ü': 'u', 'Ü': 'u',
        'ş': 's', 'Ş': 's',
        'ç': 'c', 'Ç': 'c',
        'ğ': 'g', 'Ğ': 'g',
        '\u0307': '',  # combining dot above (İ.lower() bunu yaradır)
    })

    for kat in Kategori.objects.all():
        try:
            kat.slug.encode('ascii')
            continue  # Slug onsuz da ASCII-dir
        except UnicodeEncodeError:
            pass

        new_slug = kat.slug.translate(mapping).lower()
        # Yoxla görək dublikat varmı
        if Kategori.objects.exclude(pk=kat.pk).filter(slug=new_slug).exists():
            # Dublikat var — yaxşı olanı saxla, bunu sil
            # Amma əvvəlcə SEO mətn daha uzundursa köçür
            existing = Kategori.objects.exclude(pk=kat.pk).get(slug=new_slug)
            if len(kat.seo_metn or '') > len(existing.seo_metn or ''):
                existing.seo_metn = kat.seo_metn
                existing.seo_title = kat.seo_title or existing.seo_title
                existing.seo_description = kat.seo_description or existing.seo_description
                existing.save()
            # Bu kateqoriyadakı elanları yaxşı kateqoriyaya köçür
            Elan = apps.get_model('core', 'Elan')
            Elan.objects.filter(kategori=kat).update(kategori=existing)
            kat.delete()
        else:
            kat.slug = new_slug
            kat.save()


def reverse_fix(apps, schema_editor):
    pass  # Geri dönüş lazım deyil


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0013_kategori_seo_metn_data'),
    ]

    operations = [
        migrations.RunPython(fix_slugs, reverse_fix),
    ]
