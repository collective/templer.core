# -*- coding: utf-8 -*-

import unittest2 as unittest

import sys
import StringIO

# from templer.core.control_script import checkdots
# from templer.core.control_script import process_args
from templer.core.control_script import run
from templer.core.control_script import Runner
from templer.core.ui import list_sorted_templates


def capture_stdout(function):

    def _capture_stdout(*args, **kw):
        newout = StringIO.StringIO()
        oldout = sys.stdout
        sys.stdout = newout
        try:
            function(*args, **kw)
        finally:
            sys.stdout = oldout
            newout.seek(0)
            return newout.read()
    return _capture_stdout

run = capture_stdout(run)


class test_control(unittest.TestCase):
    """Tests for Control script.
    """

    def setUp(self):
        class FauxTemplate:
            pass

        self.runner = Runner()
        self.template = FauxTemplate()

    def test_checkdots_none(self):
        """Verify that checkdots works with templates without ndots hint."""
        try:
            self.runner._checkdots(self.template,
                                   "anything is legal; not a package")
        except ValueError:
            self.fail('checkdots should not have failed with no ndots')

    def test_checkdots_two(self):
        """Verify that checkdots validates templates with ndots hint."""

        self.template.ndots = 2

        for bad in ["nodots", "one.dot", "three.dots.in.this",
                    "two.dots.but not legal"]:
            self.assertRaises(ValueError, self.runner._checkdots,
                              self.template, bad)

        try:
            self.runner._checkdots(self.template, "two.dots.legal")
        except ValueError:
            self.fail('checkdots should not have failed')

    def test_process_args(self):
        """Ensure process_args correctly processes command-line arguments"""
        argv = []

        self.assertRaises(SyntaxError, self.runner._process_args, argv[:])

        argv.append('archetype')
        processed = self.runner._process_args(argv[:])
        self.assertEqual(processed[0], 'archetype')
        self.assertFalse(processed[1])
        self.assertFalse(processed[2])

        argv.append('my.project')
        processed = self.runner._process_args(argv[:])
        self.assertEqual(processed[0], 'archetype')
        self.assertEqual(processed[1], 'my.project')
        self.assertEqual(processed[2], ['my.project'])

        argv.append('--bob=kate')
        processed = self.runner._process_args(argv[:])
        self.assertEqual(processed[0], 'archetype')
        self.assertEqual(processed[1], 'my.project')
        self.assertEqual(processed[2], ['my.project', '--bob=kate'])

        # _process_args will allow us to skip the project name argument
        argv.pop(1)
        processed = self.runner._process_args(argv[:])
        self.assertEqual(processed[0], 'archetype')
        self.assertFalse(processed[1])
        self.assertEqual(processed[2], ['--bob=kate'])

    def test_script_errors(self):
        """Verify that the run method catches errors correctly"""
        # non-existent templates are not caught until in 'run'
        args = ['no-template', 'my.package']
        output = run(*args)
        self.assertTrue('ERROR: No such template' in output)

        # calling the script with no arguments at all prints usage
        output = run()
        self.assertTrue('Usage:' in output)

    def test_show_help(self):
        # --help produces the DESCRIPTION string
        args = ['templer', '--help']
        output = run(*args)
        comp = self.runner.texts['description'] % {'script_name': 'templer'}
        self.assertTrue(comp in output,
                        '--help produces incorrect output: %s' % output)

        # the name of the given runner is interposed into the help text
        self.runner.name = newname = 'buzbee berkeley'
        output = run(*args, runner=self.runner)
        self.assertTrue(newname in output)

    def test_list_verbose(self):
        output = run('--list')
        cats = list_sorted_templates()
        catnames = cats.keys()
        templates = sum(cats.values(), [])
        tempnames = [t['name'] for t in templates]
        tempsums = [t['summary'] for t in templates]
        for cat in catnames:
            self.assertTrue(cat in output, '%s not in --list output' % cat)
        for tname in tempnames:
            self.assertTrue(tname in output, '%s not in --list output' % tname)
        for summary in tempsums:
            self.assertTrue(summary in output,
                            '%s not in --list output' % summary)

    def test_generate_dotfile(self):
        """Verify that the help features of the script function correctly"""
        cats = list_sorted_templates()
        templates = sum(cats.values(), [])
        tempnames = [t['name'] for t in templates]

        # --make-config-file produces a config file with headings for each
        # template
        output = run('--make-config-file')
        for theading in ['[' + name + ']' for name in tempnames]:
            self.assertTrue(theading in output,
                            '%s does not appear in .templer' % theading)

    def test_version(self):
        # --version should output a version number.  make sure it finds
        # something
        output = run('--version')
        self.assertFalse('unable' in output)


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(test_control)])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
