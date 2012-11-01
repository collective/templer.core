import os
import tempfile
import unittest2 as unittest
import pkg_resources
import shutil

from paste.script.command import get_commands

from templer.core.base import BaseTemplate
from templer.core.vars import DottedVar
from templer.core.vars import EXPERT

from templer.core.package_template import PackageTemplate


def cd(*args):
    dirname = os.path.join(*args)
    os.chdir(dirname)


class TestPackageTemplate(unittest.TestCase):

    def setUp(self):
        """ set up some basics for the coming tests
        """
        self.vars = [
            DottedVar('egg', 'This is a string variable',
                      title="String Title", default="string", page='Carl',
                      modes=(EXPERT)), ]
        self.template = BaseTemplate('my_name')
        create = get_commands()['create'].load()
        command = create('create')
        command.parse_args(['-t', 'package'])
        command.interactive = False
        self.command = command
        # create a temp directory and move there, remember where we came from
        self.orig_dir = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        cd(self.temp_dir)

    def tearDown(self):
        # after tests are done, return to old working dir and remove the temp
        cd(self.orig_dir)
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = None

    def test_entrypoint(self):
        eps = self._structure_entry_points = list(
            pkg_resources.iter_entry_points('paste.paster_create_template'))
        package = None
        for ep in eps:
            if ep.name == 'package':
                package = ep.name
        self.failIf(package is None)

    def test_template_pre_package(self):
        """Make sure no namespace is inserted"""
        new_template = PackageTemplate('joe')
        vars = {'egg': 'exampleproject'}
        new_template.pre(self.command, self.temp_dir, vars)
        self.failUnless(vars['namespace'] == "")

    def test_template_pre_dot_package(self):
        """Make sure the namespace line is inserted"""
        new_template = PackageTemplate('joe')
        vars = {'egg': 'example.project'}
        new_template.pre(self.command, self.temp_dir, vars)
        expected = "\n      namespace_packages=['example'],"
        self.failUnless(vars['namespace'] == expected, vars['namespace'])

    def test_template_pre_dotdot_package(self):
        """Make sure the namespace line is inserted"""
        new_template = PackageTemplate('joe')
        vars = {'egg': 'example.dotdot.project'}
        new_template.pre(self.command, self.temp_dir, vars)
        expected = "\n      namespace_packages=['example', 'example.dotdot'],"
        self.failUnless(vars['namespace'] == expected, vars['namespace'])
