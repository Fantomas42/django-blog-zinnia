"""Setup script of django-blog-zinnia"""
from setuptools import find_packages
from setuptools import setup

import zinnia

setup(
    name='django-blog-zinnia',
    version=zinnia.__version__,

    description='A clear and powerful weblog application powered with Django',
    long_description='\n'.join([open('README.rst').read(),
                                open('CHANGELOG').read()]),
    keywords='django, blog, weblog, zinnia, post, news',

    author=zinnia.__author__,
    author_email=zinnia.__email__,
    url=zinnia.__url__,

    packages=find_packages(exclude=['demo']),
    classifiers=[
        'Framework :: Django',
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'License :: OSI Approved :: BSD License',
        'Topic :: Software Development :: Libraries :: Python Modules'],

    license=zinnia.__license__,
    include_package_data=True,
    zip_safe=False,
    install_requires=['beautifulsoup4>=4.3.2',
                      'django-contrib-comments>=1.7.2',
                      'django-mptt>=0.8.6',
                      'django-tagging>=0.4.5',
                      'django-xmlrpc>=0.1.5',
                      'mots-vides>=2015.5.11',
                      'pillow>=2.0.0',
                      'pyparsing>=2.0.3',
                      'pytz>=2014.10',
                      'regex>=2016.3.2']
)
