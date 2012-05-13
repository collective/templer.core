import sys
import pkg_resources
from cStringIO import StringIO
from textwrap import TextWrapper

from paste.script.command import get_commands

from templer.core.base import wrap_help_paras
from templer.core.ui import list_sorted_templates

USAGE = """
Usage:

    templer <template> <output-name> [var1=value] ... [varN=value]

    templer --help                Full help
    templer --list                List template verbosely, with details
    templer --make-config-file    Output .zopeskel prefs file
    templer --version             Print installed version

%s
Warning:  use of the --svn-repository argument is not allowed with this script

For further help information, please invoke this script with the
option "--help".
"""

DESCRIPTION = """
This script allows you to create basic skeletons for plone and zope
products and buildouts based on best-practice templates.

It is a wrapper around PasteScript ("paster"), providing an easier
syntax for invoking and better help.


Invoking this script
--------------------

Basic usage::

    templer <template>

(To get a list of the templates, run the script without any arguments;
for a verbose list with full descriptions, run ``templer --list``)

For example::

    templer archetype

To create an Archetypes-based product for Plone. This will prompt you
for the name of your product, and for other information about it.

If you to specify your output name (resulting product, egg, or buildout,
depending on the template being used), you can also do so::

    templer <template> <output-name>

For example::

    templer archetype Products.Example

In addition, you can pass variables to this that would be requested
by that template, and these will then be used. This is an advanced
feature mostly useful for scripted use of this::

    templer archetype Products.Example author_email=joel@joelburton.com

(You can specify as many of these as you want, in name=value pairs.
To get the list of variables that a template expects, you can ask for
this with ``paster create -t <template-name> --list-variables``).


Interactive Help
----------------

While being prompted on each question, you can enter with a single
question mark to receive interactive help for that question.

For example::

  Description (One-line description of the project) ['']: ?

  |  This should be a single-line description of your project. It will
  |  be used in the egg's setup.py, and, for Zope/Plone projects, may be
  |  used in the GenericSetup profile description.


Providing defaults
------------------

It is also possible to set up default values to be used for any template by
creating a file called ``.zopeskel`` in your home directory. This file
should be in INI format.

For example, our ``$HOME/.zopeskel`` could contain::

    [DEFAULT]
    author_email = joel@joelburton.com
    license_name = GPL
    master_keywords = my common keywords here

    [plone3_theme]
    empty_styles = False
    license_name = BSD
    keywords = %(master_keywords)s additional keywords

You can generate a starter .zopeskel file by running this script with
the --make-config-file option. This output can be redirected into
your ``.zopeskel`` file::

    templer --make-config-file > /path/to/home/.zopeskel

Notes:

1) "empty_styles" applies only to themes; we can make this setting
   in the template-specific section of this file. This setting will
   not be used for other templates.

2) For a common setting, like our email address, we can set this in
   a section called DEFAULT; settings made in this section are used
   for all templates.

3) We can make a setting in DEFAULT and then override it for a
   particular template. In this example, we might generally prefer the GPL,
   but issue our themes under the BSD license.

4) You can refer to variables from the same section or from the
   DEFAULT section using Python string formatting. In this example,
   we have a common set of keywords set in DEFAULT and extend it
   for the theming template by referring to the master list.


Differences from the 'paster create' command
--------------------------------------------

1) The --svn-repository argument that can be provided to 'paster create' is
   not allowed when using the templer script.  It will raise an error.  The
   reasons for this are discussed at length in the zopeskel mailing list and
   in the zopeskel issue tracker:
   http://plone.org/products/zopeskel/issues/34
   http://plone.org/products/zopeskel/issues/35

   If this argument is desired, the user should revert to calling 'paster
   create' directly.  However, be warned that buildout templates will not work
   with the argument due to assumptions in the base paster code.


Questions
---------

If you have further questions about the usage of bin/templer, please feel
free to post your questions to the zopeskel mailing list or jump onto the
plone IRC channel (#plone) at irc.freenode.net.


To see the templates supported, run this script without any options.
For a verbose listing with help, use ``templer --list``.
"""

DOT_HELP = {
  0: """
This template expects a project name with no dots in it (a simple
Python package name, like 'foo').
""",
  1: """
This template expects a project name with 1 dot in it (a 'basic
namespace', like 'foo.bar').
""",
  2: """
This template expects a project name with 2 dots in it (a 'nested
namespace', like 'foo.bar.baz').
"""}


def checkdots(template, name):
    """Check if project name appears legal, given template requirements.

    Templates can provide number of namespaces they expect (provided
    in 'ndots' attributes for number-of-dots in name). This checks that
    provided project name is has correct number of namespaces and that
    each part is a legal Python identifier.
    """
    msg = "Not a valid Python dotted name: %s ('%s' is not an identifier)"
    ndots = getattr(template, 'ndots', None)
    if ndots is None:
        return   # No validation possible

    cdots = name.count(".")
    if ndots != cdots:
        raise ValueError(
            "Project name expected %i dots, supplied '%s' has %i dots" % (
                ndots, name, cdots))
    for part in name.split("."):
        # Check if Python identifier,
        # http://code.activestate.com/recipes/413487/
        try:
            class test(object): __slots__ = [part]
        except TypeError:
            raise ValueError(msg % (name, part))


def usage():
    templates = list_printable_templates()
    print USAGE % templates


def show_help():
    print DESCRIPTION


def show_version():
    # XXX: this always returns the version of templer core, even when
    # called from zopeskel.  We should fix that.
    try:
        dist = pkg_resources.get_distribution('templer.core')
        print dist.version
    except pkg_resources.DistributionNotFound:
        print 'unable to identify zopeskel version'


def list_verbose():
    """List templates verbosely, with full help."""
    textwrapper = TextWrapper(
            initial_indent="   ", subsequent_indent="   ")
    cats = list_sorted_templates()

    for title, items in cats.items():
        print "\n"+ title
        print "-" * len(title)
        for temp in items:
            print "\n%s: %s\n" % (temp['name'], temp['summary'])
            if temp['help']:
                wrap_help_paras(textwrapper, temp['help'])
    print


def list_printable_templates():
    """
    Printable list of all templates, sorted into two categories.
    """

    s = StringIO()

    cats = list_sorted_templates()
    templates = sum(cats.values(), [])   # flatten into single list
    max_name = max([len(x['name']) for x in templates])

    for title, items in cats.items():
        print >>s, "\n%s\n" % title
        for entry in items:
            print >>s, "|  %s:%s %s\n" % (
                 entry['name'],
                ' '*(max_name-len(entry['name'])),
                entry['summary']),

    s.seek(0)
    return s.read()


def generate_dotzopeskel():
    """Make an example .zopeskel file for user."""

    cats = list_sorted_templates()
    print """

# This file can contain preferences for zopeskel.
# To do so, uncomment the lines that look like:
#    variable_name = Default Value

[DEFAULT]
"""
    for temp in sum(cats.values(), []):
        print "\n[%(name)s]\n" % temp
        tempc = temp['entry'].load()
        for var in tempc.vars:
            if hasattr(var, 'pretty_description'):
                print "# %s" % var.pretty_description()
            print "# %s = %s\n" % (var.name, var.default)


def process_args():
    """ return a tuple of template_name, output_name and everything else

        everything else will be returned as a dictionary of key/value pairs
    """
    args = sys.argv[1:]
    try:
        template_name = args.pop(0)
    except IndexError:
        raise SyntaxError('No template name provided')
    output_name = None
    others = {}
    for arg in args:
        eq_index = arg.find('=')
        if eq_index == -1 and not output_name:
            output_name = arg
        elif eq_index > 0:
            key, val = arg.split('=')
            # the --svn-repository argument to paster does some things that
            # cause it to be pretty much incompatible with zopeskel. See the
            # following zopeskel issues:
            #     http://plone.org/products/zopeskel/issues/35
            #     http://plone.org/products/zopeskel/issues/34
            # For this reason, we are going to disallow using the
            # --svn-repository argument when using the zopeskel wrapper.
            #
            # Those who wish to use it can still do so by going back to paster,
            # with the caveat that there are some templates (particularly the
            # buildout ones) for which the argument will always throw errors
            # (at least until the problems are fixed upstream in paster
            # itself).
            if 'svn-repository' in key:
                msg = 'for a number of reasons, the --svn-repository argument '
                msg += 'is not allowed with the zopeskel script. '
                msg += "Try --help for more information"
                raise SyntaxError(msg)
            others[key] = val
        else:
            raise SyntaxError(arg)

    return template_name, output_name, others


def run():
    """ """

    if "--help" in sys.argv:
        show_help()
        sys.exit(0)

    if "--make-config-file" in sys.argv:
        generate_dotzopeskel()
        sys.exit(0)

    if "--list" in sys.argv:
        list_verbose()
        sys.exit(0)

    if "--version" in sys.argv:
        show_version()
        sys.exit(0)

    if len(sys.argv) == 1:
        usage()
        sys.exit(0)

    try:
        template_name, output_name, opts = process_args()
    except SyntaxError, e:
        usage()
        print "ERROR: There was a problem with your arguments: %s\n" % str(e)
        sys.exit(1)

    rez = pkg_resources.iter_entry_points(
            'paste.paster_create_template',
            template_name)
    rez = list(rez)
    if not rez:
        usage()
        print "ERROR: No such template: %s\n" % template_name
        sys.exit(1)

    template = rez[0].load()

    print "\n%s: %s" % (template_name, template.summary)
    help = getattr(template, 'help', None)
    if help:
        print template.help

    create = get_commands()['create'].load()

    command = create('create')

    if output_name:
        try:
            checkdots(template, output_name)
        except ValueError, e:
            print "ERROR: %s\n" % str(e)
            sys.exit(1)

    else:
        ndots = getattr(template, 'ndots', None)
        help = DOT_HELP.get(ndots)

        while True:
            if help:
                print help
            try:
                challenge = "Enter project name (or q to quit)"
                output_name = command.challenge(challenge)
                if output_name == 'q':
                    print "\n\nExiting...\n"
                    sys.exit(0)
                checkdots(template, output_name)
            except ValueError, e:
                print "\nERROR: %s" % e
            else:
                break


    print """
If at any point, you need additional help for a question, you can enter
'?' and press RETURN.
"""

    optslist = ['%s=%s' % (k, v) for k, v in opts.items()]
    if output_name is not None:
        optslist.insert(0, output_name)
    try:
        command.run(['-q', '-t', template_name] + optslist)
    except KeyboardInterrupt:
        print "\n\nExiting...\n"
    except Exception, e:
        print "\nERROR: %s\n" % str(e)
        sys.exit(1)
    sys.exit(0)
