import unittest2 as unittest
import pkg_resources

from templer.core.package_template import PackageTemplate

class TestPackageTemplate(unittest.TestCase):

    def test_entrypoint(self):
        eps = self._structure_entry_points = list(
                pkg_resources.iter_entry_points('paste.paster_create_template'))
        package = None
        for ep in eps:
            if ep.name == 'package':
                package = ep.name
        self.failIf(package is None)

    def test_template_instance(self):
        new_template = PackageTemplate('joe')



