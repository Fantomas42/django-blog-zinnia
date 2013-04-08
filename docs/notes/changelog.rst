CHANGELOG
=========

0.13
----

* Python 3.0 support
* Display page number in list
* Basic support of custom User
* Django 1.4 is no longer supported

0.12.3
------

* Better ``skeleton.html``
* Better rendering for the slider
* Add view for having a random entry
* Compatibility fix with Django 1.5 in admin
* Fix issue with author detail view paginated
* Better settings for ``ZINNIA_AUTO_CLOSE_*_AFTER``

0.12.2
------

* CSS updates and fixes
* Fix viewport meta tag
* I18n support for the URLs
* Update MarkItUp to v1.1.13
* Update WYMeditor to v1.0.0b3
* Entry's content can be blank
* Compatibility fix for WXR > 1.0
* Fix potential issue on ``check_is_spam``

0.12.1
------

* Microformats improved
* Improve Blogger importer
* Finest control on linkbacks
* Split Entry model into mixins
* Compatibility fix with Django 1.5
* Custom template for content rendering
* Fix Python 2.7 issues with ``wp2zinnia``

0.12
----

* Optimizations on the templates
* Optimizations on the database queries
* Denormalization of the comments
* ``get_authors`` context improved
* ``get_tag_cloud`` context improved
* ``get_categories`` context improved
* Default theme declinations
* Default theme more responsive
* Updating ``helloworld.json`` fixture
* Fix issues with authors in ``wp2zinnia``
* Better integration of the comments system
* Models has been splitted into differents modules

0.11.2
------

* New admin filter for authors
* Minor translation improvements
* Minor documentation improvements
* ``wp2zinnia`` handle wxr version 1.2
* Customizations of the templates with ease
* Define a custom ``Author.__unicode__`` method
* Fix issue with duplicate spam comments
* Fix bug in ``PreviousNextPublishedMixin``
* Fix bug in ``QuickEntry`` with non ascii title
* Fix ``collectstatic`` with ``CachedStaticFilesStorage``

0.11.1
------

* Fix issues with ``get_absolute_url`` and ``zbreadcrumbs``
  when time-zone support is enabled.

0.11
----

* Class-based views
* Time zones support
* Pagination on archives
* Better archive by week view
* Update of the breadcrumbs tag
* Improving ``wp2zinnia`` command
* New ``long_enough`` spam checker
* Custom templates for archive views
* Publication dates become unrequired
* No runtime warnings on Django 1.4
* Django 1.3 is no longer supported
* And a lot of bug fixes

0.10.1
------

* Django 1.4 compatibility support
* Compatibility with django-mptt >= 5.1
* ``zinnia.plugins`` is now removed

0.10
----

* Better default templates
* CSS refactoring with Sass3
* Statistics about the content
* Improvement of the documentation
* Entry's Meta options can be extended
* Django 1.2 is no longer supported
* ``zinnia.plugins`` is deprecated in favor of ``cmsplugin_zinnia``
* And a lot of bug fixes

0.9
---

* Improved URL shortening
* Improved moderation system
* Better support of django-tagging
* Blogger to Zinnia utility command
* OpenSearch capabilities
* Upgraded search engine
* Feed to Zinnia utility command
* And a lot of bug fixes

0.8
---

* Admin dashboard
* Featured entries
* Using Microformats
* Mails for comment reply
* Entry model can be extended
* More plugins for django-cms
* Zinnia to Wordpress utility command
* Code cleaning and optimizations
* And a lot of bug fixes

0.7
---

* Using signals
* Trackback support
* Ping external URLs
* Private posts
* Hierarchical categories
* TinyMCE integration
* Code optimizations
* And a lot of bug fixes

0.6
---

* Handling PingBacks
* Support MetaWeblog API
* Passing to Django 1.2.x
* Breadcrumbs templatetag
* Bug correction in calendar widget
* Wordpress to Zinnia utility command
* Major bug correction on publication system
* And a lot of bug fixes

0.5
---

* Packaging
* Tests added
* Translations
* Better templates
* New templatetags
* Plugins for django-cms
* Twitter and Bit.ly support
* Publishing sources on Github.com

0.4 and before
--------------

* The previous versions of Zinnia were not packaged, and were destinated for a
  personnal use.
