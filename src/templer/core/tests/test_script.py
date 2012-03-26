# -*- coding: utf-8 -*-

import unittest2 as unittest

import sys
import StringIO

from templer.core.zopeskel_script import checkdots
from templer.core.zopeskel_script import process_args
from templer.core.zopeskel_script import run
from templer.core.zopeskel_script import DESCRIPTION
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


class test_zopeskel(unittest.TestCase):
    """Tests for ZopeSkel script.
    """

    def test_checkdots_none(self):
        """Verify that checkdots works with templates without ndots hint."""

        class FauxTemplate:
            pass
        t = FauxTemplate()

        checkdots(t, "anything is legal; not a package")

    def test_checkdots_two(self):
        """Verify that checkdots validates templates with ndots hint."""

        class FauxTemplate:
            pass
        t = FauxTemplate()

        t.ndots = 2

        self.assertRaises(ValueError, checkdots, t, "nodots")
        self.assertRaises(ValueError, checkdots, t, "one.dot")
        self.assertRaises(ValueError, checkdots, t, "three.dots.in.this")
        self.assertRaises(ValueError, checkdots, t, "two.dots.but not legal")

        checkdots(t, "two.dots.legal")

    def test_process_args(self):
        """Ensure process_args correctly processes command-line arguments"""
        oldargv = sys.argv

        sys.argv = ['zopskel']
        self.assertRaises(SyntaxError, process_args)

        sys.argv.append('archetype')
        processed = process_args()
        self.assertEqual(processed[0], 'archetype')
        self.assertFalse(processed[1])
        self.assertFalse(processed[2])

        sys.argv.append('my.project')
        processed = process_args()
        self.assertEqual(processed[0], 'archetype')
        self.assertEqual(processed[1], 'my.project')
        self.assertFalse(processed[2])

        sys.argv.append('--bob=kate')
        processed = process_args()
        self.assertEqual(processed[0], 'archetype')
        self.assertEqual(processed[1], 'my.project')
        self.assertEqual(processed[2]['--bob'], 'kate')

        # process_args will allow us to skip the project name argument
        sys.argv.pop(2)
        processed = process_args()
        self.assertEqual(processed[0], 'archetype')
        self.assertFalse(processed[1])
        self.assertEqual(processed[2]['--bob'], 'kate')

        # providing arguments in '-name val' form is _not_ allowed
        sys.argv = ['zopeskel', 'archetype', 'my.project', '-bob', 'kate']
        self.assertRaises(SyntaxError, process_args)

        # the --svn-repository argument is _not_ allowed in any form
        sys.argv = sys.argv[:3] + ['--svn-repository=svn://svn.junk.org/svn']
        self.assertRaises(SyntaxError, process_args)

        sys.argv[3] = 'svn-repository=svn://svn.junk.org/svn/blah'
        self.assertRaises(SyntaxError, process_args)

        # providing args in a '-name val' format is not supported
        sys.argv = sys.argv[:3] + ['bob', 'kate']
        self.assertRaises(SyntaxError, process_args)

        sys.argv = oldargv

    def test_script_errors(self):
        """Verify that the run method catches errors correctly"""
        oldargv = sys.argv

        # non-existent templates are not caught until in 'run'
        sys.argv = ['zopeskel', 'no-template', 'my.package']
        output = run()
        self.assertTrue('ERROR: No such template' in output)

        # calling the script with no arguments at all prints usage
        sys.argv = sys.argv[:1]
        output = run()
        self.assertTrue('Usage:' in output)

        sys.argv = oldargv

    def test_script_features(self):
        """Verify that the help features of the script function correctly"""
        oldargv = sys.argv

        # --help produces the DESCRIPTION string
        sys.argv = ['zopeskel', '--help']
        output = run()
        self.assertTrue(DESCRIPTION in output,
                        '--help produces incorrect output: %s' % output)

        # --list produces a verbose list of all templates by category
        sys.argv = ['zopeskel', '--list']
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

        # --make-config-file produces a config file with headings for each
        # template
        sys.argv = ['zopeskel', '--make-config-file']
        output = run()
        for theading in ['[' + name + ']' for name in tempnames]:
            self.assertTrue(theading in output,
                            '%s does not appear in .zopeskel' % theading)

        # --version should output a version number.  make sure it finds
        # something
        sys.argv = ['zopeskel', '--version']
        output = run()
        self.assertFalse('unable' in output)

        sys.argv = oldargv


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(test_zopeskel)])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
