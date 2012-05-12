import copy

from templer.core.base import BaseTemplate
from templer.core.base import LICENSE_CATEGORIES
from templer.core.vars import DottedVar
from templer.core.vars import StringVar
from templer.core.vars import StringChoiceVar
from templer.core.vars import BooleanVar
from templer.core.vars import TextVar
from templer.core.vars import EASY
from templer.core.vars import EXPERT

lower_licenses = map(lambda x: x.lower(), LICENSE_CATEGORIES.keys())
LICENSE_DICT = dict(zip(lower_licenses, lower_licenses))


class BasicNamespace(BaseTemplate):
    _template_dir = 'templates/basic_namespace'
    summary = "A basic Python project with a namespace package"
    ndots = 1
    help = """
This creates a Python project without any Zope or Plone features.
"""
    category = "Core Python"

    required_templates = []
    default_required_structures = ['egg_docs', ]
    use_cheetah = True
    vars = copy.deepcopy(BaseTemplate.vars)
    vars += [
        DottedVar(
            'namespace_package',
            title='Namespace Package Name',
            description='Name of outer namespace package',
            default='my',
            modes=(EXPERT, ),
            page='Namespaces',
            help="""
This is the name of the outer package (Python folder) for this project.
For example, in 'Products.PloneFormGen', this would be 'Products'.
This will often be (for Plone products) 'Products'; it may also be
the name of your company/project, or a common-style name like
(for Plone products) 'collective'.

Note that, for some templates, there may be two namespaces, rather
than one (to create eggs with names like 'plone.app.blog')--in this
case, this would be 'plone', the first of the enclosing namespaces.
            """),

        DottedVar(
            'package',
            title='Package Name',
            description='Name of the inner namespace package',
            default='example',
            modes=(EXPERT, ),
            page='Namespaces',
            help="""
This is the name of the innermost package (Python folder) for this project.
For example, in 'Products.PloneFormGen', this would be 'PloneFormGen'.

Note that, for some templates, there may be only a package name without
a namespace package around it--in this case, this would be just the name
of the package.
"""),

        StringVar(
            'version',
            title='Version',
            description='Version number for project',
            default='1.0',
            modes=(EASY, EXPERT),
            page='Metadata',
            help="""
This becomes the version number of the created package. It will be set
in the egg's setup.py, and may be referred to in other places in the
generated project.
"""
            ),

        StringVar(
            'description',
            title='Description',
            description='One-line description of the project',
            default='',
            modes=(EASY, EXPERT),
            page='Metadata',
            help="""
This should be a single-line description of your project. It will be
used in the egg's setup.py, and, for Zope/Plone projects, may be used
in the GenericSetup profile description.
"""
            ),

        TextVar(
            'long_description',
            title='Long Description',
            description='Multi-line description (in ReST)',
            default='',
            modes=(),
            page='Metadata',
            help="""
This should be a full description for your project. It will be
used in the egg's setup.py.

It should be entered in 'restructured text' format; for information,
see http://docutils.sourceforge.net/rst.html).
"""
            ),

        StringVar(
            'author',
            title='Author',
            description='Name of author for project',
            modes=(),
            page='Metadata',
            help="""
This should be the name of the author of this project. It will be used
in the egg's setup.py, and, for some templates, in the generated
documentation/README files.
"""
            ),

        StringVar(
            'author_email',
            title='Author Email',
            description='Email of author for project',
            modes=(),
            page='Metadata',
            help="""
This should be the name of the author of this project. It will be used
in the egg's setup.py, and, for some templates, in the generated
documentation/README files.
"""
            ),

        StringVar('keywords',
            title='Keywords',
            description='List of keywords, space-separated',
            modes=(),
            page='Metadata',
            help="""
This should be the list of keywords for this project. This will be
used in the egg's setup.py (and, if this egg is later published on
PyPI, will be used to categorize the project).
"""
            ),

        StringVar(
            'url',
            title='Project URL',
            description='URL of the homepage for this project',
            modes=(),
            page='Metadata',
            default='http://svn.plone.org/svn/collective/',
            help="""
This should be a URL for the homepage for this project (if applicable).
It will be used in the egg's setup.py.
"""
            ),

        StringChoiceVar(
            'license_name',
            title='Project License',
            description='Name of license for the project',
            default='GPL',
            modes=(),
            page='Metadata',
            choices=LICENSE_CATEGORIES.keys(),
            structures=LICENSE_DICT,
            help="""
The license that this project is issued under. It will be used in the
egg's setup.py.

Common choices here are 'GPL' (for the GNU General Public License),
'ZPL' (for the Zope Public License', or 'BSD' (for the BSD license).

%s

""" % BaseTemplate('null').readable_license_options()
            ),

        BooleanVar(
            'zip_safe',
            title='Zip-Safe?',
            description='Can this project be used as a zipped egg? (true/false)',
            default=False,
            modes=(),
            page='Metadata',
            help="""
Some eggs can be used directly by Python in zipped format; others must
be unzipped so that their contents can be properly used. Zipped eggs
are smaller and may be easier to redistribute.

Most Zope/Plone projects cannot be used in zipped format; if unsure,
the safest answer is False.
            """
            ),
        ]

    def check_vars(self, vars, command):
        if not command.options.no_interactive and \
           not hasattr(command, '_deleted_once'):
            del vars['package']
            command._deleted_once = True
        return super(BasicNamespace, self).check_vars(vars, command)
