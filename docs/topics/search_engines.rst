==============
Search Engines
==============

.. module:: zinnia.views.search

Zinnia like almost all blogging systems contains a
:func:`search engine<entry_search>` feature.

But in fact there are 2 search engines, a basic and an advanced, the
advanced search engine is enabled by default, but if he fails the
basic search engine will resume the job.

.. _basic-search-engine:

Basic Search Engine
===================

The basic search engine is the original engine of Zinnia, and will be used
if the advanced engine cannot be used.

It will always returns more results than the advanced engine, because each
terms of the query will be searched in the entries and the results are
added to a main result list. We can say that the results are inclusives.

Example of a query :
  ``love paris``

  This will returns all the entries containing the terms ``love`` or
  ``paris``.

.. _advanced-search-engine:

Advanced Search Engine
======================

.. module:: zinnia.search

The advanced search engine has several possibilities for making more
elaborated queries, with it's own grammar system.

The grammar of the search is close to the main search engines like Google
or Yahoo.

The main difference with the basic engine is that the results are
exclusives.

For enabling the advanced search engine, you simply need to install the
:mod:`pyparsing` package. Otherelse the basic engine will be used.

.. _advanced-search-examples:

Query examples
--------------

Here a list of examples and possibilities:

Example of a query with terms:
   ``love paris``

   This will returns all the entries containing the terms ``love`` and
   ``paris``.

Example of a query with excluded terms:
   ``paris -hate``

   This will returns all the entries containing the term ``paris`` without
   the term ``hate``.

Example of a query with expressions:
   ``"Paris, I love you"``

   This will returns all the entries containing the expression
   ``Paris, I love you``.

Example of a query with **category operator**:
   ``love category:paris``

   This will returns all the entries containing the term ``love`` filled in
   the category named ``paris``.

Example of a query with **tag operator**:
   ``paris tag:love``

   This will returns all the entries containing the term ``paris`` with the
   tag ``love``.

Example of a query with **author operator**:
   ``paris author:john``

   This will returns all the entries containing the term ``paris`` writed by
   ``john``.

Example of a query with boolean operator:
   ``paris or berlin``

   This will returns all the entries containing the term ``paris`` or
   ``berlin``.

Example of a query with parenthesis:
   ``(paris or berlin) love``

   This will returns all the entries containing the terms ``paris`` or
   ``berlin`` with the term ``love``.

Complex example:
   ``((paris or berlin) and (tag:love or category:meet*)) girl -money``

   This will returns all the entries containing the terms ``paris`` or
   ``berlin`` with the tag ``love`` or filled under the categories starting
   by ``meet`` also containing the term ``girl`` excluding entries with the
   term ``money``.


Note that the query is stripped of common words known as stop words.
These are words such as **on**, **the** or **which** that are generally
not meaningful and cause irrelevant results.
