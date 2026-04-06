from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0011_seed_kategoriyalar'),
    ]

    operations = [
        migrations.AddField(
            model_name='kategori',
            name='seo_title',
            field=models.CharField(blank=True, max_length=200),
        ),
        migrations.AddField(
            model_name='kategori',
            name='seo_description',
            field=models.CharField(blank=True, max_length=300),
        ),
        migrations.AddField(
            model_name='kategori',
            name='seo_metn',
            field=models.TextField(blank=True, help_text='Kateqoriya səhifəsinin altında göstəriləcək SEO üçün HTML mətn'),
        ),
    ]
