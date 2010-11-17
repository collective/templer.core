from setuptools import setup, find_packages

version = '0.1a1-dev'

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

setup(name='templer.core',
      version=version,
      description="Core functionality for the templer tool",
      long_description=long_description,
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
      namespace_packages=['templer'],
      include_package_data=True,
      platforms = 'Any',
      zip_safe=False,
      install_requires=[
          'setuptools',
          "PasteScript>=1.7.2",
          "Cheetah>1.0,<=2.2.1",
      ],    
      tests_require=[
        'zc.buildout==1.4.3',
        'Cheetah', 
        'PasteScript'],
      test_suite='templer.core.tests.test_all.test_suite',
      entry_points="""
        [paste.paster_create_template]
        basic_namespace = templer.core:BasicNamespace
        nested_namespace = templer.core:NestedNamespace
        recipe = templer.core:Recipe
        
        [templer.templer_structure]
        bootstrap = templer.core.structures:BootstrapStructure
        egg_docs = templer.core.structures:EggDocsStructure
        gpl = templer.core.structures:GPLStructure
        gpl3 = templer.core.structures:GPL3Structure
        efl = templer.core.structures:EFLStructure
        asl = templer.core.structures:ASLStructure

        [console_scripts]
        zopeskel = templer.core.zopeskel_script:run
        """,
      )
