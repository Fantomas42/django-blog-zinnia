# -*- coding: utf-8 -*-

"""
A simple example of using ZINNIA_IMAGE_FIELD to set Entry.image as ForeignKey to other model
"""

from django.conf import settings
from django.db.models import SET_NULL
from django.utils.translation import ugettext_lazy as _

if 'filer' in settings.INSTALLED_APPS:
    from filer.fields.image import FilerImageField
    ZINNIA_IMAGE_FIELD = FilerImageField(
        blank=True,
        null=True,
        related_name='entry_illustration',
        help_text=_('Used for illustration.'),
        db_column='image',
        on_delete=SET_NULL,
        default=None,)
