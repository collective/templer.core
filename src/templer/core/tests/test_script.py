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
        self.assertFalse(processed[2])

        argv.append('--bob=kate')
        processed = self.runner._process_args(argv[:])
        self.assertEqual(processed[0], 'archetype')
        self.assertEqual(processed[1], 'my.project')
        self.assertEqual(processed[2]['--bob'], 'kate')

        # _process_args will allow us to skip the project name argument
        argv.pop(1)
        processed = self.runner._process_args(argv[:])
        self.assertEqual(processed[0], 'archetype')
        self.assertFalse(processed[1])
        self.assertEqual(processed[2]['--bob'], 'kate')

        # providing arguments in '-name val' form is _not_ allowed
        argv = ['archetype', 'my.project', '-bob', 'kate']
        self.assertRaises(SyntaxError, self.runner._process_args, argv[:])

        # the --svn-repository argument is _not_ allowed in any form
        argv = argv[:2] + ['--svn-repository=svn://svn.junk.org/svn']
        self.assertRaises(SyntaxError, self.runner._process_args, argv[:])

        argv[2] = 'svn-repository=svn://svn.junk.org/svn/blah'
        self.assertRaises(SyntaxError, self.runner._process_args, argv[:])

        # providing args in a '-name val' format is not supported
        argv = argv[:2] + ['bob', 'kate']
        self.assertRaises(SyntaxError, self.runner._process_args, argv[:])


    def test_script_errors(self):
        """Verify that the run method catches errors correctly"""
        oldargv = sys.argv

        # non-existent templates are not caught until in 'run'
        sys.argv = ['templer', 'no-template', 'my.package']
        output = run()
        self.assertTrue('ERROR: No such template' in output)

        # calling the script with no arguments at all prints usage
        sys.argv = sys.argv[:1]
        output = run()
        self.assertTrue('Usage:' in output)

        sys.argv = oldargv

    def test_show_help(self):
        oldargv = sys.argv

        # --help produces the DESCRIPTION string
        sys.argv = ['templer', '--help']
        output = run()
        comp = self.runner.texts['description'] % {'script_name': 'templer'}
        self.assertTrue(comp in output,
                        '--help produces incorrect output: %s' % output)

        # the name of the given runner is interposed into the help text
        self.runner.name = newname = 'buzbee berkeley'
        output = run(self.runner)
        self.assertTrue(newname in output)

        sys.argv = oldargv

    def test_list_verbose(self):
        oldargv = sys.argv

        sys.argv = ['templer', '--list']
        output = run()
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

        sys.argv = oldargv

    def test_generate_dotfile(self):
        """Verify that the help features of the script function correctly"""
        oldargv = sys.argv

        cats = list_sorted_templates()
        catnames = cats.keys()
        templates = sum(cats.values(), [])
        tempnames = [t['name'] for t in templates]

        # --make-config-file produces a config file with headings for each
        # template
        sys.argv = ['templer', '--make-config-file']
        output = run()
        for theading in ['[' + name + ']' for name in tempnames]:
            self.assertTrue(theading in output,
                            '%s does not appear in .templer' % theading)

        sys.argv = oldargv

    def test_version(self):
        oldargv = sys.argv
        # --version should output a version number.  make sure it finds
        # something
        sys.argv = ['templer', '--version']
        output = run()
        self.assertFalse('unable' in output)

        sys.argv = oldargv


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(test_control)])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
