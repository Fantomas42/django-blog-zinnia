"""Context Processors for Zinnia"""
from zinnia import __version__


def version(request):
    """Adds version of Zinnia to the context"""
    return {'ZINNIA_VERSION': __version__}
