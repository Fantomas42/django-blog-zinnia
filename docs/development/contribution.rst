======================
Contributing to Zinnia
======================

.. highlightlang:: console

Zinnia is an open-source project, so yours contributions are welcomed and
needed.

.. _writing-code:

Writing code
============

So you have a great idea to program, found a bug or a way to optimize the
code ? You are welcome.

.. _code-process:

Process
-------

#. `Fork`_ and clone the repository on Github.
#. Create a branch based on ``develop``.
#. Write tests.
#. Develop your code.
#. Update the documentation if needed.
#. Push your branch and open a pull-request.

Once the pull-request is open, the continuous integration server will build
your pull-request. If the build is passing, your contribution has great
chances to be integrated quickly.

.. _code-conventions:

Conventions
-----------

Code conventions are important in a way where they ensure the lisibility
of the code in the time, that's why the code try to respect at most the
:pep:`8`.

If you have already :ref:`run the buildout<running-the-buildout>` script
you can execute this Makefile rule to check your code. ::

  $ make kwalitee

With a clear and uniform code, the development is better and faster.

.. _writing-tests:

Tests
-----

The submited code should be covered with one or more unittests to ensure the
new behavior and will make easier future developments. Without that, your
code will not be reliable and may not be integrated.

See :doc:`tests` for more informations.

.. _writing-documentation:

Writing documentation
=====================

Sometimes considered like "annoying" by hard-core coders, documentation is
more important than the code itself! This is what brings fresh blood to a
project, and serves as a reference for old timers.

On top of this, documentation is the one area where less technical people
can help most - you just need to write a semi-decent English. People need
to understand you. We don’t care about style or correctness.

The documentation should :

* Use **Sphinx** and **restructuredText**.
* Use **.rst** as file extension.
* Be written in English.
* Be accessible. You should assume the reader to be moderately familiar
  with Python and Django, but not anything else.

Keep it mind that documenting is most useful than coding, so your
contribution will be greatly appreciated.

.. _contributing-changes-documentation:

Contributing changes
--------------------

Contribute changes to the documentation in the same fashion as committing to
source code.  Essentially, you will fork the project on github, make your
changes to the documentation, commit them, and submit a pull request.

See :ref:`code process<code-process>` for more details.

.. _writing-translations:

Translations
============

If you want to contribute by updating a translation or adding a translation
in your language, it's simple: create a account on Transifex.net and you
will be able to edit the translations at this URL :

https://www.transifex.net/projects/p/django-blog-zinnia/resource/djangopo/

.. image:: http://www.transifex.net/projects/p/django-blog-zinnia/resource/djangopo/chart/image_png

The translations hosted on Transifex.net will be pulled periodically in the
repository, but if you are in a hurry, `send me a message`_.

.. _`Fork`: https://github.com/Fantomas42/django-blog-zinnia/fork
.. _`send me a message`: https://github.com/Fantomas42
