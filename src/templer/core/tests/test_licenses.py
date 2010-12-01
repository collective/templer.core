import os
import unittest
import tempfile
import shutil
import datetime

from paste.script.command import get_commands

from templer.core.base import BaseTemplate
from templer.core.base import LICENSE_CATEGORIES

LICENSE_EXPECTATIONS = {
    'ASL': ['NOTICE.txt', 'LICENSE.ASL'],
    'BSD': ['LICENSE.txt',],
    'EFL': ['LICENSE.txt', 'LICENSE.EFL'],
    'FDL': ['LICENSE.txt', 'LICENSE.GFDL'],
    'GPL': ['LICENSE.txt', 'LICENSE.GPL'],
    'GPL3': ['LICENSE.txt', 'LICENSE.GPL'],
    'LGPL': ['LICENSE.txt', 'LICENSE.GPL', 'LICENSE.LGPL'],
    'MIT': ['LICENSE.txt',],
    'MPL': ['LICENSE.txt', 'LICENSE.MPL'],
    'MPL11': ['LICENSE.txt', 'LICENSE.MPL'],
    'NPL': ['LICENSE.txt', 'LICENSE.NPL'],
    'ZPL': ['LICENSE.txt', 'LICENSE.ZPL'],
}

class TestLicenses(unittest.TestCase):
    """ verify that all licenses are registered, findable and output correctly 
    """
    def setUp(self):
        """ set up some basics for the coming tests
        """
        self.template = BaseTemplate('my_name')
        self.license_vars = {
            'author': 'Frank Herbert',
            'author_email': 'fherb@foo.bar.com',
            'license_name': 'GPL',
            'project': 'my.package',
        }
        create = get_commands()['create'].load()
        command = create('create')
        command.parse_args(['-t', 'recipe'])
        self.command = command
        self.command.interactive = False
        self.tempdir = tempfile.mkdtemp()
    
    def tearDown(self):
        """ remove temporary directory """
        shutil.rmtree(self.tempdir, ignore_errors=True)
        self.tempdir = None
    
    def test_entry_point_list(self):
        """ verify that all selectable licenses have entry points 
        """
        selectable_licenses = [k.lower() for k in LICENSE_CATEGORIES.keys()]
        all_structures = [ep.name for ep in self.template.all_structure_entry_points()]
        
        for license in selectable_licenses:
            self.failUnless(license in all_structures)
    
    def test_license_structure(self):
        """ verify that all license structures are well formed
        """
        this_year = datetime.date.today().year
        for this_license in LICENSE_EXPECTATIONS.keys():
            self.license_vars['license_name'] = this_license
            try:
                # base template requires no structures, we should only get
                # license structure
                my_license = self.template.get_structures(self.license_vars)[0]
            except IndexError:
                self.fail('unable to find %s license structure' % this_license)
        
            my_license().write_files(self.command, 
                                     self.tempdir, 
                                     self.license_vars);
        
            top = os.listdir(self.tempdir)
            self.failUnless('docs' in top, 'failed to write the docs directory')
            expected = LICENSE_EXPECTATIONS[this_license]
            docs = os.listdir(os.path.join(self.tempdir, 'docs'))
            for filename in expected:
                self.failUnless(filename in docs, 
                                '%s not found in docs dir' % filename)
            
            bpfh = open(os.path.join(self.tempdir, 'docs', expected[0]), 'r')
            bp = bpfh.read()
            self.failUnless(self.license_vars['author'] in bp, 
                            'Author not in license boilerplate')
            self.failUnless(self.license_vars['project'] in bp, 
                            'Project name not in license boilerplate')
            self.failUnless(str(this_year) in bp, 
                            'Current year not in license boilerplate')
            # clean up
            bpfh.close()
            shutil.rmtree(self.tempdir, ignore_errors=True)
            self.tempdir = tempfile.mkdtemp()

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestLicenses)
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')