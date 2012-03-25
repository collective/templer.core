import os
import pkg_resources
from copy import copy

from textwrap import TextWrapper
import ConfigParser
from ConfigParser import SafeConfigParser
from paste.script import command
from paste.script import pluginlib
from paste.script import templates

from templer.core.vars import StringChoiceVar
from templer.core.vars import ALL
from templer.core.vars import ValidationException


LICENSE_CATEGORIES = {
    'ASL': 'License :: OSI Approved :: Apache Software License',
    'BSD': 'License :: OSI Approved :: BSD License',
    'EFL': 'License :: Eiffel Forum License (EFL)',
    'FDL': 'License :: OSI Approved :: GNU Free Documentation License (FDL)',
    'GPL': 'License :: OSI Approved :: GNU General Public License (GPL) v2',
    'GPL3': 'License :: OSI Approved :: GNU General Public License (GPL) v3',
    'LGPL': 'License :: OSI Approved :: GNU Library or Lesser General Public License (LGPL)',
    'MIT': 'License :: OSI Approved :: MIT License',
    'MPL': 'License :: OSI Approved :: Mozilla Public License 1.0 (MPL)',
    'MPL11': 'License :: OSI Approved :: Mozilla Public License 1.1 (MPL 1.1)',
    'NPL': 'License :: Netscape Public License 1.1 (NPL)',
    'ZPL': 'License :: OSI Approved :: Zope Public License',
    }


def wrap_help_paras(wrapper, text):
    """Given a string containing embedded paras, output wrapped"""

    for idx, para in enumerate(text.split("\n\n")):
        if idx:
            print
        print wrapper.fill(para)


def get_zopeskel_prefs():
    # http://snipplr.com/view/7354/get-home-directory-path--in-python-win-lin-other/
    try:
        from win32com.shell import shellcon, shell
        homedir = shell.SHGetFolderPath(0, shellcon.CSIDL_APPDATA, 0, 0)
    except ImportError:
        # quick semi-nasty fallback for non-windows/win32com case
        homedir = os.path.expanduser("~")

    # Get defaults from .zopeskel
    config = SafeConfigParser()
    config.read('%s/.zopeskel' % homedir)
    return config


def get_var(vars, name):
    for var in vars:
        if var.name == name:
            return var
    else:
        raise ValueError("No such var: %r" % name)


def update_setup_cfg(path, section, option, value):

    parser = ConfigParser.ConfigParser()
    if os.path.exists(path):
        parser.read(path)

    if not parser.has_section(section):
        parser.add_section(section)

    parser.set(section, option, value)
    parser.write(open(path, 'w'))


class BaseTemplate(templates.Template):
    """Base template for all ZopeSkel templates"""

    #a zopeskel template has to set this to True if it wants to use
    #localcommand
    use_local_commands = False
    null_value_marker = []
    pre_run_msg = None
    post_run_msg = None
    default_required_structures = []

    def __init__(self, name):
        super(BaseTemplate, self).__init__(name)
        self.required_structures = copy(self.default_required_structures)

    vars = [
        StringChoiceVar(
            'expert_mode',
            title='Expert Mode?',
            description='What question mode would you like? (easy/expert/all)?',
            page='Begin',
            default='easy',
            choices=('easy', 'expert', 'all'),
            help="""
In easy mode, you will be asked fewer, more common questions.

In expert mode, you will be asked to answer more advanced,
technical questions.

In all mode, no questions will be skipped--even things like
author_email, which would normally be a default set in a
$HOME/.zopeskel file.
"""),
    ]

    #this is just to be able to add ZopeSkel to the list of paster_plugins if
    #the use_local_commands is set to true and to write a zopeskel section in
    #setup.cfg file containing the name of the parent template.
    #it will be used by addcontent command to list the apropriate subtemplates
    #for the generated project. the post method is not a candidate because
    #many templates override it
    def run(self, command, output_dir, vars):
        # XXX: The goal here is to only do this if templer.localcommands has
        #      been installed.  If it isn't the user doesn't want local
        #      commands and we should not inject them (it would fail anyway)
        if self.use_local_commands and\
            'templer.localcommands' not in self.egg_plugins:
            self.egg_plugins.append('templer.localcommands')

        templates.Template.run(self, command, output_dir, vars)

        # can we make the inclusion of this provisional, based on 
        # whether the localcommands package is loaded?
        setup_cfg = os.path.join(output_dir, 'setup.cfg')
        if self.use_local_commands:
            update_setup_cfg(setup_cfg, 'templer.local', 'template', self.name)

    def print_subtemplate_notice(self, output_dir=None):
            """Print a notice about local commands being available (if this is
            indeed the case).

            Unfortunately for us, at this stage in the process, the
            egg_info directory has not yet been created (and won't be
            within the scope of this template running [see
            paste.script.create_distro.py]), so we cannot show which
            subtemplates are available.
            
            ^^^ this appears not to be completely true.  The point where
                this method is run we are in a template which has subcommands
                and so I believe that it might actually be possible to print
                a list of those subtemplates which belong to me, since 
                self.name is the same as the template name used in 
                command._list_sub_templates
            """
            plugins = pluginlib.resolve_plugins(['templer.localcommands'])
            commands = pluginlib.load_commands_from_plugins(plugins)
            if not commands:
                return
            commands = commands.items()
            commands.sort()
            longest = max([len(n) for n, c in commands])
            print_commands = []
            for name, this_command in commands:
                name = name + ' ' * (longest - len(name))
                print_commands.append('  %s  %s' %
                                        (name, this_command.load().summary))
            print_commands = '\n'.join(print_commands)
            print '-' * 78
            print """\
The project you just created has local commands. These can be used from within
the product.

usage: paster COMMAND

Commands:
%s

For more information: paster help COMMAND""" % print_commands
            print '-' * 78

    def print_zopeskel_message(self, msg_name):
        """ print a message stored as an attribute of the template
        """
        msg = getattr(self, msg_name, None)
        if msg:
            textwrapper = TextWrapper(
                    initial_indent="**  ",
                    subsequent_indent="**  ",
                    )
            print "\n" + '*'*74
            wrap_help_paras(textwrapper, msg)
            print '*'*74 + "\n"

    def readable_license_options(self):
        output = ["The following licenses are available:\n", ]
        for key, classifier in LICENSE_CATEGORIES.items():
            output.append("%s --\n %s\n" % (key, classifier))
        return "\n".join(output)

    def all_structure_entry_points(self):
        if not hasattr(self, '_structure_entry_points'):
            self._structure_entry_points = list(
                pkg_resources.iter_entry_points('templer.templer_structure'))
        return self._structure_entry_points

    def load_structure(self, name):
        for ep in self.all_structure_entry_points():
            if ep.name == name:
                return ep.load()
        raise LookupError('No entry point for structure %s available' % name)

    def get_structures(self, vars):
        my_structures = []
        # TODO: protect users against errors raised by load_structure
        for structure in self.required_structures:
            my_structures.append(self.load_structure(structure))
        return my_structures

    def write_structures(self, command, output_dir, vars):
        structures = self.get_structures(vars)
        for structure in structures:
            structure().write_files(command, output_dir, vars)

    def pre(self, *args, **kwargs):
        templates.Template.pre(self, *args, **kwargs)

    def write_files(self, command, output_dir, vars):
        """ override base write_files to inject structural (non-template)
            directories
        """
        self.write_structures(command, output_dir, vars)
        super(BaseTemplate, self).write_files(command, output_dir, vars)

    def post(self, command, output_dir, vars):
        if self.should_print_subcommands(command):
            self.print_subtemplate_notice()
        templates.Template.post(self, command, output_dir, vars)
        # at the very end of it all, print the post_run_msg so we can
        # inform users of important information.
        self.print_zopeskel_message('post_run_msg')

    def get_template_stack(self, command):
        """ return a list of the template objects to be run in this command
        """
        asked_tmpls = command.options.templates or ['basic_package']
        templates = []
        for tmpl_name in asked_tmpls:
            command.extend_templates(templates, tmpl_name)
        return [tmpl_obj for tmpl_name, tmpl_obj in templates]

    def get_position_in_stack(self, stack):
        """ return the index of the current template in the stack
        """
        class_stack = [t.__class__ for t in stack]

        return class_stack.index(self.__class__)

    def should_print_subcommands(self, command):
        """ return true or false

            if this template has subcommands _and_ is the last template
            to be run through that does, go ahead and return true, otherwise
            return false
        """
        if not getattr(self, 'use_local_commands', False):
            return False
        # we have local commands for this template, is it the last one for
        # which this is true?
        stack = self.get_template_stack(command)
        index = self.get_position_in_stack(stack)
        remaining_stack = stack[index+1:]
        have_subcommands_left = [getattr(t, 'use_local_commands', False)
                                 for t in remaining_stack]
        if True in have_subcommands_left:
            return False

        return True

    def _filter_for_modes(self, mode, expected_vars):
        """Filter questions down according to our mode.

        ALL = show all questions
        EASY, EXPERT = show just those
        """

        if mode == ALL:
            return {}

        hidden = {}

        for var in expected_vars:
            # if in expert mode, hide vars not for expert mode
            if  mode not in var.modes:
                hidden[var.name] = var.default

        return hidden

    def override_package_names_defaults(self, vars, expect_vars):
        """Override package names defaults using project title.

        Override the default for namespace_package, namespace_package2,
        and package from splitting the project title--if ndots is
        specified by this template.

        This is helpful for new users, who find it confusing to provide
        a package name like "mycompany.theme.blue" and then have to
        (slightly-redundantly) specify namespace_package=mycompany,
        namespace_package2=theme, package=blue.
        """

        ndots = getattr(self, 'ndots', None)
        if ndots:
            parts = vars['project'].split(".")
            if ndots >= 1 and len(parts) >= 1:
                get_var(expect_vars, 'namespace_package').default = parts[0]
            if ndots >= 2 and len(parts) >= 2:
                get_var(expect_vars, 'namespace_package2').default = parts[1]
            package_name = parts[-1]
            get_var(expect_vars, 'package').default = package_name

    def _set_structure_from_var(self, var, key):
        structures = var.structures[key]
        if not isinstance(structures, (list, tuple, )):
            structures = [structures, ]
        for structure in structures:
            if structure:
                self.required_structures.append(structure)

    def check_vars(self, vars, cmd):
        # if we need to notify users of anything before they start this
        # whole process, we can do it here.
        self.print_zopeskel_message('pre_run_msg')

        # Copied and modified from PasteScript's check_vars--
        # the method there wasn't hookable for the things
        # we need -- question posing, validation, etc.
        #
        # Admittedly, this could be merged into PasteScript,
        # but it was decided it was easier to limit scope of
        # these changes to ZopeSkel, as other projects may
        # use PasteScript in very different ways.

        cmd._deleted_once = 1      # don't re-del package

        textwrapper = TextWrapper(
                initial_indent="|  ",
                subsequent_indent="|  ",
                )

        # now, mostly copied direct from paster
        expect_vars = self.read_vars(cmd)
        if not expect_vars:
            # Assume that variables aren't defined
            return vars
        converted_vars = {}
        errors = []

        config = get_zopeskel_prefs()
        # pastescript allows one to request more than one template (multiple
        # -t options at the command line) so we will get a list of templates
        # from the cmd's options property
        requested_templates = cmd.options.templates
        for var in expect_vars:
            for template in requested_templates:
                if config.has_option(template, var.name):
                    var.default = config.get(template, var.name)
                    break
            else:
                # Not found in template section, now look explicitly
                # in DEFAULT section
                if config.has_option('DEFAULT', var.name):
                    var.default = config.get('DEFAULT', var.name)

        self.override_package_names_defaults(vars, expect_vars)
        unused_vars = vars.copy()

        for var in expect_vars:
            response = self.null_value_marker
            if var.name not in unused_vars:
                if cmd.interactive:
                    prompt = var.pretty_description()
                    while response is self.null_value_marker:
                        response = cmd.challenge(prompt, var.default,
                                                 var.should_echo)
                        if response == '?':
                            help = var.further_help().strip() % converted_vars
                            print
                            wrap_help_paras(textwrapper, help)
                            print
                            response = self.null_value_marker
                        if response is not self.null_value_marker:
                            try:
                                response = var.validate(response)
                            except ValidationException, e:
                                print e
                                response = self.null_value_marker
                elif var.default is command.NoDefault:
                    errors.append('Required variable missing: %s'
                                  % var.full_description())
                else:
                    response = var.validate(var.default)
            else:
                response = var.validate(unused_vars.pop(var.name))

            converted_vars[var.name] = response
            # if a variable has structures associated, we will insert them
            # in the template required_structures property at this time, let's
            # test first to see if we need to do anything.
            if var._is_structural:
                self._set_structure_from_var(var, str(response))

            # filter the vars for mode.
            if var.name == 'expert_mode':
                expert_mode = converted_vars['expert_mode']
                hidden = self._filter_for_modes(expert_mode, expect_vars)
                unused_vars.update(hidden)

        if errors:
            raise command.BadCommand(
                'Errors in variables:\n%s' % '\n'.join(errors))
        converted_vars.update(unused_vars)
        vars.update(converted_vars)

        result = converted_vars

        return result

    @property
    def pages(self):
        pages = []
        page_map = {}
        for question in self.vars:
            name = question.page
            if name in page_map:
                page = page_map[name]
                page['vars'].append(question)
            else:
                page = {'name': name, 'vars': [question]}
                pages.append(page)
                page_map[name] = page
        return pages
