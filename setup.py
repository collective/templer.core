import sys
from setuptools import setup, find_packages

# # PasteDeploy 1.5.0 is explicitly not python 2.4 compatible, if we are using
# python 2.4, pin PasteDeploy to an earlier version
paste_deploy = "PasteDeploy"
if sys.version_info[1] < 5:
    paste_deploy += "<1.5.0"

version = '1.0b4'

long_description = (
    open('README.txt').read()
    + '\n' +
    'Contributors\n'
    '============\n'
    + '\n' +
    open('CONTRIBUTORS.txt').read()
    + '\n' +
    open('CHANGES.txt').read()
    + '\n')

tests_require = [
    'unittest2',
    'Cheetah',
    'PasteScript'],

setup(name='templer.core',
      version=version,
      description="Core functionality for the templer tool",
      long_description=long_description,
      classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Framework :: Zope2",
        "Framework :: Zope3",
        "Framework :: Plone",
        "Framework :: Plone :: 3.2",
        "Framework :: Plone :: 3.3",
        "Framework :: Plone :: 4.0",
        "Framework :: Plone :: 4.1",
        "Framework :: Buildout",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        'Programming Language :: Python :: 2.4',
        'Programming Language :: Python :: 2.5',
        'Programming Language :: Python :: 2.6',
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Software Development :: Code Generators",
       ],
      keywords='web zope command-line skeleton project',
      author='Cris Ewing',
      author_email='cris@crisewing.com',
      url='https://github.com/collective/templer.core',
      license='MIT',
      packages=find_packages('src'),
      package_dir={'': 'src'},
      namespace_packages=['templer'],
      include_package_data=True,
      platforms='Any',
      zip_safe=False,
      install_requires=[
          'setuptools',
          paste_deploy,
          "PasteScript>=1.7.2",
          "Cheetah>1.0,<=2.2.1",
      ],
      tests_require=tests_require,
      extras_require=dict(test=tests_require),
      entry_points="""
        [paste.paster_create_template]
        basic_namespace = templer.core:BasicNamespace
        nested_namespace = templer.core:NestedNamespace

        [templer.templer_structure]
        egg_docs = templer.core.structures:EggDocsStructure
        asl = templer.core.structures:ASLStructure
        bsd = templer.core.structures:BSDStructure
        efl = templer.core.structures:EFLStructure
        fdl = templer.core.structures:FDLStructure
        gpl = templer.core.structures:GPLStructure
        gpl3 = templer.core.structures:GPL3Structure
        lgpl = templer.core.structures:LGPLStructure
        mit = templer.core.structures:MITStructure
        mpl = templer.core.structures:MPLStructure
        mpl11 = templer.core.structures:MPL11Structure
        npl = templer.core.structures:NPLStructure
        zpl = templer.core.structures:ZPLStructure

        [console_scripts]
        templer = templer.core.zopeskel_script:run
        """,
      )
