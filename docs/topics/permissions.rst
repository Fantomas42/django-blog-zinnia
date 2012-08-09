===========
Permissions
===========

.. module:: zinnia.models.entry

In addition to the **add**, **change** and **delete** permissions
automatically created, the default :class:`Entry` model provides three
extra permissions. These permissions will be used in the admin site to
provide a collaborative work feature when creating and editing the
entries. You can use these permissions in your custom views and templates
and of course change the list of Entry's permissions by
:doc:`/how-to/extending_entry_model`.

.. seealso::
   :attr:`django.db.models.Options.permissions` for more information about
   the permissions on the Django models.

Now let's move on to the descriptions and implementations of these
permissions.

.. _can-view-all:

Can view all entries
====================

In the admin site, this permission is used to limit the entries displayed
and editable by a staff member. If the user does not have this permission,
only his own entries will be editable. It's particulary useful when you
have multiple authors and you don't want them to be allowed to share the
entries

.. _can-change-status:

Can change status
=================

Thanks to this permission, a user can change the status of an entry. If the
user is not granted with this permission, he will be able to create entries
but they will remain in the ``DRAFT`` status until someone granted with this
permission changes the status to ``PUBLISH``.

Or you can let an user edit your entries without letting him change the
publication status.

.. _can-change-author:

Can change authors
==================

This permission allows a user to change the authors who can participate to
the entries. When you create an entry, you will be its author by default,
unless you set the authors field. If you are granted with this permission,
you can assign any staff member to the authors' list. If you set an author
who does not have the ``can_view_all`` permission, he will now be able to
view the entry.
