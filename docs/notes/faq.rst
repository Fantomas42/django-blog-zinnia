==========================
Frequently Asked Questions
==========================

.. contents::

.. _faq-entries:

Entries
=======

.. _custom-markups:

I want to write my entries in `MarkDown`_, `RestructuredText`_ or any lightweight markup language, is it possible ?
-------------------------------------------------------------------------------------------------------------------

Yes of course, Zinnia currently support `MarkDown`_, `Textile`_ and
`reStructuredText`_ as markup languages, but if you want to write your
entries in a custom markup language a solution is to disable the WYSIWYG
editor in the admin site with the :setting:`ZINNIA_WYSIWYG` setting, and
use the appropriate template filter in your templates.

I want to have multilingual support on the entries, is it possible ?
--------------------------------------------------------------------

Due to the extending capabilities of Zinnia, many solutions on this
problematic are possible, but you must keep in mind that multiplingual
entries is just a concept, the needs and the implementations can differ
from a project to another. But you should take a look on this excellent
tutorial to `convert Zinnia into a multilingual Weblog`_ with
`django-modeltranslation`_, which can be a good starting point for your
needs.

.. _multiple-authors:

Is Zinnia able to allow multiple users to edit it's own blog ?
--------------------------------------------------------------

Zinnia is designed to be multi-site. That's mean you can publish entries on
several sites or share an admin interface for all the sites handled.

Zinnia also provides a new permission that's allow or not the user to
change the authors. Useful for collaborative works.

But if you want to restrict the edition of the entries by site, authors or
whatever you want, it's your job to implement this functionality in your
project.

The simple way to do that, respecting the Django rules, is to override the
admin classes provided by Zinnia, and register those classes in another
admin site.

.. _faq-images:

Images
======

.. _image-thumbnails:

How can I use the image field for fitting to my skin ?
------------------------------------------------------

Take a looks at `sorl.thumbnail`_ and use his templatetags.

You can do something like this in your templates:

.. code-block:: html+django

  <img src="{% thumbnail object.image 250x250 %}" />

.. _image-gallery:

I want an image gallery in my posts, what can I do ?
----------------------------------------------------

Simply create a new application with a model named :class:`EntryImage` with a
:class:`~django.db.models.ForeignKey` to the
:class:`~zinnia.models.entry.Entry` model.

Then in the admin module of your app, unregister the
:class:`~zinnia.admin.entry.EntryAdmin` class, and use
:class:`~django.contrib.admin.InlineModelAdmin` in your new admin class.

Here an simple example : ::

  # The model
  from django.db import models
  from django.utils.translation import ugettext_lazy as _

  from zinnia.models.entry import Entry

  class EntryImage(models.Model):
      """Image Model"""
      entry = models.ForeignKey(Entry, verbose_name=_('entry'))

      image = models.ImageField(_('image'), upload_to='uploads/gallery')
      title = models.CharField(_('title'), max_length=250)
      description = models.TextField(_('description'), blank=True)

      def __unicode__(self):
          return self.title

  # The admin

  from django.contrib import admin

  from zinnia.admin import EntryAdmin
  from zinnia.models.entry import Entry
  from gallery.models import EntryImage

  class EntryImageInline(admin.TabularInline):
      model = EntryImage

  class EntryAdminImage(EntryAdmin):
      inlines = (EntryImageInline,)

  admin.site.unregister(Entry)
  admin.site.register(Entry, EntryAdminImage)

Another and better solution is to extend the :class:`~zinnia.models.entry.Entry`
model like described in :doc:`/how-to/extending_entry_model`.

.. _faq-comments:

Comments
========

.. _customizing-comments:

Is it possible have a different comment system, with reply feature for example ?
--------------------------------------------------------------------------------

Yes the comment system integrated in Zinnia is based on
:mod:`django_comments` and can be extended or replaced if doesn't
quite fit your needs. You should take a look on the
`customizing the comments framework`_ documentation for more information.

.. warning::

   The custom comment Model must be inherited from
   :class:`~django_comments.models.Comment` and implement the
   :class:`~django_comments.managers.CommentManager` to properly
   work with Zinnia.


If you want the ability to reply on comments, you can take a look at
`zinnia-threaded-comments`_ or at `django-threadcomments`_.


.. _`MarkDown`: http://daringfireball.net/projects/markdown/
.. _`Textile`: http://redcloth.org/hobix.com/textile/
.. _`reStructuredText`: http://docutils.sourceforge.net/rst.html
.. _`convert Zinnia into a multilingual Weblog`: http://www.codeispoetry.me/django-blog-zinnia-multilanguage-support-with-django-modeltranslation/
.. _`django-modeltranslation`: https://github.com/deschler/django-modeltranslation
.. _`sorl.thumbnail`: https://github.com/mariocesar/sorl-thumbnail
.. _`customizing the comments framework`: http://django-contrib-comments.readthedocs.org/en/latest/custom.html
.. _`zinnia-threaded-comments`: https://github.com/django-blog-zinnia/zinnia-threaded-comments
.. _`django-threadcomments`: https://github.com/HonzaKral/django-threadedcomments
