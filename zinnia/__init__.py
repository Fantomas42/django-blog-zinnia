"""Zinnia"""
__version__ = '0.13.dev'
__license__ = 'BSD License'

__author__ = 'Fantomas42'
__email__ = 'fantomas42@gmail.com'

__url__ = 'https://github.com/Fantomas42/django-blog-zinnia'

import django

is_before_1_6 = (django.VERSION[0] < 1) or (django.VERSION[0]
                                            == 1 and django.VERSION[1] < 6)
