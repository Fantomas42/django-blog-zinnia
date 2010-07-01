From WordPress to Zinnia
========================

Zinnia provides a command for importing export files from WordPress.

http://codex.wordpress.org/Tools_Export_SubPanel

Once you have the XML file, you simply have to do this. ::

  $> python manage.py wp2zinnia path/to/your/wordpress.xml

This command will associate the post's authors to User and
import the tags, categories, post and comments.

For the options execute this. ::

  $> python manage.py help wp2zinnia

