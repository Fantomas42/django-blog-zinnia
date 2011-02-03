Developers
==========

Your contributions are welcomed and needed.

Buildout
--------

To increase the speed of the development process a `Buildout
<http://pypi.python.org/pypi/zc.buildout>`_ script is provided to properly
initialize the project for anybody who wants to contribute to the project.

First of all, please use `VirtualEnv
<http://pypi.python.org/pypi/virtualenv>`_ to protect your system.

Follow these steps to start the development : ::

  $ git clone git://github.com/Fantomas42/django-blog-zinnia.git
  $ virtualenv --no-site-packages django-blog-zinnia
  $ cd django-blog-zinnia
  $ source ./bin/activate
  $ python bootstrap.py
  $ ./bin/buildout

The buildout script will resolve all the dependencies needed to develop the
application.

Once these operations are done, you are ready to develop the zinnia project.

Run this command to launch the tests. ::

  $ ./bin/test

To view the code coverage run this command. ::

  $ ./bin/cover

Execute these commands to check the code conventions. ::

  $ ./bin/pyflakes zinnia
  $ ./bin/pep8 --count -r --exclude=tests.py,migrations zinnia

To launch the demo site, execute these commands. ::

  $ ./bin/demo syncdb
  $ ./bin/demo loaddata helloworld
  $ ./bin/demo runserver

And for building the HTML documentation run this. ::

  $ ./bin/docs

Pretty easy no ?

Translations
------------

If you want to contribute by updating a translation or adding a translation
in your language, it's simple: create a account on Transifex.net and you
will be able to edit the translations at this URL :

http://www.transifex.net/projects/p/django-blog-zinnia/resource/djangopo/

.. image:: http://www.transifex.net/projects/p/django-blog-zinnia/resource/djangopo/chart/image_png

The translations hosted on Transifex.net will be pulled periodically in the
repository, but if you are in a hurry, `send me a message
<https://github.com/inbox/new/Fantomas42>`_.

Online resources
----------------

  * `Code repository
    <https://github.com/Fantomas42/django-blog-zinnia>`_.
  * `Documentation
    <http://django-blog-zinnia.com/documentation/>`_.
  * `API documentation
    <http://django-blog-zinnia.com/docs/api/>`_.
  * `Code coverage
    <http://django-blog-zinnia.com/documentation/coverage/>`_.
  * Discussions and help at `Google Group
    <http://groups.google.com/group/django-blog-zinnia/>`_.
  * For reporting a bug use `Github Issues
    <http://github.com/Fantomas42/django-blog-zinnia/issues/>`_.
