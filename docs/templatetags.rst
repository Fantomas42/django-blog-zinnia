Template Tags
=============

Zinnia provides several template tags based on *inclusion_tag* system to
create some **widgets** in your website's templates.

* get_recent_entries(number=5, template="zinnia/tags/recent_entries.html")

Display the latest entries.

* get_featured_entries(number=5, template="zinnia/tags/featured_entries.html")

Display the featured entries.

* get_random_entries(number=5, template="zinnia/tags/random_entries.html")

Display random entries.

* get_popular_entries(number=5, template="zinnia/tags/popular_entries.html")

Display popular entries.

* get_similar_entries(number=5, template="zinnia/tags/similar_entries.html")

Display entries similar to an existing entry.

* get_calendar_entries(year=auto, month=auto, template="zinnia/tags/calendar.html")

Display an HTML calendar with date of publications.

* get_archives_entries(template="zinnia/tags/archives_entries.html")

Display the archives by month.

* get_archives_entries_tree(template="zinnia/tags/archives_entries_tree.html")

Display all the archives as a tree.

* get_categories(template="zinnia/tags/categories.html")

Display all the categories available.

* get_authors(template="zinnia/tags/authors.html")

Display all the published authors.

* get_recent_comments(number=5, template="zinnia/tags/recent_comments.html")

Display the latest comments.

* get_recent_linkbacks(number=5, template="zinnia/tags/recent_linkbacks.html")

Display the latest linkbacks.

* zinnia_breadcrumbs(separator="/", root_name="Blog", template="zinnia/tags/breadcrumbs.html")

Display the breadcrumbs for the pages handled by Zinnia.

* get_gravatar(email, size=80, rating='g', default=None)

Display the Gravatar image associated to an email, useful for comments.


The usage of the *template* argument allow you to reuse and customize the
rendering of a template tag in a generic way. Like this you can display the
same template tag many times in your pages but with a different form.

