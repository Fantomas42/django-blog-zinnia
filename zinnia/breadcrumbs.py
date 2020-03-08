"""Breadcrumb module for Zinnia"""
import re
from datetime import datetime
from functools import wraps

from django.urls import reverse
from django.utils.dateformat import DateFormat
from django.utils.timezone import is_aware
from django.utils.timezone import localtime
from django.utils.translation import gettext as _


class Crumb(object):
    """
    Part of the breadcrumbs.
    """
    def __init__(self, name, url=None):
        self.name = name
        self.url = url


def year_crumb(date):
    """
    Crumb for a year.
    """
    year = date.strftime('%Y')
    return Crumb(year, reverse('zinnia:entry_archive_year',
                               args=[year]))


def month_crumb(date):
    """
    Crumb for a month.
    """
    year = date.strftime('%Y')
    month = date.strftime('%m')
    month_text = DateFormat(date).format('F').capitalize()
    return Crumb(month_text, reverse('zinnia:entry_archive_month',
                                     args=[year, month]))


def day_crumb(date):
    """
    Crumb for a day.
    """
    year = date.strftime('%Y')
    month = date.strftime('%m')
    day = date.strftime('%d')
    return Crumb(day, reverse('zinnia:entry_archive_day',
                              args=[year, month, day]))


def entry_breadcrumbs(entry):
    """
    Breadcrumbs for an Entry.
    """
    date = entry.publication_date
    if is_aware(date):
        date = localtime(date)
    return [year_crumb(date), month_crumb(date),
            day_crumb(date), Crumb(entry.title)]


MODEL_BREADCRUMBS = {'Tag': lambda x: [Crumb(_('Tags'),
                                             reverse('zinnia:tag_list')),
                                       Crumb(x.name)],
                     'Author': lambda x: [Crumb(_('Authors'),
                                                reverse('zinnia:author_list')),
                                          Crumb(x.__str__())],
                     'Category': lambda x: [Crumb(
                         _('Categories'), reverse('zinnia:category_list'))] +
                     [Crumb(anc.__str__(), anc.get_absolute_url())
                      for anc in x.get_ancestors()] + [Crumb(x.title)],
                     'Entry': entry_breadcrumbs}

ARCHIVE_REGEXP = re.compile(
    r'.*(?P<year>\d{4})/(?P<month>\d{2})?/(?P<day>\d{2})?.*')

ARCHIVE_WEEK_REGEXP = re.compile(
    r'.*(?P<year>\d{4})/week/(?P<week>\d+)?.*')

PAGE_REGEXP = re.compile(r'page/(?P<page>\d+).*$')


def handle_page_crumb(func):
    """
    Decorator for handling the current page in the breadcrumbs.
    """
    @wraps(func)
    def wrapper(path, model, page, root_name):
        path = PAGE_REGEXP.sub('', path)
        breadcrumbs = func(path, model, root_name)
        if page:
            if page.number > 1:
                breadcrumbs[-1].url = path
                page_crumb = Crumb(_('Page %s') % page.number)
                breadcrumbs.append(page_crumb)
        return breadcrumbs
    return wrapper


@handle_page_crumb
def retrieve_breadcrumbs(path, model_instance, root_name=''):
    """
    Build a semi-hardcoded breadcrumbs
    based of the model's url handled by Zinnia.
    """
    breadcrumbs = []
    zinnia_root_path = reverse('zinnia:entry_archive_index')

    if root_name:
        breadcrumbs.append(Crumb(root_name, zinnia_root_path))

    if model_instance is not None:
        key = model_instance.__class__.__name__
        if key in MODEL_BREADCRUMBS:
            breadcrumbs.extend(MODEL_BREADCRUMBS[key](model_instance))
            return breadcrumbs

    date_match = ARCHIVE_WEEK_REGEXP.match(path)
    if date_match:
        year, week = date_match.groups()
        year_date = datetime(int(year), 1, 1)
        date_breadcrumbs = [year_crumb(year_date),
                            Crumb(_('Week %s') % week)]
        breadcrumbs.extend(date_breadcrumbs)
        return breadcrumbs

    date_match = ARCHIVE_REGEXP.match(path)
    if date_match:
        date_dict = date_match.groupdict()
        path_date = datetime(
            int(date_dict['year']),
            date_dict.get('month') is not None and
            int(date_dict.get('month')) or 1,
            date_dict.get('day') is not None and
            int(date_dict.get('day')) or 1)

        date_breadcrumbs = [year_crumb(path_date)]
        if date_dict['month']:
            date_breadcrumbs.append(month_crumb(path_date))
        if date_dict['day']:
            date_breadcrumbs.append(day_crumb(path_date))
        breadcrumbs.extend(date_breadcrumbs)
        breadcrumbs[-1].url = None
        return breadcrumbs

    url_components = [comp for comp in
                      path.replace(zinnia_root_path, '', 1).split('/')
                      if comp]
    if len(url_components):
        breadcrumbs.append(Crumb(_(url_components[-1].capitalize())))

    return breadcrumbs
