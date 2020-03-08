"""Preview for Zinnia"""
from __future__ import division

from bs4 import BeautifulSoup

from django.utils.functional import cached_property
from django.utils.html import strip_tags
from django.utils.text import Truncator

from zinnia.settings import PREVIEW_MAX_WORDS
from zinnia.settings import PREVIEW_MORE_STRING
from zinnia.settings import PREVIEW_SPLITTERS


class HTMLPreview(object):
    """
    Build an HTML preview of an HTML content.
    """

    def __init__(self, content, lead='',
                 splitters=PREVIEW_SPLITTERS,
                 max_words=PREVIEW_MAX_WORDS,
                 more_string=PREVIEW_MORE_STRING):
        self._preview = None

        self.lead = lead
        self.content = content
        self.splitters = splitters
        self.max_words = max_words
        self.more_string = more_string

    @property
    def preview(self):
        """
        The preview is a cached property.
        """
        if self._preview is None:
            self._preview = self.build_preview()
        return self._preview

    @property
    def has_more(self):
        """
        Boolean telling if the preview has hidden content.
        """
        return bool(self.content and self.preview != self.content)

    def __str__(self):
        """
        Method used to render the preview in templates.
        """
        return str(self.preview)

    def build_preview(self):
        """
        Build the preview by:

        - Returning the lead attribut if not empty.
        - Checking if a split marker is present in the content
          Then split the content with the marker to build the preview.
        - Splitting the content to a fixed number of words.
        """
        if self.lead:
            return self.lead
        for splitter in self.splitters:
            if splitter in self.content:
                return self.split(splitter)
        return self.truncate()

    def truncate(self):
        """
        Truncate the content with the Truncator object.
        """
        return Truncator(self.content).words(
            self.max_words, self.more_string, html=True)

    def split(self, splitter):
        """
        Split the HTML content with a marker
        without breaking closing markups.
        """
        soup = BeautifulSoup(self.content.split(splitter)[0],
                             'html.parser')
        last_string = soup.find_all(text=True)[-1]
        last_string.replace_with(last_string.string + self.more_string)
        return soup

    @cached_property
    def total_words(self):
        """
        Return the total of words contained
        in the content and in the lead.
        """
        return len(strip_tags('%s %s' % (self.lead, self.content)).split())

    @cached_property
    def displayed_words(self):
        """
        Return the number of words displayed in the preview.
        """
        return (len(strip_tags(self.preview).split()) -
                (len(self.more_string.split()) * int(not bool(self.lead))))

    @cached_property
    def remaining_words(self):
        """
        Return the number of words remaining after the preview.
        """
        return self.total_words - self.displayed_words

    @cached_property
    def displayed_percent(self):
        """
        Return the percentage of the content displayed in the preview.
        """
        return (self.displayed_words / self.total_words) * 100

    @cached_property
    def remaining_percent(self):
        """
        Return the percentage of the content remaining after the preview.
        """
        return (self.remaining_words / self.total_words) * 100
