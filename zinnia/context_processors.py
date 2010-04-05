"""Context Processors for zinnia"""
from zinnia.settings import MEDIA_URL

def media(request):
    """Adds media-related context variables to the context"""
    return {'ZINNIA_MEDIA_URL': MEDIA_URL}
