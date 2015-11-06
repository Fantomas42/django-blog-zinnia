=============
Template Tags
=============

.. module:: zinnia.templatetags

.. highlightlang:: html+django

Zinnia provides several template tags based on
:ref:`inclusion_tag<howto-custom-template-tags-inclusion-tags>` system to
create some **widgets** in your Web site's templates.

.. note::

   The presence of the ``template`` argument in many template tags allow you
   to reuse and customize the rendering of a template tag in a generic
   way. Like that you can display the same template tag many times in your
   pages but with a different appearance.

To start using any of the following template tags you need to load them
first at the top of your template: ::

  {% load zinnia %}

.. module:: zinnia.templatetags.zinnia

.. templatetag:: get_recent_entries

get_recent_entries
==================

Display the latest entries.

.. autofunction:: get_recent_entries

Usage examples: ::

  {% get_recent_entries %}
  {% get_recent_entries 3 %}
  {% get_recent_entries 3 "custom_template.html" %}
  {% get_recent_entries template="custom_template.html" %}

.. templatetag:: get_featured_entries

get_featured_entries
====================

Display the featured entries.

.. autofunction:: get_featured_entries

Usage examples: ::

  {% get_featured_entries %}
  {% get_featured_entries 3 %}
  {% get_featured_entries 3 "custom_template.html" %}
  {% get_featured_entries template="custom_template.html" %}

.. templatetag:: get_draft_entries

get_draft_entries
=================

Display the latest entries marked as draft.

.. autofunction:: get_draft_entries

Usage examples: ::

  {% get_draft_entries %}
  {% get_draft_entries 3 %}
  {% get_draft_entries 3 "custom_template.html" %}
  {% get_draft_entries template="custom_template.html" %}

.. templatetag:: get_random_entries

get_random_entries
==================

Display random entries.

.. autofunction:: get_random_entries

Usage examples: ::

  {% get_random_entries %}
  {% get_random_entries 3 %}
  {% get_random_entries 3 "custom_template.html" %}
  {% get_random_entries template="custom_template.html" %}

.. templatetag:: get_popular_entries

get_popular_entries
===================

Display popular entries.

.. autofunction:: get_popular_entries

Usage examples: ::

  {% get_popular_entries %}
  {% get_popular_entries 3 %}
  {% get_popular_entries 3 "custom_template.html" %}
  {% get_popular_entries template="custom_template.html" %}

.. templatetag:: get_similar_entries

get_similar_entries
===================

Display entries similar to an existing entry.

.. autofunction:: get_similar_entries

Usage examples: ::

  {% get_similar_entries %}
  {% get_similar_entries 3 %}
  {% get_similar_entries 3 "custom_template.html" %}
  {% get_similar_entries template="custom_template.html" %}

.. templatetag:: get_calendar_entries

get_calendar_entries
====================

Display an HTML calendar with date of publications.

If you don't set the *year* or the *month* parameter, the calendar will
look in the context of the template if one of these variables is set in
this order : ``(month, day, object.creation_date)``.

If no one of these variables is found, the current month will be displayed.

.. autofunction:: get_calendar_entries

Usage examples: ::

  {% get_calendar_entries %}
  {% get_calendar_entries 2011 4 %}
  {% get_calendar_entries 2011 4 "custom_template.html" %}
  {% get_calendar_entries template="custom_template.html" %}
  {% get_calendar_entries year=object.creation_date|date:"Y" month=12 %}

.. templatetag:: get_archives_entries

get_archives_entries
====================

Display the archives by month.

.. autofunction:: get_archives_entries

Usage examples: ::

  {% get_archives_entries %}
  {% get_archives_entries "custom_template.html" %}

.. templatetag:: get_archives_entries_tree

get_archives_entries_tree
=========================

Display all the archives as a tree.

.. autofunction::  get_archives_entries_tree

Usage examples: ::

  {% get_archives_entries_tree %}
  {% get_archives_entries_tree "custom_template.html" %}

.. templatetag:: get_authors

get_authors
===========

Display all the published authors.

.. autofunction:: get_authors

Usage examples: ::

  {% get_authors %}
  {% get_authors "custom_template.html" %}

.. templatetag:: get_categories

get_categories
==============

Display all the published categories.

.. autofunction:: get_categories

Usage examples: ::

  {% get_categories %}
  {% get_categories "custom_template.html" %}

.. templatetag:: get_categories_tree

get_categories_tree
===================

Display a hierarchical tree of all the categories available.

.. autofunction:: get_categories_tree

Usage examples: ::

  {% get_categories_tree %}
  {% get_categories "custom_template.html" %}

.. templatetag:: get_tags

get_tags
========

Store in a context variable a queryset of all the published tags.

.. autofunction:: get_tags

Usage example: ::

  {% get_tags as entry_tags %}

.. templatetag:: get_tag_cloud

get_tag_cloud
=============

Display a cloud of published tags.

.. autofunction:: get_tag_cloud

Usage examples: ::

  {% get_tag_cloud %}
  {% get_tag_cloud 9 %}
  {% get_tag_cloud 9 3 %}
  {% get_tag_cloud 9 3 "custom_template.html" %}
  {% get_tag_cloud template="custom_template.html" %}

.. templatetag:: get_recent_comments

get_recent_comments
===================

Display the latest comments.

.. autofunction:: get_recent_comments

Usage examples: ::

  {% get_recent_comments %}
  {% get_recent_comments 3 %}
  {% get_recent_comments 3 "custom_template.html" %}
  {% get_recent_comments template="custom_template.html" %}

.. templatetag:: get_recent_linkbacks

get_recent_linkbacks
====================

Display the latest linkbacks.

.. autofunction:: get_recent_linkbacks

Usage examples: ::

  {% get_recent_linkbacks %}
  {% get_recent_linkbacks 3 %}
  {% get_recent_linkbacks 3 "custom_template.html" %}
  {% get_recent_linkbacks template="custom_template.html" %}

.. templatetag:: zinnia_pagination

zinnia_pagination
=================

Display a Digg-like pagination for long list of pages.

.. autofunction:: zinnia_pagination

Usage examples: ::

  {% zinnia_pagination page_obj %}
  {% zinnia_pagination page_obj 2 2 %}
  {% zinnia_pagination page_obj 2 2 3 3 %}
  {% zinnia_pagination page_obj 2 2 3 3 "custom_template.html" %}
  {% zinnia_pagination page_obj begin_pages=2 template="custom_template.html" %}

.. templatetag:: zinnia_breadcrumbs

zinnia_breadcrumbs
==================

Display the breadcrumbs for the pages handled by Zinnia.

.. autofunction:: zinnia_breadcrumbs

Usage examples: ::

  {% zinnia_breadcrumbs %}
  {% zinnia_breadcrumbs "News" %}
  {% zinnia_breadcrumbs "News" "custom_template.html" %}
  {% zinnia_breadcrumbs template="custom_template.html" %}

.. templatetag:: zinnia_loop_template

zinnia_loop_template
====================

Store in a context variable a :class:`~django.template.base.Template`
choosen from his position whithin a loop of entries.

.. autofunction:: zinnia_loop_template

Usage example: ::

  {% for object in object_list %}
    {% zinnia_loop_template "my-template.html" as template %}
    {% include template %}
  {% endfor %}

.. templatetag:: zinnia_statistics

zinnia_statistics
=================

Display the statistics about the contents handled in Zinnia.

.. autofunction:: zinnia_statistics

Usage examples: ::

  {% zinnia_statistics %}
  {% zinnia_statistics "custom_template.html" %}

.. templatetag:: get_gravatar

get_gravatar
============

Display the `Gravatar
<http://gravater.com>`_ image associated to an email, useful for comments.

.. autofunction:: get_gravatar

Usage examples: ::

  {% get_gravatar user.email %}
  {% get_gravatar user.email 50 %}
  {% get_gravatar user.email 50 "PG" %}
  {% get_gravatar user.email 50 "PG" "identicon" "https" %}
  {% get_gravatar user.email rating="PG" protocol="https" %}

.. templatefilter:: widont

widont
======

Insert a non-breaking space between the last two words of your sentence.

.. autofunction:: widont

Usage example: ::

  {{ variable|widont }}

.. templatefilter:: week_number

week_number
===========

Return the Python week number of a date.

.. autofunction:: week_number

Usage example: ::

  {{ date_variable|week_number }}

.. templatefilter:: comment_admin_urlname

comment_admin_urlname
=====================

Return an admin URL for managing the comments, whatever the the application
used.

.. autofunction:: comment_admin_urlname

Usage example: ::

  {% url 'changelist'|comment_admin_urlname %}

.. templatefilter:: user_admin_urlname

user_admin_urlname
=====================

Return an admin URL for managing the users, whatever the the application
used.

.. autofunction:: user_admin_urlname

Usage example: ::

  {% url 'changelist'|user_admin_urlname %}
