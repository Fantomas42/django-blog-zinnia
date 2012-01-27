=====================
Rewriting Entry's URL
=====================

.. module:: zinnia.models

By default the :class:`Entry` model implements a default
:meth:`~Entry.get_absolute_url` method to retrieve the canonical URL for an
instance onto the Weblog.

.. seealso::
   :meth:`~django.db.models.Model.get_absolute_url` for more information about
   the usage of this method if your are not familiar with this concept.

The result of this method is a string componed of the entry's creation date
and his slug. For example this URL: ``/blog/2011/07/17/how-to-change-url/``
refers to an entry created the 17th July 2011 under the slug
``how-to-change-url``.

This URL pattern is common for most of Weblog engine and have this
following advantages.

* Human readable / SEO Friendly.
* You can remove parts of the URL and find archives.
* The slug is only unique with the creation date, so you can reuse it.

But if you want to change it to a different form, you have to know that
it's possible, by not so easily.

You have to note that the changes required to the Zinnia's code base for
simplifying this customization step in a generic way, are evil, dirty and
unsecure. You will see all along this document why this customization is
not directly implemented and cannot be handled genericly and the pitfalls
to avoid.

.. warning::
   The methods explained below are reserved for confirmed Django developers
   knowing what they are doing. No warranties and not support will be
   provided for the problems encountered if you customize this part of
   Zinnia.

Choosing your new URL pattern
=============================

The get_absolute_url method
===========================

Configuring URLs
================

Adding your view
================
