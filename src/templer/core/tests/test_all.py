import unittest

from templer.core.tests.test_base import test_suite as base_test_suite
from templer.core.tests.test_vars import test_suite as vars_test_suite
from templer.core.tests.test_script import test_suite as script_test_suite
from templer.core.tests.test_licenses import test_suite as license_test_suite
from templer.core.tests.test_templates import test_suite as doc_test_suite

def test_suite():
    """ wrap all tests in a single test suite, doctests must come last
    """
    suite = unittest.TestSuite([
        base_test_suite(),
        vars_test_suite(),
        script_test_suite(),
        license_test_suite(),
        doc_test_suite(),
    ])
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')