Compatibility
=============

Zinnia tries to fit a maximum to the Django's standards to gain in
readability and to be always present when the version 3.4.2 will be
here. :)

Predicting the future is a good thing, because it will be soon.
Actually Zinnia is designed to handle the 1.2.x version and will reach the
release 1.5 easily without major changes.

http://docs.djangoproject.com/en/dev/internals/deprecation/

If you are running on the 1.1.x versions you can also use Zinnia
by applying the patch located in
**patches/compatibility_django_1.1.patch**.

But the patch is not 100% efficient for 1 thing.

The feeds API provided by the django.contrib.syndication in the 1.1
versions is deprecated and the Feed classes provided by has been migrated
to the new API. This migration is actually incompatible with the 1.1
versions.

The patch only avoid the generation of errors when the tests are runned.

So if someone find a good solution to this problem, the patch will be
integrated in the development branch.