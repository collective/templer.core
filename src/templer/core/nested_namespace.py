import copy

from templer.core.base import get_var
from templer.core.vars import EXPERT
from templer.core.basic_namespace import BasicNamespace
from templer.core.vars import DottedVar

VAR_NS2 = DottedVar(
            'namespace_package2',
            title='Nested Namespace Package Name',
            description='Name of inner namespace package',
            default='nested',
            modes=(EXPERT, ),
            page='Namespaces',
            help="""
This is the name of the inner namespace package (Python folder) for this
project. For example, in 'plone.app.example', this would be
'app' ('plone' will be the first namespace, and 'example' would be
the package name).
"""
)


class NestedNamespace(BasicNamespace):
    _template_dir = 'templates/nested_namespace'
    summary = "A basic Python project with a nested namespace (2 dots in name)"
    ndots = 2
    help = """
This creates a Python project without any Zope or Plone features.
"""
    required_templates = []
    use_cheetah = True

    vars = copy.deepcopy(BasicNamespace.vars)
    get_var(vars, 'namespace_package').default = 'my'
    vars.insert(2, VAR_NS2)
    get_var(vars, 'package').default = 'example'
