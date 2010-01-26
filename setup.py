from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='django-blog-zinnia',
      version=version,
      description='A clear and powerfull weblog application powered with Django',
      long_description=open(os.path.join('README.rst')).read(),
      keywords='django, blog',
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'Topic :: Software Development :: Libraries :: Python Modules',
          ],
      
      author='Fantomas42',
      author_email='fantomas42@gmail.com',
      url='http://github.com/Fantomas42/django-blog-zinnia',
      
      license='GPL',
      packages=['zinnia'],
      include_package_data=True,
      zip_safe=True,
      install_requires=[
          #
      ])

