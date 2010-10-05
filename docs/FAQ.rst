Frequently Asked Questions
==========================

* The templates does not fit to my wishes. What can I do ?

    The templates provided for Zinnia are simple but complete and
    as generic as possible. But you can easily change them by
    `specifying a template directory
    <http://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates>`_.


* How can I use the image field for fitting to my skin ?

    Take a looks at `sorl.thumbnail
    <http://code.google.com/p/sorl-thumbnail/>`_ and use his templatetags.

    You can do something like this in your templates : ::

    <img src="{% thumbnail object.image 250x250 %}" />


* Is it possible to have a better comment system, with reply feature
  for example ?

    Yes the comment system integrated in Zinnia is based on
    *django.contrib.comments* and can be extended or replaced.

    If you want the ability to reply on comments, you can take a look
    at `django-threadcomments
    <http://github.com/ericflo/django-threadedcomments>`_ for example.


* I want to write my entries in `MarkDown
  <http://daringfireball.net/projects/markdown/>`_, `RestructuredTest
  <http://docutils.sourceforge.net/rst.html>`_ or any lightweight
  markup language, is it possible ?

    Yes of course, disable de WYSIWYG in the admin site with the
    ZINNIA_WYSIWYG setting, and use the the `markup application
    <http://docs.djangoproject.com/en/dev/ref/contrib/markup/>`_ in
    your templates.


* Is Zinnia able to allow multiple users to edit it's own blog ?

    Zinnia is designed to be multi-site. That's mean you can publish entries
    on several sites or share an admin interface for all the sites handled.

    Zinnia also provides a new permission that's allow or not the user to
    change the authors. Usefull for collaborative works.

    But if you want to restrict the edition of the entries by site,
    authors or whatever you want, it's your job to implement this
    functionality in your project.

    The simple way to do that, respecting the Django rules, is to
    override the admin classes provided by Zinnia, and register
    those classes in another admin site.


* I want an image gallery in my posts, what can I do ?

    Simply create a new application with a model named **EntryImage**
    with a ForeignKey to the Entry model.

    Then in the admin module of your app, unregister the EntryAdmin
    class, and use ModelInline in your new admin class.

    Here an example : ::

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

