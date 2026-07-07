from django.conf import settings
from django.db import migrations


def set_default_site(apps, schema_editor):
    """Site (id=1) ni 'example.com' o'rniga DataScience.uz qilib o'rnatadi."""
    Site = apps.get_model('sites', 'Site')
    site_id = getattr(settings, 'SITE_ID', 1)
    Site.objects.update_or_create(
        id=site_id,
        defaults={'domain': 'data-science.uz', 'name': 'DataScience.uz'},
    )


def revert_default_site(apps, schema_editor):
    """Orqaga qaytarishda Django standart qiymatlariga qaytaradi."""
    Site = apps.get_model('sites', 'Site')
    site_id = getattr(settings, 'SITE_ID', 1)
    Site.objects.filter(id=site_id).update(domain='example.com', name='example.com')


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
        ('sites', '0002_alter_domain_unique'),
    ]

    operations = [
        migrations.RunPython(set_default_site, revert_default_site),
    ]
