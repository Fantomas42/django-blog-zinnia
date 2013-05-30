====================
Testing and Coverage
====================

  *"An application without tests, is a dead-born application."*
    Someone very serious

.. module:: zinnia.tests

.. highlightlang:: console

Writing tests is important, maybe more important than coding.

And this for a lot of reasons, but I'm not here to convince you about
the benefits of software testing, some prophets will do it better than me.

* http://en.wikipedia.org/wiki/Software_testing
* https://docs.djangoproject.com/en/dev/topics/testing/

Of course Zinnia is tested using the `unittest`_  approach.
All the tests belong in the directory :file:`zinnia/tests/`.

.. _lauching-test-suite:

Launching the test suite
========================

If you have :ref:`run the buildout script<running-the-buildout>` bundled in
Zinnia, the tests are run under `nose`_ by launching this command: ::

  $ ./bin/test

But the tests can also be launched within a Django project with the default
test runner: ::

  $ django-admin.py test zinnia --settings=zinnia.testsettings

Using the ``./bin/test`` script is usefull when you develop because the tests
are calibrated to run fast, but testing Zinnia within a Django project even
if it's slow, can prevent some integration issues.

If you want to make some speed optimizations or compare with your tests
results, you can check the actual execution time of the
`tests on Python 2.7`_  online.

.. _coverage:

Coverage
========

Despite my best efforts, some functionnalities are not yet tested, that's why
I need your help !

As I write these lines the **175** tests in Zinnia cover **96%** of the code
bundled in Zinnia. A real effort has been made to obtain this percentage,
for ensuring the quality of the code.

I know that a coverage percent does not represent the quality of the tests,
but maintaining or increasing this percentage ensures the quality of
Zinnia and his future evolutions. For information, you can check the actual
`coverage percent on Python 2.7`_ online.

I hope that you will write some tests and find some bugs. :)

.. _`unittest`: http://docs.python.org/library/unittest.html
.. _`nose`: http://somethingaboutorange.com/mrl/projects/nose/
.. _`tests on Python 2.7`: https://jenkins.shiningpanda.com/django-blog-zinnia/job/Django-Blog-Zinnia/PLATFORM=debian6,PYTHON=StacklessPython-2.7/lastCompletedBuild/testReport/zinnia.tests/
.. _`coverage percent on Python 2.7`: https://jenkins.shiningpanda.com/django-blog-zinnia/job/Django-Blog-Zinnia/PLATFORM=debian6,PYTHON=StacklessPython-2.7/lastCompletedBuild/cobertura/
