
import os
import tempfile
import unittest2 as unittest
import pkg_resources

from paste.script.command import get_commands

from templer.core.base import BaseTemplate
from templer.core.base import get_var
from templer.core.vars import var
from templer.core.vars import BooleanVar
from templer.core.vars import StringVar
from templer.core.vars import TextVar
from templer.core.vars import DottedVar
from templer.core.vars import EXPERT
from templer.core.vars import EASY

from templer.core.package_template import PackageTemplate


def cd(*args):
    dirname = os.path.join(*args)
    os.chdir(dirname)


class TestPackageTemplate(unittest.TestCase):

    def setUp(self):
        """ set up some basics for the coming tests
        """
        self.vars = [
#            var('basic_var', 'This is a basic variable',
#                title="Basic Title", default="foo",
#                modes=(EXPERT, EASY)),
#            BooleanVar('bool_var', 'This is a boolean variable',
#                       title="Boolean Title", default=False, page='Main',
##                       modes=(EASY)),
            DottedVar('egg', 'This is a string variable',
                      title="String Title", default="string", page='Carl',
                      modes=(EXPERT)),]
##            TextVar('txt_var', 'This is a text variable', page='Martin',
#                    title="Text Title", default="text",
#                    modes=()),
#            DottedVar('dot_var', 'This is a dotted variable',
#                      title="Dotted Title", default="dotted.variable")]
        self.template = BaseTemplate('my_name')
        create = get_commands()['create'].load()
        command = create('create')
        command.parse_args(['-t', 'package'])
        command.interactive = False
        self.command = command
        self.orig_dir = os.getcwd()
        self.temp_dir = tempfile.mkdtemp()
        cd(self.temp_dir)

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
        vars = {'egg' : 'exampleproject'}
        new_template.pre(self.command, self.temp_dir, vars)
        self.failUnless(vars['namespace'] == "")

    def test_template_pre_dot_package(self):
        """Make sure the namespace line is inserted"""
        new_template = PackageTemplate('joe')
        vars = {'egg' : 'example.project'}
        new_template.pre(self.command, self.temp_dir, vars)
        self.failUnless(vars['namespace'] == "\n      namespace_packages=['example'],", vars['namespace'])

    def test_template_pre_dotdot_package(self):
        """Make sure the namespace line is inserted"""
        new_template = PackageTemplate('joe')
        vars = {'egg' : 'example.dotdot.project'}
        new_template.pre(self.command, self.temp_dir, vars)
        self.failUnless(vars['namespace'] == "\n      namespace_packages=['example', 'example.dotdot'],", vars['namespace'])
