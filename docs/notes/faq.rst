==========================
Frequently Asked Questions
==========================

.. contents::

.. _faq-templates:

Templates
=========

.. _customizing-templates:

The templates does not fit to my wishes. What can I do ?
--------------------------------------------------------

You should take a look on :doc:`/how-to/customize_look_and_feel`.

.. _faq-comments:

Comments
========

.. _customizing-comments:

Is it possible have a different comment system, with reply feature for example ?
--------------------------------------------------------------------------------

Yes the comment system integrated in Zinnia is based on
:mod:`django.contrib.comments` and can be extended or replaced if doesn't
quite fit your needs. You should take a look on the
`customizing the comments framework`_ documentation for more information.

.. warning::

   The custom comment Model must be inherited from
   :class:`~django.contrib.comments.models.Comment` and implement the
   :class:`~django.contrib.comments.managers.CommentManager` to properly
   work with Zinnia.


If you want the ability to reply on comments, you can take a look at
`django-threadcomments`_ for example.

.. _faq-edition:

Edition
=======

.. _custom-markups:

I want to write my entries in `MarkDown`_, `RestructuredText`_ or any lightweight markup language, is it possible ?
-------------------------------------------------------------------------------------------------------------------

Yes of course, Zinnia currently support `MarkDown`_, `Textile`_ and
`reStructuredText`_ as markup languages, but if you want to write your
entries in a custom markup language a solution is to disable the WYSIWYG
editor in the admin site with the :setting:`ZINNIA_WYSIWYG` setting, and
use the appropriate template filter in your templates.

.. _faq-authors:

Authors
=======

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

You can do something like this in your templates :

.. code-block:: html+django

  <img src="{% thumbnail object.image 250x250 %}" />

.. _image-gallery:

I want an image gallery in my posts, what can I do ?
----------------------------------------------------

Simply create a new application with a model named :class:`EntryImage` with a
:class:`~django.db.models.ForeignKey` to the :class:`~zinnia.models.Entry`
model.

Then in the admin module of your app, unregister the
:class:`~zinnia.admin.entry.EntryAdmin` class, and use
:class:`~django.contrib.admin.InlineModelAdmin` in your new admin class.

Here an simple example : ::

  # The model
  from django.db import models
  from django.utils.translation import ugettext_lazy as _

  from zinnia.models import Entry

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

  from zinnia.models import Entry
  from zinnia.admin import EntryAdmin
  from gallery.models import EntryImage

  class EntryImageInline(admin.TabularInline):
      model = EntryImage

  class EntryAdminImage(EntryAdmin):
      inlines = (EntryImageInline,)

  admin.site.unregister(Entry)
  admin.site.register(Entry, EntryAdminImage)

Another and better solution is to extend the :class:`~zinnia.models.Entry`
model like described in :doc:`/how-to/extending_entry_model`.


.. _`customizing the look and feel`: https://docs.djangoproject.com/en/dev/intro/tutorial02/#customize-the-admin-look-and-feel
.. _`customizing the comments framework`: https://docs.djangoproject.com/en/dev/ref/contrib/comments/custom/
.. _`django-threadcomments`: https://github.com/HonzaKral/django-threadedcomments
.. _`MarkDown`: http://daringfireball.net/projects/markdown/
.. _`Textile`: http://redcloth.org/hobix.com/textile/
.. _`reStructuredText`: http://docutils.sourceforge.net/rst.html
.. _`sorl.thumbnail`: http://thumbnail.sorl.net/
