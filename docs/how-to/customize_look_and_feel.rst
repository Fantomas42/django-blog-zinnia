================================
Customize Zinnia's look and feel
================================

The templates provided for Zinnia are simple but complete and as generic as
possible. You can easily change them by
`specifying a template directory`_. If you are not familiar with Django,
part two of the excellent Django tutorial explains in details how to
`customize the look and feel`_ of the :mod:`~django.contrib.admin` app:
it's actually the same thing in Zinnia.

A good starting point is to copy-paste the :file:`zinnia/base.html`
template, and edit the :ttag:`extends` instruction in order to fit into
your skin.

.. note::
	* The main content is displayed in a block named ``content``.
	* Additional data is displayed in a block named ``sidebar``.

You can also create your own app containing some Zinnia’s templates based
on inheritance. For example you can find these applications which can be a
good starting point to make your own at:

* `Zinnia-theme-bootstrap`_.
* `Zinnia-theme-foundation`_.
* `Zinnia-theme-html5`_.
* `Django Blog Quintet`_.

.. warning::
   .. versionchanged:: 0.9

   `Django Blog Quintet`_ is no longer compatible with Zinnia, but is still
   a good example.

Now that we have seen the basic mechanisms to add and customize Zinnia's
templates we will see in details the different possibilities in the
customization process.

.. _css-customization:

CSS customizations
------------------

Most of the time the customization process of Zinnia is about editing the
cascading style sheet of the differents pages delivered by the Weblog.

First of all you have to note that each page of the Weblog has several
classes applied on the ``<body>`` markup. For examples if the document has
paginated entries, the ``paginated`` and ``page-{id}`` classes will be
added. Many classes are used within the default templates so should take a
look on it, maybe it will be useful for you.

Secondly all the documents served by Zinnia have the ``zinnia`` class name
on the ``<body>``. If you remove this class, all the default CSS provided
by Zinnia will not be applied. And if you add it on templates provided by
third-party applications, the Zinnia's style will be applied. Pretty
useful, for enabling or disabling Zinnia's default style.

Of course adding or removing classes can easily be done in your own
templates by overriding the block named ``body-class``.

You also have to note that a real effort has be done for providing clean
and valid HTML documents, without redundant and useless classes or IDs
overweighting the document respecting the **presentation-free markup**
rule.

Now that you have all of these information in mind, you can add new
cascading style sheets into your templates, containing your customization
rules and of course remove the default CSS files provided by Zinnia if
needed.

.. _default-theme-variations:

Variations on the default theme
-------------------------------

.. versionadded:: 0.12

Beside the ``zinnia`` class name in the ``<body>`` tag of the
``zinnia/skeleton.html`` template, three other class names are available:

.. code-block:: html+django

  <body class="zinnia default blue right-sidebar {% block body-class %}{% endblock %}">

The ``default`` class name represents the original default theme of
Zinnia. You can remove this class, or replace with the classes ``light`` or
``dark`` to activate the variations with high readability and contrast,
thanks to the `Solarized`_ project.

The ``blue`` class represents the main color used within the
theme. Available color are: ``yellow``, ``orange``, ``red``, ``magenta``,
``violet``, ``blue``, ``cyan``, ``green``.

The ``right-sidebar`` class sets the sidebar at right and ``left-sidebar``
at left, by default if none of these classes are present, the sidebar is
set at right. You can hide the sidebar by using the ``no-sidebar`` class.

With these 3 sets of classes available in the CSS, you now have 4*9*3=108
variations of the default theme available. Try them and choose your
favorite!

.. _special-templates:

Special templates
-----------------

Since the beginning of Zinnia, the development has been influenced by the
idea of **Power templates for easy rendering**. Customizing all the
templates of the Weblog must be possible, easy and fast. So Zinnia has a
unique feature for returning custom templates depending on the view's
context.

.. _filter-templates:

Templates for filters
=====================

Zinnia as a complete Weblog application provides views for filtering the
last entries by authors, categories and tags. In these views you have the
possibility to use a dedicated template related to the filtering
model. This feature is useful for highlighting a special category or for
providing a template per author.

Each of these views will return a list of templates name to render the page
but only the first template name matching to an existing template will be
used to render.

Examples:

* For the URL ``/blog/categories/events/`` the
  :class:`~zinnia.views.categories.CategoryDetail` view will be called and
  return this list of template names: ::

    ['zinnia/category/event/entry_list.html',
     'zinnia/category/event_entry_list.html',
     'zinnia/category/entry_list.html',
     'zinnia/entry_list.html']

* For the URL ``/blog/tags/featured/`` the
  :class:`~zinnia.views.tags.TagDetail` view will be called and
  return this list of template names: ::

    ['zinnia/tag/featured/entry_list.html',
     'zinnia/tag/featured_entry_list.html',
     'zinnia/tag/entry_list.html',
     'zinnia/entry_list.html']

* For the URL ``/blog/authors/keneda/`` the
  :class:`~zinnia.views.authors.AuthorDetail` view will be called and
  return this list of template names: ::

    ['zinnia/author/keneda/entry_list.html',
     'zinnia/author/keneda_entry_list.html',
     'zinnia/author/entry_list.html',
     'zinnia/entry_list.html']

.. _archives-templates:

Templates for archives
======================

Concerning the archive views the same feature is implemented, a list of
template names will be returned depending of the date and the archive
period. This feature take all his sense if want to use *Halloween* or
*Christmas* templates for your Weblog. With this feature you can also
program and re-use your themes on several periods.

Another side effect is if you write an Entry during the *Halloween*
period with dedicated templates, even after the *Halloween* period the
templates will still be used.

Examples:

* For the URL ``/blog/2012/`` the
  :class:`~zinnia.views.archives.EntryYear` view will be called and
  return this list of template names: ::

    ['zinnia/archives/2012/entry_archive_year.html',
     'zinnia/archives/entry_archive_year.html',
     'zinnia/entry_archive_year.html',
     'entry_archive_year.html']

* For the URL ``/blog/2012/week/16/`` the
  :class:`~zinnia.views.archives.EntryWeek` view will be called and
  return this list of template names: ::

    ['zinnia/archives/2012/week/16/entry_archive_week.html',
     'zinnia/archives/week/16/entry_archive_week.html',
     'zinnia/archives/2012/entry_archive_week.html',
     'zinnia/archives/entry_archive_week.html',
     'zinnia/entry_archive_week.html',
     'entry_archive_week.html']

* For the URL ``/blog/2012/04/21/`` the
  :class:`~zinnia.views.entries.EntryDay` view will be called and
  return this list of template names: ::

    ['zinnia/archives/2012/04/21/entry_archive_day.html',
     'zinnia/archives/month/04/day/21/entry_archive_day.html',
     'zinnia/archives/2012/day/21/entry_archive_day.html',
     'zinnia/archives/day/21/entry_archive_day.html',
     'zinnia/archives/2012/month/04/entry_archive_day.html',
     'zinnia/archives/month/04/entry_archive_day.html',
     'zinnia/archives/2012/entry_archive_day.html',
     'zinnia/archives/entry_archive_day.html',
     'zinnia/entry_archive_day.html',
     'entry_archive_day.html']

.. _detail-templates:

Templates for entry detail
==========================

Each entries of the Weblog has the possibility to have his own template to
be rendered by using the :setting:`ZINNIA_ENTRY_DETAIL_TEMPLATES` settings, so
with this option you can handle multiple presentation for your entries. And
because :class:`~zinnia.views.entries.EntryDetail` is based on an archive
view a custom list of templates is built uppon the publication date.
The entry's slug is also used to build the template list for having
maximal customization capabilities with ease.

For example if I use the ``custom.html`` template to render the entry
located at the URL ``/blog/2012/04/21/my-entry/`` the list of template
names will be: ::

  ['zinnia/archives/2012/04/21/my-entry_custom.html',
   'zinnia/archives/month/04/day/21/my-entry_custom.html',
   'zinnia/archives/2012/day/21/my-entry_custom.html',
   'zinnia/archives/day/21/my-entry_custom.html',
   'zinnia/archives/2012/04/21/my-entry.html',
   'zinnia/archives/month/04/day/21/my-entry.html',
   'zinnia/archives/2012/day/21/my-entry.html',
   'zinnia/archives/day/21/my-entry.html',
   'zinnia/archives/2012/04/21/custom.html',
   'zinnia/archives/month/04/day/21/custom.html',
   'zinnia/archives/2012/day/21/custom.html',
   'zinnia/archives/day/21/custom.html',
   'zinnia/archives/2012/month/04/my-entry_custom.html',
   'zinnia/archives/month/04/my-entry_custom.html',
   'zinnia/archives/2012/month/04/my-entry.html',
   'zinnia/archives/month/04/my-entry.html',
   'zinnia/archives/2012/month/04/custom.html',
   'zinnia/archives/month/04/custom.html',
   'zinnia/archives/2012/my-entry_custom.html',
   'zinnia/archives/2012/my-entry.html',
   'zinnia/archives/2012/custom.html',
   'zinnia/archives/my-entry_custom.html',
   'zinnia/my-entry_custom.html',
   'my-entry_custom.html',
   'zinnia/archives/my-entry.html',
   'zinnia/my-entry.html',
   'my-entry.html',
   'zinnia/archives/custom.html',
   'zinnia/custom.html',
   'custom.html']

Now you have the choice !

.. _content-templates:

Templates for entries' content
==============================

Imagine that you have different kind of entries, some with photos, some
with videos or even with tweets. You might not want to share the same
presentation between these different entries.

An elegent solution to better highlight the content is to use different
templates for each kind of content or presentation you want.

You can easily do this by using the :setting:`ZINNIA_ENTRY_CONTENT_TEMPLATES`.
It allows you to specify a content template for each entries of your blog
using the administration interface.

.. _loop-templates:

Templates within loops
======================

When displaying a list of entries the templates are chosen according to
:setting:`ZINNIA_ENTRY_CONTENT_TEMPLATES`.

But how can we specify a template for a given index position the list ?
For example if we want to highlight the first entry.

Then we simply create a new template suffixed by a dash followed by the
position.

Example: ``zinnia/_entry_detail-1.html``

If we use an underscore instead of a dash the position will reset at every
new page. Replacing the dash by an underscore in the previous example would
highlight the first entry of every page.

You can bypass this behavior altogether and have more control over your
templates by using the :setting:`ZINNIA_ENTRY_LOOP_TEMPLATES` setting.

.. _changing-templates:

Changing templates
------------------

Maybe CSS customizations and adding markup to the templates is not enough
because you need to change a more important part of the templates or you
simply don't want to use it.

Because all the front views bundled in Zinnia are customizable, changing
the template used to render the view is pretty easy and can be a good
solution for you if you are confortable with Django.

Example of changing the default template for the search view by another
view: ::

  from zinnia.views.search import EntrySearch

  class CustomTemplateEntrySearch(EntrySearch):
      template_name = 'custom/template.html'


or directly in the urls: ::

  from django.conf.urls import url
  from django.conf.urls import patterns

  from zinnia.views.search import EntrySearch

  urlpatterns = patterns(
      '',
      url(r'^$', EntrySearch.as_view(
          template_name='custom/template.html'),
          name='entry_search'),
      )

.. _packaging-theme:

Going further
-------------

As you can see that you can customize the look and feel of Zinnia by CSS,
SASS, HTML and Python and even by adding custom views. So why don't you
make a Python package containing a Django application of your complete
theme ? The theme of your weblog will be sharable and easily installable.

Remember to take a look at `Zinnia-theme-bootstrap`_ for having a good
starting point of a packaged theme.


.. _`specifying a template directory`: https://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates
.. _`customize the look and feel`: https://docs.djangoproject.com/en/dev/intro/tutorial07/#customize-the-admin-look-and-feel
.. _`Zinnia-theme-bootstrap`: https://github.com/django-blog-zinnia/zinnia-theme-bootstrap
.. _`Zinnia-theme-foundation`: https://github.com/django-blog-zinnia/zinnia-theme-foundation
.. _`Zinnia-theme-html5`: https://github.com/django-blog-zinnia/zinnia-theme-html5
.. _`Django Blog Quintet`: https://github.com/franckbret/django-blog-quintet
.. _`Solarized`: http://ethanschoonover.com/solarized
