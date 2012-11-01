import os
import copy

from paste.script import templates
from templer.core.base import BaseTemplate
from templer.core.base import get_var
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


class PackageTemplate(BaseTemplate):
    _outer_template_dir = 'templates/outer'
    _inner_template_dir = 'templates/inner'
    summary = "A Python package template for templer"
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
            'egg',
            title='Package',
            description='Package name (for namespace support use dots.)',
            default='',
            modes=(EASY, ),
            page='Namespaces',
            help="""
Choose the name of your package.

If you want to use dots in the package name (namespaces), just provide them
directly in the name. For example: my.package.
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

    def pre(self, command, output_dir, vars):
        """The namespace string for insertion into setup.py needs to
           be calculated, and inserted into the vars for use in
           setup.py_tmpl.
        """
        if '.' in vars['egg']:
            # Taken from http://code.google.com/p/wsgitemplates/
            namespace = []
            for i in range(len(vars['egg'].split('.')) - 1):
                namespace.append(".".join(vars['egg'].split('.')[0:i+1]))
            vars['namespace'] = "\n      namespace_packages=%s," % namespace
        else:
            vars['namespace'] = ""

        super(PackageTemplate, self).pre(command, output_dir, vars)

    def post(self, command, output_dir, vars):
        cwd = os.getcwd()
        os.chdir(vars['egg'])
        os.chdir('src')
        for i in range(len(vars['egg'].split('.'))):
            segs = vars['egg'].split('.')[0:i+1]
            try:
                os.mkdir(os.path.join(*vars['egg'].split('.')[0:i+1]))
            except OSError:
                pass
            segs.append("__init__.py")
            init = None
            if i != len(vars['egg'].split('.'))-1:
                init = open(os.path.join(*segs), "w")
                bit = "__import__('pkg_resources').declare_namespace(__name__)"
                init.write(bit)
            if not init is None:
                init.close()
        os.chdir(cwd)
        super(PackageTemplate, self).post(command, output_dir, vars)

    def run(self, command, output_dir, vars):
        self._template_dir = self._outer_template_dir
        templates.Template.run(self, command, output_dir, vars)
        output_dir = os.path.join(
            *([vars['egg'], 'src'] + vars['egg'].split('.')))

        self._template_dir = self._inner_template_dir
        _old_required_structures=self.required_structures
        self.required_structures=[]
        templates.Template.run(self, command, output_dir, vars)
        self.required_structures = _old_required_structures

    def check_vars(self, vars, command):
        if not command.options.no_interactive and \
           not hasattr(command, '_deleted_once'):
            del vars['package']
            command._deleted_once = True
        return super(PackageTemplate, self).check_vars(vars, command)
