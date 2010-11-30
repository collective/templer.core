import os
import unittest
import tempfile
import shutil
import datetime

from paste.script.command import get_commands

from templer.core.base import BaseTemplate
from templer.core.base import LICENSE_CATEGORIES

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
    
    def test_gpl_structure(self):
        """ verify that the gpl2 license writes correctly, given appropriate values
            
            the base template requires no structures, so the only one we should
            get below is the license structure
        """
        this_year = datetime.date.today().year
        try:
            my_license = self.template.get_structures(self.license_vars)[0]
        except IndexError:
            self.fail('unable to find GPL license structure')
        
        my_license().write_files(self.command, self.tempdir, self.license_vars);
        import pdb; pdb.set_trace( )
        
        top = os.listdir(self.tempdir)
        self.failUnless('docs' in top, 'failed to write the docs directory')
        
        docs = os.listdir(os.path.join(self.tempdir, 'docs'))
        self.failUnless('LICENSE.GPL' in docs, 'GPL License failed to write')
        self.failUnless('LICENSE.txt' in docs, 'license boilerplate failed to write')
        
        bp = open(os.path.join(self.tempdir, 'docs', 'LICENSE.txt'), 'r').read()
        self.failUnless(self.license_vars['author'] in bp, 'Author not in license boilerplate')
        self.failUnless(self.license_vars['project'] in bp, 'Project name not in license boilerplate')
        self.failUnless(str(this_year) in bp, 'Current year not in license boilerplate')

def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestLicenses)
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')