"""Apps for Zinnia"""
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class ZinniaConfig(AppConfig):
    """
    Config for Zinnia application.
    """
    name = 'zinnia'
    label = 'zinnia'
    verbose_name = _('Weblog')
