=====================
Rewriting Entry's URL
=====================

.. module:: zinnia.models.entry

By default the :class:`Entry` model implements a default
:meth:`~Entry.get_absolute_url` method to retrieve the canonical URL for an
instance into the Weblog.

.. seealso::
   :meth:`~django.db.models.Model.get_absolute_url` for more information about
   the usage of this method if your are not familiar with this concept.

The result of this method is a string composed of the entry's
``creation date`` and the ``slug``. For example this URL:
``/blog/2011/07/17/how-to-change-url/`` refers to an entry created on the
17th July 2011 under the slug ``how-to-change-url``.

This URL pattern is common for most of the Weblog engines and have these
following advantages.

* SEO Friendly.
* Human readable.
* You can remove parts of the URL and find archives.
* The slug is unique with the creation date, so you can reuse it.

But if you want to change it into a different form, you have to know that
it's possible, but not easy.

You have to note that the changes required on the Zinnia's code base to
simplify this customization step in a generic way, are evil, dirty and
unsecured. You will see throughout this document why this customization is
not directly implemented, why it cannot be handled genericaly and which are
the pitfalls to avoid.

.. warning::
   Before further reading, you have to note that the methods explained
   below are reserved for confirmed Django developers, knowing what they
   are doing. No warranties and no support will be provided for the
   problems encountered if you customize this part of Zinnia.

.. _choosing-your-new-url-pattern:

Choosing your new URL pattern
=============================

We can imagine many different forms of new URL for your entries:

* ``/blog/<id>/``
* ``/blog/<slug>/``
* ``/blog/<year>/<slug>/``
* ``/blog/<creation-date>-<slug>/``
* ``/blog/<slug>/<tag-1>/<tag-n>/``
* ``/blog/<category-1>/<category-n>/<slug>/``

As you can see we can imagine a lot of new patterns to handle the canonical
URL of an entry. But you must keep in mind that you must have a unique URL
per entry.

Like we said above, the slug is unique with the creation date, so only
using the entry' slug to retrieve the matching :class:`Entry` instance
is not safe, because the view will fail if you have 2 entries with the
same slug.

If you want to decorate the entry's slug with the categories' slugs of the
entry, or with some additionnal datas (like in the latest examples), make
sure that you can write an efficient regular expression for capturing text
in the URL. The complexity of the URL's regexp will depend on the pattern
choosen for the new URL.

For the rest of this document we will show how to change the entry's URL
with the ``/blog/<id>/`` pattern. This is just to illustrate the facts
presented in this document, because this pattern is already handled by the
default :doc:`/topics/url_shortener` backend, but have the advantage to be
perfect for this tutorial.

We assume that the code involved in this document belong in the
:mod:`zinnia_customized` package/application. This package will contain all
the pieces of code to customize the default behaviour of Zinnia.

.. _the-entry-get-absolute-url-method:

The :meth:`Entry.get_absolute_url` method
=========================================

Accordingly to your new URL pattern you have to override the
:meth:`Entry.get_absolute_url` method to pass the desired parameters to
build the canonical URL of an entry.

To do this override, simply use the method explained in the
:doc:`/how-to/extending_entry_model` document to create a new class based on
:class:`~zinnia.models_bases.entry.AbstractEntry` with the new
``get_absolute_url`` method. ::

  class EntryWithNewUrl(AbstractEntry):
      """Entry with '/blog/<id>/' URL"""

      @models.permalink
      def get_absolute_url(self):
          return ('zinnia_entry_detail', (),
                  {'pk': self.id})

      class Meta(AbstractEntry.Meta):
          abstract = True

Due to the intensive use of this method into the templates, make sure that
your re-implemention is not too slow. For example hitting the database to
recontruct this URL is not a really good idea. That's why an URL pattern
based on the categories like ``/blog/<category-1>/<category-n>/<slug>/`` is
really bad.

.. _adding-your-entry-detail-view:

Adding your view
================

Now we must write a custom view to handle the detailed view of an
:class:`Entry` instance from the text parameters passed in the URL.
So in a module called :mod:`zinnia_customized.views` we can write this view
for handling our new URL. ::

  from django.views.generic.detail import DetailView

  from zinnia.models.entry import Entry
  from zinnia.views.mixins.entry_protection import EntryProtectionMixin

  class EntryDetail(EntryProtectionMixin, DetailView):
      queryset = Entry.published.on_site()
      template_name_field = 'template'


Pretty easy isn't it ? For more information, check the documentation about
the :class:`~django.views.generic.detail.DetailView` view. Note that the
:class:`~zinnia.views.mixins.EntryProtectionMixin` is used for enabling
password and login protections if needed on the entry.

.. _reconfigure-urls:

Configuring URLs
================

The final step to rewrite the entry's URL, is to change the URLconf for
the Weblog application. Instead of using the default implementation
provided by :mod:`zinnia.urls` in your project's URLconf, you have to
re-implement all the URLsets provided by Zinnia as described in the
:ref:`urls` section of the installation process.

But instead of including :mod:`zinnia.urls.entries` you will include your own
URLconf containing the new URL code for the canonical URL of your
entries. Doing a copy of the original module in your own project can save
you a lot time. ::

  ...
  url(r'^weblog/', include('zinnia_customized.urls')),
  ...

Now in :mod:`zinnia_customized.urls` rewrite the :func:`~django.conf.urls.url`
named ``'zinnia_entry_detail'`` with your new regular expression handling the
canonical URL of your entries and the text parameters. Don't forget to also
change the path to your view retrieving the :class:`Entry` instance from
the text parameters. ::

  from zinnia_customized.views import EntryDetail

  url(r'^(?P<pk>\d+)/$',
      EntryDetail.as_view(),
      name='zinnia_entry_detail')

.. warning::
   If you use the pingback XML-RPC service, you will also need change
   to :func:`~zinnia.xmlrpc.pingback.pingback_ping` function for retrieving
   the :class:`Entry` instance, accordingly to the new text parameters
   captured in the URL.


Actually you should consider Zinnia like a ready to use Weblog application
and also like a framework to make customized Weblog engines.
