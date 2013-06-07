"""Preview for Zinnia"""
from django.utils.text import Truncator
from django.utils.encoding import python_2_unicode_compatible

from bs4 import BeautifulSoup

from zinnia.settings import PREVIEW_SPLITTERS
from zinnia.settings import PREVIEW_MAX_WORDS
from zinnia.settings import PREVIEW_MORE_STRING


@python_2_unicode_compatible
class HTMLPreview(object):
    """
    Build an HTML preview of an HTML content.
    """

    def __init__(self, content,
                 splitters=PREVIEW_SPLITTERS,
                 max_words=PREVIEW_MAX_WORDS,
                 more_string=PREVIEW_MORE_STRING):
        self._preview = None

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
        return self.preview != self.content

    def __str__(self):
        """
        Method used to render the preview in templates.
        """
        return self.preview

    def build_preview(self):
        """
        Build the preview by:
        - Checking if a split marker is present in the content
          Then split the content with the marker to build the preview.
        - Splitting the content to a fixed number of words.
        """
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
