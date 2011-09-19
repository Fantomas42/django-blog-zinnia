Extending Entry model
=====================

The Entry model bundled in Zinnia can now be extended and customized.

This feature is useful for who wants to add some fields in the model,
or change its behavior. It allows Zinnia to be a really generic
and reusable application.

Imagine that I find Zinnia really great, but that is misses some fields
or features to be the blog app that I need for my django project.
For example I need to add a custom field linking to an image gallery,
2 solutions :

* I search for another django blogging app fitting my needs.
* I make a monkey patch, but I won't be able to upgrade to future releases.

These 2 solutions are really bad, that's why Zinnia provides
a third solution.

* Customizing the model noninvasively with the power of inheritance.

How do we do that ?

In fact, simply by creating an abstract model inherited from
EntryBaseModel, adding fields or/and overriding his methods, and
registering it with the ZINNIA_ENTRY_BASE_MODEL setting in your project.

Example for adding a gallery field. ::

  from django.db import models
  from mygalleryapp.models import Gallery
  from zinnia.models import EntryAbstractClass

  class EntryGallery(EntryAbstractClass):
    gallery = models.ForeignKey(Gallery)

    class Meta:
      abstract = True


Now you register the EntryGallery model like this in your project's
settings. ::

  ZINNIA_ENTRY_BASE_MODEL = 'appname.custom_entry.EntryGallery'


Finally extend the entry admin class to show your custom field. ::

  from django.contrib import admin
  from zinnia.admin.entry import EntryAdmin
  from zinnia.models import Entry
  from django.utils.translation import ugettext_lazy as _
  
  class EntryGalleryAdmin(EntryAdmin):
    
    # in our case put the gallery field into the 'Content' fieldset
    fieldsets = ((_('Content'), {'fields': ('title', 'content', 'image', 'status', 'gallery')}),) + EntryAdmin.fieldsets[1:]

  admin.site.unregister(Entry)
  admin.site.register(Entry, EntryGalleryAdmin)


You can see another example in the files *zinnia/plugins/placeholder.py* and *zinnia/plugins/admin.py*.

.. note:: You have to respect **4 important rules** :

          #. Do not import the Entry model in your file defining the
             extended model because it will cause a circular importation.

          #. Do not put your abstract model in a file named models.py,
             it will not work for a non obvious reason.

          #. Don't forget to tell that your model is abstract. Otherwise a
             table will be created and the extending process will not work
             as expected.

          #. If you extend the Entry model after the syncdb command, you
             will have to reset the Zinnia application to reflect your
             changes.
