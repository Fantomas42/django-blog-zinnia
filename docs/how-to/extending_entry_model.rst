=====================
Extending Entry model
=====================

.. module:: zinnia.models

.. versionadded:: 0.8

The :class:`Entry` model bundled in Zinnia can now be extended and customized.

This feature is useful for who wants to add some fields in the model,
or change its behavior. It also allows Zinnia to be a really generic
and reusable application.

.. _why-extending:

Why extending ?
===============

Imagine that I find Zinnia really great for my project but some fields
or features are missing to be the Weblog app that suits to my project.
For example I need to add a custom field linking to an image gallery,
two solutions:

* I search for another Django blogging app fitting my needs.
* I do a monkey patch, into the Zinnia code base.

These two solutions are really bad.

For the first solution maybe you will not find the desired application and
also mean that Zinnia is not a reusable application following the Django's
convention. For the second solution, I don't think that I need to provide
more explanations about the evil side of monkey patching (evolution,
reproduction...). That's why Zinnia provides a third generic solution.

* Customizing the :class:`Entry` model noninvasively with the power of
  class inheritance !

The extension process is done in three main steps:

#. Write a class containing your customizations.
#. Register your class into Zinnia to be used.
#. Update the :class:`~zinnia.admin.entry.EntryAdmin` class accordingly.

In the suite of this document we will show how to add an image gallery into
the :class:`Entry` model to illustrate the concepts involved. We assume that
the pieces of codes written for this document belong in the
:mod:`zinnia_gallery` package/application.

.. _writing-model-extension:

Writing model extension
=======================

The first step to extend the :class:`Entry` model is to define a new class
inherited from the :class:`EntryAbstractClass` and add your fields or/and
override the inherited methods if needed. So in :mod:`zinnia_gallery` let's
write our new class in a file named :file:`entry_gallery.py`. ::

  from django.db import models
  from zinnia_gallery.models import Gallery
  from zinnia.models import EntryAbstractClass

  class EntryGallery(EntryAbstractClass):
      gallery = models.ForeignKey(Gallery)

      def __unicode__(self):
          return 'EntryGallery %s' % self.title

      class Meta(EntryAbstractClass.Meta):
          abstract = True

In this code sample, we add a new :class:`~django.db.models.ForeignKey`
field named ``gallery`` pointing to a :class:`Gallery` model defined in
:mod:`zinnia_gallery.models` and we override the
:meth:`EntryAbstractClass.__unicode__` method.

.. note:: You have to respect **3 important rules** to make extending working :

          #. Do not import the :class:`Entry` model in your file defining
             the extended model because it will cause a circular
             importation.

          #. Do not put your abstract model in a file named :file:`models.py`,
             it will not work for a non obvious reason.

          #. Don't forget to tell that your model is ``abstract``. Otherwise a
             table will be created and the extending process will not work
             as expected.

.. note:: Considerations about the database :

          * If you extend the :class:`Entry` model after the ``syncdb``
            command, you have to reset the Zinnia application to reflect
            your changes.

          * South cannot be used to write migrations to your new model.

.. seealso::
   :ref:`model-inheritance` for more information about the concepts
   behind the model inheritence in Django and the limitations.

.. _registering-the-extension:

Registering the extension
=========================

Once your extension class is defined you simply have to register it,
with the :setting:`ZINNIA_ENTRY_BASE_MODEL` setting in your Django
settings. The expected value is a string representing the full Python path
to the extented model's class name. This is the easiest part of the
process.

Following our example we must add this line in the project's settings. ::

  ZINNIA_ENTRY_BASE_MODEL = 'zinnia_gallery.entry_gallery.EntryGallery'

If an error occurs when your new class is imported a warning will be raised
and the :class:`EntryAbstractClass` will be used.

.. _updating-admin-interface:

Updating the admin interface
============================

Now we should update the :class:`Entry`'s admin class to reflect our
changes and use the new fields.

To do that we will write a new admin class inherited from
:class:`~zinnia.admin.entry.EntryAdmin` and use the admin site
register/unregister mechanism for using our new class.

In the file :file:`zinnia_gallery/admin.py` we can write these code lines
for adding the gallery field: ::

  from django.contrib import admin
  from django.utils.translation import ugettext_lazy as _

  from zinnia.models import Entry
  from zinnia.admin.entry import EntryAdmin

  class EntryGalleryAdmin(EntryAdmin):
    # In our case we put the gallery field
    # into the 'Content' fieldset
    fieldsets = ((_('Content'), {'fields': (
      'title', 'content', 'image', 'status', 'gallery')}),) + \
      EntryAdmin.fieldsets[1:]

  # Unregister the default EntryAdmin
  # then register the EntryGalleryAdmin class
  admin.site.unregister(Entry)
  admin.site.register(Entry, EntryGalleryAdmin)


Note that the :mod:`zinnia_gallery` application must be registered in the
:setting:`INSTALLED_APPS` setting after the :mod:`zinnia` application for
applying the register/unregister mechanism in the admin site.

Now we can easily
:doc:`customize the templates</how-to/customize_look_and_feel>`
provided by Zinnia to display the gallery field into the Weblog's pages.

For information you can see another implementation example in the
`cmsplugin-zinnia`_ package.

.. _`cmsplugin-zinnia`: https://github.com/Fantomas42/cmsplugin-zinnia
