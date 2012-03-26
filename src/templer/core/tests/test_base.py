# -*- coding: utf-8 -*-

import unittest2 as unittest

from paste.script.command import get_commands

from templer.core.base import BaseTemplate, get_var
from templer.core.vars import var
from templer.core.vars import BooleanVar
from templer.core.vars import StringVar
from templer.core.vars import TextVar
from templer.core.vars import DottedVar
from templer.core.vars import EXPERT
from templer.core.vars import EASY
from templer.core.basic_namespace import BasicNamespace
from templer.core.nested_namespace import NestedNamespace


class test_base_template(unittest.TestCase):
    """ test for methods on the base template class
    """

    def setUp(self):
        """ set up some basics for the coming tests
        """
        self.vars = [
            var('basic_var', 'This is a basic variable',
                title="Basic Title", default="foo",
                modes=(EXPERT, EASY)),
            BooleanVar('bool_var', 'This is a boolean variable',
                       title="Boolean Title", default=False, page='Main',
                       modes=(EASY)),
            StringVar('str_var', 'This is a string variable',
                      title="String Title", default="string", page='Carl',
                      modes=(EXPERT)),
            TextVar('txt_var', 'This is a text variable', page='Martin',
                    title="Text Title", default="text",
                    modes=()),
            DottedVar('dot_var', 'This is a dotted variable',
                      title="Dotted Title", default="dotted.variable")]
        self.template = BaseTemplate('my_name')
        create = get_commands()['create'].load()
        command = create('create')
        command.parse_args(['-t', 'nested_namespace'])
        self.command = command

    def test_filter_for_modes(self):
        """ _filter_for_modes should return a dictionary of var names to
            be hidden from view dependent on the running mode of zopeskel
            and the modes property of each variable
        """
        easy_vars = [var.name for var in self.vars
                     if EASY not in var.modes]
        expert_vars = [var.name for var in self.vars
                       if EXPERT not in var.modes]

        expert_mode = EASY
        hidden = self.template._filter_for_modes(expert_mode, self.vars)

        self.assertEqual(len(hidden), 2)
        for varname in hidden.keys():
            self.assertTrue(varname in easy_vars,
                            "missing easy var: %s" % varname)

        expert_mode = EXPERT
        hidden = self.template._filter_for_modes(expert_mode, self.vars)

        self.assertEqual(len(hidden), 2)
        for varname in hidden.keys():
            self.assertTrue(varname in expert_vars,
                            "missing expert var: %s" % varname)

    def test_get_vars(self):
        """ get_vars is not a method of BaseTemplate, but we've got a nice set
            of variables all set up in here, so let's use it
        """
        var = get_var(self.vars, 'basic_var')
        self.assertEqual(var.name, 'basic_var')
        self.assertEqual(var.title, 'Basic Title')
        self.assertEqual(var.description, 'This is a basic variable')
        self.assertEqual(var.modes, (EXPERT, EASY))
        self.assertEqual(var.default, 'foo')

    def test_pages(self):
        """ pagaes provide discreet sets of template questions for web GUI
        """

        class MyTemplate(BaseTemplate):
            vars = BaseTemplate.vars + self.vars

        template = MyTemplate('some_name')
        pages = template.pages
        self.assertEqual(len(pages), 4)

        page = pages.pop(0)
        self.assertEqual(page['name'], 'Begin')
        questions = page['vars']
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].name, 'expert_mode')
        page = pages.pop(0)
        self.assertEqual(page['name'], 'Main')
        questions = page['vars']
        self.assertEqual(len(questions), 3)
        self.assertEqual(questions[0].name, 'basic_var')
        self.assertEqual(questions[1].name, 'bool_var')
        self.assertEqual(questions[2].name, 'dot_var')

        page = pages.pop(0)
        self.assertEqual(page['name'], 'Carl')
        questions = page['vars']
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].name, 'str_var')

        page = pages.pop(0)
        self.assertEqual(page['name'], 'Martin')
        questions = page['vars']
        self.assertEqual(len(questions), 1)
        self.assertEqual(questions[0].name, 'txt_var')

    def test_get_position_in_stack(self):
        """ verify that the position of a template can be reliably found
        """
        stack = self.template.get_template_stack(self.command)
        self.assertRaises(
            ValueError, self.template.get_position_in_stack, stack)

        new_template = NestedNamespace('joe')
        self.assertEqual(
            new_template.get_position_in_stack(stack), len(stack) - 1)

    def test_get_template_stack(self):
        """ verify that running this command against a create command
            with the argument '-t nested_namespace' returns the expected vals
        """
        stack = self.template.get_template_stack(self.command)
        self.assertEqual(len(stack), 1)

        self.assertFalse(self.template.__class__ in
                    [t.__class__ for t in stack], "%s" % stack)
        new_template = NestedNamespace('joe')
        self.assertTrue(new_template.__class__ in
                        [t.__class__ for t in stack], "%s" % stack)

        errmsg = "%s does not appear to be a subclass of %s"
        for c in [t.__class__ for t in stack]:
            self.assertTrue(isinstance(new_template, c),
                            errmsg % (new_template, c))

    def test_should_print_subcommands(self):
        """ Subcommands should be printed after the template runs
        """
        b_template = BasicNamespace('tom')
        n_template = NestedNamespace('bob')
        # pretend the nested_namespace template provides localcommands (it
        # doesn't have to actually provide them, just claim that it does)
        n_template.use_local_commands = True

        self.assertFalse(b_template.should_print_subcommands(self.command))
        self.assertTrue(n_template.should_print_subcommands(self.command))


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(test_base_template),
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
