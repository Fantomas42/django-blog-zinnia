Buildout
========

To increase the speed of the development process a `Buildout
<http://pypi.python.org/pypi/zc.buildout>`_ script is provided to properly
initialize the project for anybody who wants to contribute to the project.

First of all, please use `VirtualEnv
<http://pypi.python.org/pypi/virtualenv>`_ to protect your system, it's
not mandatory but handy.

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

Run this command to launch the test suite. ::

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
