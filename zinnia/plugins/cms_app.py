"""Applications hooks for zinnia.plugins"""
from django.utils.translation import ugettext_lazy as _

from cms.app_base import CMSApp
from cms.apphook_pool import apphook_pool

from zinnia.plugins.settings import APP_MENUS

class ZinniaApphook(CMSApp):
    name = _('Zinnia App Hook')
    urls = ['zinnia.urls']
    menus = APP_MENUS

apphook_pool.register(ZinniaApphook)
