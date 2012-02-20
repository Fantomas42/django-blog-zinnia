==============================
Customize Zinnia look and feel
==============================

The templates provided for Zinnia are simple but complete and as generic as
possible. But you can easily change them by
`specifying a template directory`_. If you are not familiar with Django,
the part two of the excellent Django tutorial explains in detail
how to proceed for `customizing the look and feel`_ of the
:mod:`~django.contrib.admin` app, in Zinnia it's the same thing.

A good starting point is to copy-paste the :file:`zinnia/base.html` template,
and edit the :ttag:`extends` instruction for fitting to your skin.

.. note::
	* The main content is displayed in block named ``content``.
	* Additional datas are displayed in a block named ``sidebar``.

You can also create your own app containing some Zinnia's templates based
on inheritance. You can also create your own app containing some Zinnia’s
templates based on inheritance. For example you can find these two
applications which aim is to transform the templates for Zinnia to be HTML5
ready, which can be a good starting point to make your own at :

* `Zinnia-theme-html5`_.
* `Django Blog Quintet`_.

.. warning::
   .. versionchanged:: 0.9

   `Django Blog Quintet`_ is no longer compatible with Zinnia, but still be
   a good example.



.. _`specifying a template directory`: https://docs.djangoproject.com/en/dev/ref/templates/api/#loading-templates
.. _`customizing the look and feel`: https://docs.djangoproject.com/en/dev/intro/tutorial02/#customize-the-admin-look-and-feel
.. _`Zinnia-theme-html5`: https://github.com/Fantomas42/zinnia-theme-html5
.. _`Django Blog Quintet`: https://github.com/franckbret/django-blog-quintet