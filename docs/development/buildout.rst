========
Buildout
========

.. highlightlang:: console

To increase the speed of the development process a `buildout`_ script is
provided to properly initialize the project for anybody who wants to
contribute to the project.

Buildout is a developer oriented tool designed for workings with Python
eggs, so can be used for installing egg-based scripts for personal use.

One of the major force of buildout is that is **repeatable**, it should be
possible to check-in a buildout specification and reproduce the same
software later by checking out the specification and rebuilding.

Actually buildout is actively used for development and deployment.

.. _using-virtualenv:

VirtualEnv
==========

First of all, please use `virtualenv`_ to protect your system, it's not
mandatory but handy.

What problem does virtualenv solve? If you like Python as I do, chances are
you want to use it for other projects besides django-blog-zinnia.
But the more projects you have, the more likely it is that you will be
working with different versions of Python itself, or at least different
versions of Python libraries.
Let’s face it; quite often libraries break backwards compatibility,
and it’s unlikely that any serious application will have zero
dependencies.

So what do you do if two or more of your projects have conflicting
dependencies?
Virtualenv basically enables multiple side-by-side installations of Python,
one for each project. It doesn’t actually install separate copies of
Python, but it does provide a clever way to keep different project
environments isolated.

So if you doesn't already have virtualenv I suggest to you to type one of
the following two commands: ::

  $ sudo easy_install virtualenv

or even better: ::

  $ sudo pip install virtualenv

.. _running-the-buildout:

Running the buildout
====================

Before running the buildout script we will clone the main development
repository of django-blog-zinnia, create a virtual Python environment to
isolate the installation of the required librairies, then bootstrap the
buildout script to finally execute it.

Follow these few command to start the development: ::

  $ git clone git://github.com/Fantomas42/django-blog-zinnia.git
  $ cd django-blog-zinnia
  $ virtualenv .
  $ source ./bin/activate
  $ pip install zc.buildout
  $ ./bin/buildout

The buildout script will resolve all the dependencies needed to develop the
application and install some usefull scripts.

Once the buildout has run, you are ready to hack the Zinnia project.

.. _development-scripts:

Development scripts
===================

Use this command to launch the test suite: ::

  $ ./bin/test

To view the code coverage run this command: ::

  $ ./bin/cover

Execute these commands to check the code conventions: ::

  $ ./bin/flake8 --count -r --exclude=tests.py,migrations zinnia

For building the HTML documentation run this simple command: ::

  $ ./bin/docs

.. _demo-project:

Demo project
============

A demo project using Zinnia, is available once the buildout script has
run. The demo project is usefull when you want to do functionnal testing.

To launch the demo site, execute these commands: ::

  $ ./bin/demo migrate
  $ ./bin/demo runserver

To directly have entries in your demo, run this command: ::

  $ ./bin/demo loaddata helloworld

Pretty easy no ?


.. _`buildout`: http://pypi.python.org/pypi/zc.buildout
.. _`virtualenv`: http://pypi.python.org/pypi/virtualenv
