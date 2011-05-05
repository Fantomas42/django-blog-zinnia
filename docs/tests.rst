Testing and Coverage
====================

  *"An application without tests, is a dead-born application."*
    Someone very serious

Writing tests is important, maybe more important than coding.

And this for a lot of reasons, but I'm not here to convince you about
the benefits of software testing, some prophets will do it better than me.

* http://en.wikipedia.org/wiki/Software_testing
* http://docs.djangoproject.com/en/dev/topics/testing/

Of course Zinnia is tested using the `unittest
<http://docs.python.org/library/unittest.html>`_ approach.
All the tests belong in the directory *zinnia/tests/*.

Launching the test suite
------------------------

If you have run the :doc:`buildout` script bundled in Zinnia, the tests are
run under `nose
<http://somethingaboutorange.com/mrl/projects/nose/0.11.2/>`_ by launching
this command: ::

  $ ./bin/test

But the tests can also be launched within a django project with the default
test runner: ::

  $ django-admin.py test zinnia --settings=zinnia.testsettings

Coverage
--------

Despite my best efforts, some functionnalities are not yet tested, that's why
I need your help !

As I write these lines the **115** tests in Zinnia cover **93%** of the code
bundled in Zinnia. It's not bad, but the goal (*realistic*) is to reach a
**95%** coverage.

I know that a coverage percent does not represent the quality of the tests,
but increasing this percent will ensure the quality of Zinnia and his
future evolutions.

You can check the actual coverage percent at this url:

http://django-blog-zinnia.com/documentation/coverage/

I hope that you will write some tests and find some bugs. :)
