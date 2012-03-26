# -*- coding: utf-8 -*-

import unittest2 as unittest

import sys
from templer.core.vars import var
from templer.core.vars import BooleanVar
from templer.core.vars import StringVar
from templer.core.vars import TextVar
from templer.core.vars import DottedVar
from templer.core.vars import OnOffVar
from templer.core.vars import IntVar
from templer.core.vars import BoundedIntVar
from templer.core.vars import ValidationException


class test_var(unittest.TestCase):
    """ test that there is no default implementation of the validation method
    """

    def setUp(self):
        self.var = var('name', 'description')
        self.svar = var('name', 'description',
                        structures={'False': 'foo', 'True': 'bar'})

    def testValidation(self):
        """ the validation method should raise a ValidationException
        """
        msg = "The validation method should not be implemented on the basic "
        msg += "var class"
        try:
            self.var.validate('foo')
        except NotImplementedError:
            pass
        else:
            self.fail(msg)

    def testPrettyDescription(self):
        """ pretty_description should return a combination of title or name
            and description
        """
        self.assertEqual(self.var.pretty_description(), 'name (description)')

        self.var.title = 'title'
        self.assertEqual(self.var.pretty_description(), 'title (description)')

    def testFurtherHelp(self):
        """ further_help will return the extensive help string set for a var
            or a default 'nothing to see here' string
        """
        default = "Sorry, no further help is available for name\n"
        self.assertEqual(self.var.further_help(), default)

        self.var.help = "I'm a little help text, short and stout"
        self.assertEqual(self.var.further_help(),
                         "I'm a little help text, short and stout")

    def testIsStructural(self):
        self.assertTrue(self.svar._is_structural,
                        'svar is not structural, but should be')
        self.assertFalse(self.var._is_structural,
                         'var is structural, but should not be')

    def testBadStructureRaisesValueError(self):
        self.assertRaises(ValueError, var,
                          'name', 'description', structures=['foo', 'bar'])


class test_BooleanVar(unittest.TestCase):
    """ verify functionality of the BooleanVar variable class
    """

    def setUp(self):
        self.bvar = BooleanVar('name', 'description')

    def testValidation(self):
        """ check to see that various inputs result in a Boolean Value
        """
        for val in ('f', 'F', 'n', 'N', 'false', 0):
            self.assertFalse(self.bvar.validate(val))

        for val in ('t', 'T', 'y', 'Y', 'true', 1):
            self.assertTrue(self.bvar.validate(val))

        self.assertRaises(ValidationException, self.bvar.validate,
                          'humpty-dumpty')


class test_OnOffVar(unittest.TestCase):
    """ verify functionality of the OnOffVar variable class
    """

    def setUp(self):
        self.ovar = OnOffVar('name', 'description')

    def testValidation(self):
        """ check to see that various inputs result in a Boolean Value
        """
        for val in ('f', 'F', 'n', 'N', 'false', 0, 'off'):
            self.assertEqual(self.ovar.validate(val), 'off')

        for val in ('t', 'T', 'y', 'Y', 'true', 1, 'on'):
            self.assertEqual(self.ovar.validate(val), 'on')

        self.assertRaises(ValidationException, self.ovar.validate, 'lunchbox')


class test_IntVar(unittest.TestCase):
    """ verify functionality of the IntVar variable class
    """

    def setUp(self):
        self.ivar = IntVar('name', 'description')

    def testValidation(self):
        """ an IntVar should take values that can be cast to an integer,
            any other value should raise a ValidationException
        """
        self.assertEqual(1, self.ivar.validate(1))
        self.assertEqual(1, self.ivar.validate(1.9))
        self.assertEqual(1, self.ivar.validate('1'))

        self.assertRaises(ValidationException, self.ivar.validate, 'one')


class test_BoundedIntVar(unittest.TestCase):
    """ verify functionality of the BoundedIntVar variable class
    """

    def setUp(self):
        self.bivar = BoundedIntVar('name', 'description', min=3, max=10)
        self.defaultminvar = BoundedIntVar('name', 'description', max=10)
        self.defaultmaxvar = BoundedIntVar('name', 'description', min=3)
        self.max = sys.maxint
        self.min = -self.max - 1

    def testValidation(self):
        """ A BoundedIntVar should take values between min and max (inclusive)
            If max is not provided, default to sys.maxint
            if min is not provided, default to -sys.maxint-1
        """
        self.assertEqual(4, self.bivar.validate(4))
        self.assertEqual(5, self.bivar.validate(5.9))
        self.assertEqual(6, self.bivar.validate('6'))

        self.assertRaises(ValidationException, self.bivar.validate, 'four')
        self.assertRaises(ValidationException, self.bivar.validate, 1)
        self.assertRaises(ValidationException, self.bivar.validate, 11)

        self.assertEqual(self.max, self.defaultmaxvar.validate(self.max))
        self.assertEqual(self.min, self.defaultminvar.validate(self.min))


class test_StringVar(unittest.TestCase):
    """ verify functionality of the StringVar variable class
    """

    def setUp(self):
        self.svar = StringVar('name', 'description')

    def testValidation(self):
        """ check to see that validation returns appropriate values:
                string should have no spaces at front or back
                unicode strings and regular strings should pass through
                unchanged non-string values raise validation errors
        """
        val = 'george'
        self.assertEqual(val, self.svar.validate(val))

        val = u'george'
        self.assertEqual(val, self.svar.validate(val))

        val = ' hello '
        validated = self.svar.validate(val)
        self.assertNotEqual(validated[0], ' ')
        self.assertNotEqual(validated[-1], ' ')
        self.assertTrue(validated in val)

        for val in (0, True):
            self.assertRaises(ValidationException, self.svar.validate, val)


class test_TextVar(unittest.TestCase):
    """ verify functionality of the TextVar variable class
    """

    def setUp(self):
        self.tvar = TextVar('name', 'description')

    def testValidation(self):
        """ we will test this more thoroughly when it does something useful
            that is different than validation for the parent class above.
        """
        pass


class test_DottedVar(unittest.TestCase):

    def setUp(self):
        self.dvar = DottedVar('name', 'description')

    def testValidation(self):
        """ all parts of a dotted name must be valid python identifiers
        """
        for val in ('this.package', '_foo_.bar', '__class__.__name__'):
            self.assertEqual(val, self.dvar.validate(val))

        for val in ('ham-and-eggs.yummy', 'spam.yucky!'):
            self.assertRaises(ValidationException, self.dvar.validate, val)


def test_suite():
    suite = unittest.TestSuite([
        unittest.makeSuite(test_var),
        unittest.makeSuite(test_BooleanVar),
        unittest.makeSuite(test_OnOffVar),
        unittest.makeSuite(test_IntVar),
        unittest.makeSuite(test_BoundedIntVar),
        unittest.makeSuite(test_StringVar),
        unittest.makeSuite(test_TextVar),
        unittest.makeSuite(test_DottedVar),
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
