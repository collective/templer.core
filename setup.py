from setuptools import setup, find_packages
import os

version = '1.0-dev'

setup(name='zopeskel.core',
      version=version,
      description="Core functionality for the zopeskel tool",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
          "Development Status :: 2 - Pre-Alpha",
          "Framework :: Zope2",
          "Framework :: Zope3",
          "Framework :: Plone",
          "Intended Audience :: Developers",
          "License :: OSI Approved :: GNU General Public License (GPL)",
          "Programming Language :: Python",
          "Topic :: Internet :: WWW/HTTP",
          "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
       ],
      keywords='web zope command-line skeleton project',
      author='Cris Ewing',
      author_email='cewing@sound-data.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL version 2',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['zopeskel'],
      include_package_data=True,
      platforms = 'Any',
      zip_safe=False,
      install_requires=[
          'setuptools',
          "PasteScript>=1.7.2",
          "Cheetah>1.0,<=2.2.1",
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
