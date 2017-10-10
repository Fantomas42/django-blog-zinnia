# How to Contribute to Zinnia

Zinnia is an open-source project, so yours contributions are welcomed and needed.

## Did you find a bug?

  * **Ensure the bug was not already reported** by searching on GitHub
    under [Issues](https://github.com/Fantomas42/django-blog-zinnia/issues).

  * If you're unable to find an open issue addressing the problem, [open a
    new one](https://github.com/Fantomas42/django-blog-zinnia/issues/new).
    Be sure to include a **title and clear description**, as much relevant
    information as possible, and a **code sample** or an **executable test
    case** demonstrating the expected behavior that is not occurring.

## Do you want to write code ?

### Process

  1. [Fork](https://github.com/Fantomas42/django-blog-zinnia/fork) and clone the repository on Github.
  2. Create a branch based on ``develop``.
  3. Write tests.
  4. Develop your code.
  5. Update the documentation if needed.
  6. Push your branch and open a pull-request.

### Conventions

Code conventions are important in a way where they ensure the lisibility of
the code in the time, that’s why the code try to respect at most the [PEP 8](https://www.python.org/dev/peps/pep-0008).

If you have already run the buildout script you can execute this Makefile
rule to check your code.

    $ make kwalitee

With a clear and uniform code, the development is better and faster.

### Tests

The submited code should be covered with one or more unittests to ensure
the new behavior and will make easier future developments. Without that,
your code will not be reliable and may not be integrated.

See [testing and coverage](http://docs.django-blog-zinnia.com/en/latest/development/tests.html)
for more informations.

## Do you want to translate ?

If you want to contribute by updating a translation or adding a translation
in your language, it's simple: create a account on Transifex.net and you
will be able to edit the translations at this URL :

https://www.transifex.net/projects/p/django-blog-zinnia/resource/djangopo/

![translation status](http://www.transifex.net/projects/p/django-blog-zinnia/resource/djangopo/chart/image_png)

The translations hosted on Transifex.net will be pulled periodically in the
repository, but if you are in a hurry, [send me a message](https://github.com/Fantomas42).

If you’ve found that a particular piece of text cannot be translated in
your language, because it lacks a plural form, or requires to be split in
two separate sentences to deal with a different gender, you can click the
open issue button to mark your comment as an issue. A developer can then
resolve the issue.

Thanks for contributing!
