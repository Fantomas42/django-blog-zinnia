Template Tags
=============

.. module:: zinnia.templatetags

.. highlightlang:: html+django

Zinnia provides several template tags based on *inclusion_tag* system to
create some **widgets** in your website's templates.

To use any of the following template tags you need to load them first at
the top of your template: ::

  {% load zinnia_tags %}

get_recent_entries
------------------

Display the latest entries.

**Prototype:** ``get_recent_entries(number=5, template="zinnia/tags/recent_entries.html")``

Examples: ::

  {% get_recent_entries %}
  {% get_recent_entries 3 %}
  {% get_recent_entries 3 "custom_template.html" %}

get_featured_entries
--------------------

Display the featured entries.

**Prototype:** ``get_featured_entries(number=5, template="zinnia/tags/featured_entries.html")``

Examples: ::

  {% get_featured_entries %}
  {% get_featured_entries 3 %}
  {% get_featured_entries 3 "custom_template.html" %}

get_random_entries
------------------

Display random entries.

**Prototype:** ``get_random_entries(number=5, template="zinnia/tags/random_entries.html")``

Examples: ::

  {% get_random_entries %}
  {% get_random_entries 3 %}
  {% get_random_entries 3 "custom_template.html" %}

get_popular_entries
-------------------

Display popular entries.

**Prototype:** ``get_popular_entries(number=5, template="zinnia/tags/popular_entries.html")``

Examples: ::

  {% get_popular_entries %}
  {% get_popular_entries 3 %}
  {% get_popular_entries 3 "custom_template.html" %}

get_similar_entries
-------------------

Display entries similar to an existing entry.

**Prototype:** ``get_similar_entries(number=5, template="zinnia/tags/similar_entries.html")``

Examples: ::

  {% get_similar_entries %}
  {% get_similar_entries 3 %}
  {% get_similar_entries 3 "custom_template.html" %}

get_calendar_entries
--------------------

Display an HTML calendar with date of publications.

If you don't set the *year* or the *month* parameter, the calendar will
look in the context of the template if one of these variables is set in
this order : ``(month, day, object.creation_date)``.

If no one of these variables is found, the current month will be displayed.

**Prototype:** ``get_calendar_entries(year=auto, month=auto, template="zinnia/tags/calendar.html")``

Examples: ::

  {% get_calendar_entries %}
  {% get_calendar_entries 2011 4 %}
  {% get_calendar_entries 2011 4 "custom_template.html" %}

get_archives_entries
--------------------

Display the archives by month.

**Prototype:** ``get_archives_entries(template="zinnia/tags/archives_entries.html")``

Examples: ::

  {% get_archives_entries %}
  {% get_archives_entries "custom_template.html" %}

get_archives_entries_tree
-------------------------

Display all the archives as a tree.

**Prototype:** ``get_archives_entries_tree(template="zinnia/tags/archives_entries_tree.html")``

Examples: ::

  {% get_archives_entries_tree %}
  {% get_archives_entries_tree "custom_template.html" %}

get_authors
-----------

Display all the published authors.

**Prototype:** ``get_authors(template="zinnia/tags/authors.html")``

Examples: ::

  {% get_authors %}
  {% get_authors "custom_template.html" %}

get_categories
--------------

Display all the categories available.

**Prototype:** ``get_categories(template="zinnia/tags/categories.html")``

Examples: ::

  {% get_categories %}
  {% get_categories "custom_template.html" %}

get_tags
--------

Store in a context variable a queryset of all the published tags.

Example: ::

  {% get_tags as entry_tags %}

get_tag_cloud
-------------

Display a cloud of published tags.

**Prototype:** ``get_tag_cloud(steps=6, template="zinnia/tags/tag_cloud.html")``

Examples: ::

  {% get_tag_cloud %}
  {% get_tag_cloud 9 %}
  {% get_tag_cloud 9 "custom_template.html" %}

get_recent_comments
-------------------

Display the latest comments.

**Prototype:** ``get_recent_comments(number=5, template="zinnia/tags/recent_comments.html")``

Examples: ::

  {% get_recent_comments %}
  {% get_recent_comments 3 %}
  {% get_recent_comments 3 "custom_template.html" %}

get_recent_linkbacks
--------------------

Display the latest linkbacks.

**Prototype:** ``get_recent_linkbacks(number=5, template="zinnia/tags/recent_linkbacks.html")``

Examples: ::

  {% get_recent_linkbacks %}
  {% get_recent_linkbacks 3 %}
  {% get_recent_linkbacks 3 "custom_template.html" %}

zinnia_pagination
-----------------

Display a Digg-like pagination for long list of pages.

**Prototype:** ``zinnia_pagination(page, begin_pages=3, end_pages=3, before_pages=2, after_pages=2, template="zinnia/tags/pagination.html")``

Examples: ::

  {% zinnia_pagination page_obj %}
  {% zinnia_pagination page_obj 2 2 %}
  {% zinnia_pagination page_obj 2 2 3 3 %}
  {% zinnia_pagination page_obj 2 2 3 3 "custom_template.html" %}

zinnia_breadcrumbs
------------------

Display the breadcrumbs for the pages handled by Zinnia.

**Prototype:** ``zinnia_breadcrumbs(separator="/", root_name="Blog", template="zinnia/tags/breadcrumbs.html")``

Examples: ::

  {% zinnia_breadcrumbs %}
  {% zinnia_breadcrumbs ">" "News" %}
  {% zinnia_breadcrumbs ">" "News" "custom_template.html" %}

get_gravatar
------------

Display the `Gravatar
<http://gravater.com>`_ image associated to an email, useful for comments.

**Prototype:** ``get_gravatar(email, size=80, rating='g', default=None)``

Examples: ::

  {% get_gravatar user.email %}
  {% get_gravatar user.email 50 %}
  {% get_gravatar user.email 50 "PG" %}
  {% get_gravatar user.email 50 "PG" "identicon" %}

The usage of the **template** argument allow you to reuse and customize the
rendering of a template tag in a generic way. Like this you can display the
same template tag many times in your pages but with a different appearance.
