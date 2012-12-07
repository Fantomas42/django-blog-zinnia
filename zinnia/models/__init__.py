"""Models for Zinnia"""
from django.db.models.signals import post_save
from django.contrib.comments.moderation import moderator
# Here we import the Zinnia's Model classes
# to register the Models at the loading, not
# when the Zinnia's urls are parsed. Issue #161.
from zinnia.models.entry import Entry
from zinnia.models.author import Author
from zinnia.models.category import Category

from zinnia.moderator import EntryCommentModerator
from zinnia.signals import ping_directories_handler
from zinnia.signals import ping_external_urls_handler

__all__ = [Entry.__name__,
           Author.__name__,
           Category.__name__]

moderator.register(Entry, EntryCommentModerator)
post_save.connect(ping_directories_handler, sender=Entry,
                  dispatch_uid='zinnia.entry.post_save.ping_directories')
post_save.connect(ping_external_urls_handler, sender=Entry,
                  dispatch_uid='zinnia.entry.post_save.ping_external_urls')
