"""Breadcrumb module for Zinnia templatetags"""
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _

class Crumb(object):
    """Part of the Breadcrumbs"""
    def __init__(self, name, url=None):
        self.name = name
        self.url = url

zinnia_root_url = reverse('zinnia_entry_archive_index')

archives_crumb = Crumb(_('Archives'))
tags_crumb = Crumb(_('Tags'), reverse('zinnia_tag_list'))
authors_crumb = Crumb(_('Authors'), reverse('zinnia_author_list'))
categories_crumb = Crumb(_('Categories'), reverse('zinnia_category_list'))

MODEL_BREADCRUMBS = {'Tag': lambda x: [tags_crumb, Crumb(x.name)],
                     'User': lambda x: [authors_crumb, Crumb(x.username)],    
                     'Category': lambda x: [categories_crumb, Crumb(x.title)],
                     'Entry': lambda x: [Crumb(x.categories.all()[0].title,
                                               x.categories.all()[0].get_absolute_url()),
                                         Crumb(x.title)],
                     }

def retrieve_breadcrumbs(path, model_instance, root_name=''):
    """Build a semi-hardcoded breadcrumbs
    based of the model's url handled by Zinnia"""
    breadcrumbs = []
    
    if root_name:
        breadcrumbs.append(Crumb(root_name, zinnia_root_url))

    if model_instance is not None:
        key = model_instance.__class__.__name__
        if key in MODEL_BREADCRUMBS:
            breadcrumbs.extend(MODEL_BREADCRUMBS[key](model_instance))
            return breadcrumbs

    url_components = [comp for comp in path.split('/') if comp]
    if len(url_components) == 2:#Need to be changed
        breadcrumbs.append(Crumb(_(url_components[-1].capitalize())))
    elif len(url_components) > 2:#Idem
        breadcrumbs.append(archives_crumb)

    return breadcrumbs
    
