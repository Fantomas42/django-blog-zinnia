"""Zinnia"""
__version__ = '0.16.dev0'
__license__ = 'BSD License'

__author__ = 'Fantomas42'
__email__ = 'fantomas42@gmail.com'

__url__ = 'https://github.com/Fantomas42/django-blog-zinnia'

default_app_config = 'zinnia.apps.ZinniaConfig'

# Little hack for use MySQL with Python 3.X
try:
    import pymysql
    pymysql.install_as_MySQLdb()
except ImportError:
    pass
