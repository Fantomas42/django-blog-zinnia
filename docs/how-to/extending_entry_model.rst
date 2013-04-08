=====================
Extending Entry model
=====================

.. module:: zinnia.models.entry

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

.. _writing-model-extension:

Writing model extension
=======================

In the suite of this document we will show how to add an image gallery into
the :class:`Entry` model to illustrate the concepts involved when
extending. We assume that the pieces of codes written for this document
belong in the :mod:`zinnia_gallery` module/application.

.. versionchanged:: 0.13

The :class:`zinnia.models.entry.EntryAbstractClass` has been moved and
renamed to :class:`zinnia.models_bases.entry.AbstractEntry`.

The first step to extend the :class:`Entry` model is to define a new class
inherited from the :class:`~zinnia.models_bases.entry.AbstractEntry` and
add your fields or/and override the inherited methods if needed. So in
:mod:`zinnia_gallery` let's write our gallery models and the extension in
the :class:`Entry` model in :file:`models.py`. ::

  from django.db import models
  from zinnia.models_bases.entry import AbstractEntry

  class Picture(models.Model):
      title = models.CharField(max_length=50)
      image = models.ImageField(upload_to='gallery')

  class Gallery(models.Model):
      title = models.CharField(max_length=50)
      pictures = models.ManyToManyField(Picture)

  class EntryGallery(AbstractEntry):
      gallery = models.ForeignKey(Gallery)

      def __unicode__(self):
          return u'EntryGallery %s' % self.title

      class Meta(AbstractEntry.Meta):
          abstract = True

In this code sample, we simply add in our :class:`Entry` model a new
:class:`~django.db.models.ForeignKey` field named ``gallery`` pointing to a
:class:`Gallery` model and we override the :meth:`Entry.__unicode__` method.

.. note:: You have to respect **2 important rules** to make extending working :

          #. Do not import the :class:`Entry` model in your file defining
             the extended model because it will cause a circular
             importation.

          #. Don't forget to tell that your model is ``abstract``. Otherwise a
             table will be created and the extending process will not work
             as expected.

.. seealso::
   :ref:`model-inheritance` for more information about the concepts
   behind the model inheritence in Django and the limitations.

.. _writing-model-customisation:

Writing model customisation
===========================

Adding fields is pretty easy, but now that the :class:`Entry` model has
been extended, we want to change the :attr:`image` field wich is an
:class:`~django.db.models.ImageField` by default to use our new
:class:`Picture` instead.

To customise this field, the same process as extending apply, but we can
take advantage of all the abstracts classes provided to build the
:class:`~zinnia.models_bases.entry.AbstractEntry` to rebuild our own custom
:class:`Entry` model like this: ::

  from django.db import models
  from zinnia.models_bases import entry

  class Picture(models.Model):
      title = models.CharField(max_length=50)
      image = models.ImageField(upload_to='gallery')

  class Gallery(models.Model):
      title = models.CharField(max_length=50)
      pictures = models.ManyToManyField(Picture)

  class EntryGallery(
            entry.CoreEntry,
            entry.ContentEntry,
            entry.DiscussionsEntry,
            entry.RelatedEntry,
            entry.ExcerptEntry,
            entry.FeaturedEntry,
            entry.AuthorsEntry,
            entry.CategoriesEntry,
            entry.TagsEntry,
            entry.LoginRequiredEntry,
            entry.PasswordRequiredEntry,
            entry.ContentTemplateEntry,
            entry.DetailTemplateEntry):

      image = models.ForeignKey(Picture)
      gallery = models.ForeignKey(Gallery)

      def __unicode__(self):
          return u'EntryGallery %s' % self.title

      class Meta(entry.CoreEntry.Meta):
          abstract = True

Now we have an :class:`Entry` model extended with a gallery of pictures and
customised with a :class:`Picture` model relation as the :attr:`image`
field.

Note that the same process apply if you want to delete some built-in fields.

.. _database-considerations:

Considerations about the database
=================================

If you do the extension of the :class:`Entry` model after the ``syncdb``
command, you have to manually alter the Zinnia's tables for reflecting your
changes made on the model class. In the case where your database is empty,
you can simply execute the ``reset`` command on the Zinnia application for
destroying the old database schema and installing the new one.

Now if you are using `South`_ and try to write a new migration for
reflecting your changes, the migration script will be written in the
:mod:`zinnia.migrations` module, which is not recommended because the
result is not replicable for multiple installations and breaks the
migration system with future releases of Zinnia.

Fortunatly `South`_ provides an elegant solution with the
`SOUTH_MIGRATION_MODULES`_ setting. Once this setting done for the
``'zinnia'`` key, because you are now out the Zinnia's default migrations
flow, you have to delete the ghost migrations for Zinnia. At this step you
can now start to write new migrations.

It's recommended that the new initial migration represents the default
:class:`Entry` schema provided by Zinnia, because after that, you just have
to write a new migration for reflecting your changes, and you can alter
your database schema with the ``migrate`` command.

.. _registering-the-extension:

Registering the extension
=========================

Once your extension class is defined you simply have to register it,
with the :setting:`ZINNIA_ENTRY_BASE_MODEL` setting in your Django
settings. The expected value is a string representing the full Python path
to the extented model's class name. This is the easiest part of the
process.

Following our example we must add this line in the project's settings. ::

  ZINNIA_ENTRY_BASE_MODEL = 'zinnia_gallery.models.EntryGallery'

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

  from zinnia.models.entry import Entry
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

For more information you can see another implementation example in the
`cmsplugin-zinnia`_ package.

.. _`South`: http://south.aeracode.org/
.. _`SOUTH_MIGRATION_MODULES`: http://south.readthedocs.org/en/latest/settings.html#south-migration-modules
.. _`cmsplugin-zinnia`: https://github.com/Fantomas42/cmsplugin-zinnia
