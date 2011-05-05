Spam Checker
============

Spam protection is mandatory when you want to let your users to comment
your entries.

Originally Zinnia provided a only one type of spam protection with the
support of Akismet.

One it's not bad, but it's not enough, because depend of a third-party
service may be a little bit risky.

Now Akismet has been moved in a dedicated module and the moderation system
let you choose the spam checkers to use. With this new feature you can now
write a custom spam checker corresponding to your needs and use it for
moderation your comments.

We can imagine for example that you want to authorize comments from
a white-list of IPs, it's possible by writing a backend.

Note that you can use multiple backends, they are chained, useful for an
maximum protection.


Writing your own spam checker backend
-------------------------------------

Writing a backend for using a custom spam checker is simple as
possible, you only needs to follows 4 rules.

#. In a new python file write a function named **backend** taking in
   parameter : ``content`` the text to verify, ``content_object`` the object
   related to the text and ``request`` the current request.

#. The **backend** function should returns ``True`` if ``content`` is spam
   and ``False`` otherwhise.

#. If the **backend** requires initial configuration you must raise a
   *django.core.exceptions.ImproperlyConfigured* exception if the
   configuration is not valid. The error will be displayed in the console.

#. Register your backend to be used in your project with this setting : ::

    ZINNIA_SPAM_CHECKER_BACKENDS = ('path.to.your.spam.checker.module',)

For a more examples take a look in this folder : *zinnia/spam_checker/backends/*.
