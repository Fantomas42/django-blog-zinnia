Channels
========

Views by author, categories, tags is not enough :).

The idea is to create specific pages based on a query search.

Imagine that we want to customize the homepage of the weblog, because we
write on a variety of subjects and we don't want to bore visitors who aren't
interested in some really specific entries.

Another usage of the channels is for SEO, for aggregating entries
under a well-formatted url.

For doing that Zinnia provides a view called
*zinnia.views.channels.entry_channel*.

If we take our first example, we will do like that for customizing
the weblog homepage in our project's urls.py. ::

  url(r'^weblog/$', 'zinnia.views.channels.entry_channel',
      {'query': 'category:python OR category:django'}),
  url(r'^weblog/', include('zinnia.urls')),

The first url will handle the homepage of the blog instead of the default
url provided by Zinnia.

As we can see, the only required argument for this view is *query*. This
parameter represents a query search string. This string will be interpreted
by the search engine activated in Zinnia and return a list of entries.

So our homepage will only display entries filled under the categories
'Python' and 'Django'.

The others parameters handled by the channel view are the same that
the generic `object_list
<http://docs.djangoproject.com/en/dev/ref/generic-views/#django-views-generic-list-detail-object-list>`_
view bundled in Django can handle.

