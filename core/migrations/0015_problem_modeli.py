from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0014_fix_non_ascii_slugs'),
    ]

    operations = [
        migrations.CreateModel(
            name='Problem',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('bashliq', models.CharField(max_length=200)),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('metn', models.TextField(help_text='Problem haqqında ətraflı HTML mətn')),
                ('seo_title', models.CharField(blank=True, max_length=200)),
                ('seo_description', models.CharField(blank=True, max_length=300)),
                ('aktiv', models.BooleanField(db_index=True, default=True)),
                ('yaradildi', models.DateTimeField(auto_now_add=True)),
                ('yenilendi', models.DateTimeField(auto_now=True)),
                ('kategori', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='problemler', to='core.kategori')),
            ],
            options={
                'verbose_name': 'Problem',
                'verbose_name_plural': 'Problemlər',
                'ordering': ['-yaradildi'],
            },
        ),
    ]
