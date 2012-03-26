# -*- coding: utf-8 -*-

import unittest2 as unittest

import os
import tempfile
import shutil
import datetime

from paste.script.command import get_commands

from templer.core.base import BaseTemplate
from templer.core.base import LICENSE_CATEGORIES

LICENSE_EXPECTATIONS = {
    'asl': ['NOTICE.txt', 'LICENSE.ASL'],
    'bsd': ['LICENSE.txt', ],
    'efl': ['LICENSE.txt', 'LICENSE.EFL'],
    'fdl': ['LICENSE.txt', 'LICENSE.GFDL'],
    'gpl': ['LICENSE.txt', 'LICENSE.GPL'],
    'gpl3': ['LICENSE.txt', 'LICENSE.GPL'],
    'lgpl': ['LICENSE.txt', 'LICENSE.GPL', 'LICENSE.LGPL'],
    'mit': ['LICENSE.txt', ],
    'mpl': ['LICENSE.txt', 'LICENSE.MPL'],
    'mpl11': ['LICENSE.txt', 'LICENSE.MPL'],
    'npl': ['LICENSE.txt', 'LICENSE.NPL'],
    'zpl': ['LICENSE.txt', 'LICENSE.ZPL'],
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
        command.parse_args(['-t', 'nested_namespace'])
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
        all_structures = [ep.name for ep\
                          in self.template.all_structure_entry_points()]
        for license in selectable_licenses:
            self.assertTrue(license in all_structures)

    def test_license_structure(self):
        """ verify that all license structures are well formed
        """
        this_year = datetime.date.today().year
        for this_license in LICENSE_EXPECTATIONS.keys():
            self.license_vars['license_name'] = this_license
            try:
                # base template requires no structures, we should only get
                # license structure
                my_license = self.template.load_structure(
                    self.license_vars['license_name'])
            except IndexError:
                self.fail('unable to find %s license structure' % this_license)

            my_license().write_files(self.command,
                                     self.tempdir,
                                     self.license_vars)

            top = os.listdir(self.tempdir)
            self.assertTrue('docs' in top,
                            'failed to write the docs directory')
            expected = LICENSE_EXPECTATIONS[this_license]
            docs = os.listdir(os.path.join(self.tempdir, 'docs'))
            for filename in expected:
                self.assertTrue(filename in docs,
                                '%s not found in docs dir' % filename)

            bpfh = open(os.path.join(self.tempdir, 'docs', expected[0]), 'r')
            bp = bpfh.read()
            self.assertTrue(self.license_vars['author'] in bp,
                            'Author not in license boilerplate')
            self.assertTrue(self.license_vars['project'] in bp,
                            'Project name not in license boilerplate')
            self.assertTrue(str(this_year) in bp,
                            'Current year not in license boilerplate')
            # clean up
            bpfh.close()
            shutil.rmtree(self.tempdir, ignore_errors=True)
            self.tempdir = tempfile.mkdtemp()


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(TestLicenses), ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
