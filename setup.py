import os
from setuptools import setup, find_packages

import zinnia

setup(name='django-blog-zinnia',
      version=zinnia.__version__,
      
      description='A clear and powerfull weblog application powered with Django',
      long_description=open(os.path.join('README.rst')).read(),
      keywords='django, blog',

      author=zinnia.__author__,
      author_email=zinnia.__email__,
      url=zinnia.__url__,

      packages=find_packages(),
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
      install_requires=['django-tagging',
                        'django-mptt==0.3.1',
                        'akismet',
                        'BeautifulSoup',
                        ])


