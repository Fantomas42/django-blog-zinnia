import os
from setuptools import setup, find_packages

import zinnia

setup(name='django-blog-zinnia',
      version=zinnia.__version__,

      description='A clear and powerfull weblog application powered with Django',
      long_description='\n'.join([open('README.rst').read(),
                                  open(os.path.join('docs', 'notes',
                                                    'changelog.rst')).read(),]),
      keywords='django, blog, weblog, zinnia, post, news',

      author=zinnia.__author__,
      author_email=zinnia.__email__,
      url=zinnia.__url__,

      packages=find_packages(exclude=['demo']),
      classifiers=[
          'Framework :: Django',
          'Development Status :: 5 - Production/Stable',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: BSD License',
          'Topic :: Software Development :: Libraries :: Python Modules',],

      license=zinnia.__license__,
      include_package_data=True,
      zip_safe=False,
      install_requires=['BeautifulSoup>=3.2.0',
                        'django-mptt>=0.5.2',
                        'django-tagging>=0.3.1',
                        'django-xmlrpc>=0.1.3',
                        'pyparsing>=1.5.5',
                        ])
