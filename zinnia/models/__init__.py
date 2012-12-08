"""Models for Zinnia"""
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category

from zinnia.signals import connect_entry_signals
from zinnia.signals import connect_discussion_signals
from zinnia.moderator import EntryCommentModerator
from django.contrib.comments.moderation import moderator

# Here we import the Zinnia's Model classes
# to register the Models at the loading, not
# when the Zinnia's URLs are parsed. Issue #161.
__all__ = [Entry.__name__,
           Author.__name__,
           Category.__name__]

# Register the comment moderator on Entry
moderator.register(Entry, EntryCommentModerator)

# Connect the signals
connect_entry_signals()
connect_discussion_signals()
