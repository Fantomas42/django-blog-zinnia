from setuptools import setup, find_packages
import os

version = '0.5'

setup(name='django-blog-zinnia',
      version=version,
      
      description='A clear and powerfull weblog application powered with Django',
      long_description=open(os.path.join('README.rst')).read(),
      keywords='django, blog',

      author='Fantomas42',
      author_email='fantomas42@gmail.com',
      url='http://github.com/Fantomas42/django-blog-zinnia',

      packages=find_packages(),
      classifiers=[
          'Development Status :: 4 - Beta',
          'Environment :: Web Environment',
          'Programming Language :: Python',
          'Intended Audience :: Developers',
          'Operating System :: OS Independent',
          'License :: OSI Approved :: BSD License',
          'Topic :: Software Development :: Libraries :: Python Modules',],
            
      license='BSD License',
      include_package_data=True,
      zip_safe=True,
      install_requires=['django-tagging',
                        'akismet',
                        ])


