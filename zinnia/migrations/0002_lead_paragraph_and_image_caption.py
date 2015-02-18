from django.db import models
from django.db import migrations

from ..models import Entry
from ..models_bases.entry import LeadEntry, ImageEntry

operations = []
if issubclass(Entry, ImageEntry):
    operations.append(migrations.AddField(
        model_name='entry',
        name='image_caption',
        field=models.TextField(
            default='', help_text="Image's caption",
            verbose_name='caption', blank=True),
        preserve_default=False,))
if issubclass(Entry, LeadEntry):
    operations.append(migrations.AddField(
        model_name='entry',
        name='lead',
        field=models.TextField(
            default='', help_text='Lead paragraph',
            verbose_name='lead', blank=True),
        preserve_default=False))


class Migration(migrations.Migration):
    dependencies = [
        ('zinnia', '0001_initial'),
    ]

    operations = operations
