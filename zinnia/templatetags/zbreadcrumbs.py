"""Breadcrumb module for Zinnia templatetags"""
import re
from datetime import datetime

from django.core.urlresolvers import reverse
from django.utils.translation import ugettext as _


class Crumb(object):
    """Part of the Breadcrumbs"""
    def __init__(self, name, url=None):
        self.name = name
        self.url = url


def year_crumb(datetime):
    year = datetime.strftime('%Y')
    return Crumb(year, reverse('zinnia_entry_archive_year',
                               args=[year]))


def month_crumb(datetime):
    year = datetime.strftime('%Y')
    month = datetime.strftime('%m')
    month_text = datetime.strftime('%b').capitalize()
    return Crumb(month_text, reverse('zinnia_entry_archive_month',
                                     args=[year, month]))


def day_crumb(datetime):
    year = datetime.strftime('%Y')
    month = datetime.strftime('%m')
    day = datetime.strftime('%d')
    return Crumb(day, reverse('zinnia_entry_archive_day',
                              args=[year, month, day]))


zinnia_root_url = reverse('zinnia_entry_archive_index')

archives_crumb = Crumb(_('Archives'))
tags_crumb = Crumb(_('Tags'), reverse('zinnia_tag_list'))
authors_crumb = Crumb(_('Authors'), reverse('zinnia_author_list'))
categories_crumb = Crumb(_('Categories'), reverse('zinnia_category_list'))

MODEL_BREADCRUMBS = {'Tag': lambda x: [tags_crumb, Crumb(x.name)],
                     'User': lambda x: [authors_crumb, Crumb(x.username)],
                     'Category': lambda x: [categories_crumb] + \
                                           [Crumb(anc.title, anc.get_absolute_url())
                                            for anc in x.get_ancestors()] + \
                                           [Crumb(x.title)],
                     'Entry': lambda x: [year_crumb(x.creation_date),
                                         month_crumb(x.creation_date),
                                         day_crumb(x.creation_date),
                                         Crumb(x.title)]}

DATE_REGEXP = re.compile(r'.*(?P<year>\d{4})/(?P<month>\d{2})?/(?P<day>\d{2})?.*')


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

    date_match = DATE_REGEXP.match(path)
    if date_match:
        date_dict = date_match.groupdict()
        path_date = datetime(
            int(date_dict['year']),
            date_dict.get('month') is not None and int(date_dict.get('month')) or 1,
            date_dict.get('day') is not None and int(date_dict.get('day')) or 1)

        date_breadcrumbs = [year_crumb(path_date)]
        if date_dict['month']:
            date_breadcrumbs.append(month_crumb(path_date))
        if date_dict['day']:
            date_breadcrumbs.append(day_crumb(path_date))
        breadcrumbs.extend(date_breadcrumbs)

        return breadcrumbs

    url_components = [comp for comp in
                      path.replace(zinnia_root_url, '').split('/') if comp]
    if len(url_components):
        breadcrumbs.append(Crumb(_(url_components[-1].capitalize())))

    return breadcrumbs
