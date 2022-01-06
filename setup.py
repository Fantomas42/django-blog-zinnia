"""Setup script of django-blog-zinnia"""
from setuptools import find_packages
from setuptools import setup

import zinnia

setup(
    dependency_links=[
        "git+https://github.com/arrobalytics/django-tagging.git@027eb90c88ad2d4aead4f50bbbd8d6f0b1678954#egg=django-tagging",
        "git+https://github.com/arrobalytics/django-xmlrpc.git@6cf59c555b207de7ecec75ac962751e8245cf8c9#egg=django-xmlrpc",
        "git+https://github.com/arrobalytics/mots-vides.git@eaeccf73bdb415d0c5559ccd74de360b37a2bbac#egg=mots-vides",
    ],
    name="django-blog-zinnia",
    version=zinnia.__version__,
    description="A clear and powerful weblog application powered with Django",
    long_description="\n".join([open("README.rst").read(), open("CHANGELOG").read()]),
    keywords="django, blog, weblog, zinnia, post, news",
    author=zinnia.__author__,
    author_email=zinnia.__email__,
    url=zinnia.__url__,
    packages=find_packages(exclude=["demo"]),
    classifiers=[
        "Framework :: Django",
        "Development Status :: 5 - Production/Stable",
        "Environment :: Web Environment",
        "Programming Language :: Python :: 3",
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: BSD License",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    license=zinnia.__license__,
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "asgiref>=3.4.1; python_version >= '3.6'",
        "beautifulsoup4>=4.10.0",
        "django>=2.2",
        "django-contrib-comments>=2.1.0",
        "django-js-asset>=1.2.2",
        "django-mptt>=0.13.4",
        "html5lib>=1.1; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3, 3.4'",
        "importlib-metadata>=4.9.0; python_version < '3.10'",
        "markdown>=3.3.6",
        "pillow>=8.4.0",
        "pyparsing>=3.0.6",
        "regex>=2021.11.10",
        "six>=1.16.0; python_version >= '2.7' and python_version not in '3.0, 3.1, 3.2, 3.3'",
        "soupsieve>=2.3.1; python_version >= '3.6'",
        "sqlparse>=0.4.2; python_version >= '3.5'",
        "textile>=4.0.2",
        "webencodings>=0.5.1",
        "zipp>=3.6.0; python_version >= '3.6'",
    ],
)
