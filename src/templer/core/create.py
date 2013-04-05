# (c) 2005 Ian Bicking and contributors; written for Paste (http://pythonpaste.org)
# Licensed under the MIT license: http://www.opensource.org/licenses/mit-license.php

import ConfigParser
import difflib
import fnmatch
import getpass
import os
import pkg_resources
import re
import subprocess
import sys
import textwrap

from templer.core import bool_optparse
from templer.core import copydir
from templer.core import pluginlib


class BadCommand(Exception):
    def __init__(self, message, exit_code=2):
        self.message = message
        self.exit_code = exit_code
        Exception.__init__(self, message)

    def _get_message(self):
        """Getter for 'message'; needed only to override deprecation
        in BaseException."""
        return self.__message

    def _set_message(self, value):
        """Setter for 'message'; needed only to override deprecation
        in BaseException."""
        self.__message = value

    # BaseException.message has been deprecated since Python 2.6.
    # To prevent DeprecationWarning from popping up over this
    # pre-existing attribute, use a new property that takes lookup
    # precedence.
    message = property(_get_message, _set_message)


class NoDefault(object):
    pass


class Command(object):
    max_args = None
    max_args_error = 'You must provide no more than %(max_args)s arguments'
    min_args = None
    min_args_error = 'You must provide at least %(min_args)s arguments'
    required_args = None
    # If this command takes a configuration file, set this to 1 or -1
    # Then if invoked through #! the config file will be put into the positional
    # arguments -- at the beginning with 1, at the end with -1
    takes_config_file = None

    # Grouped in help messages by this:
    group_name = ''

    required_args = ()
    description = None
    usage = ''
    hidden = False
    # This is the default verbosity level; --quiet subtracts,
    # --verbose adds:
    default_verbosity = 0
    # This is the default interactive state:
    default_interactive = 0
    return_code = 0

    def run(self, args):
        self.parse_args(args)

        # Setup defaults:
        for name, default in [('verbose', 0),
                              ('quiet', 0),
                              ('interactive', False),
                              ('overwrite', False)]:
            if not hasattr(self.options, name):
                setattr(self.options, name, default)
        if getattr(self.options, 'simulate', False):
            self.options.verbose = max(self.options.verbose, 1)
        self.interactive = self.default_interactive
        if getattr(self.options, 'interactive', False):
            self.interactive += self.options.interactive
        if getattr(self.options, 'no_interactive', False):
            self.interactive = False
        self.verbose = self.default_verbosity
        self.verbose += self.options.verbose
        self.verbose -= self.options.quiet
        self.simulate = getattr(self.options, 'simulate', False)

        # For #! situations:
        if (os.environ.get('PASTE_CONFIG_FILE')
                and self.takes_config_file is not None):
            take = self.takes_config_file
            filename = os.environ.get('PASTE_CONFIG_FILE')
            if take == 1:
                self.args.insert(0, filename)
            elif take == -1:
                self.args.append(filename)
            else:
                assert 0, (
                    "Value takes_config_file must be None, 1, or -1 (not %r)"
                    % take)

        if (os.environ.get('PASTE_DEFAULT_QUIET')):
            self.verbose = 0

        # Validate:
        if self.min_args is not None and len(self.args) < self.min_args:
            raise BadCommand(
                self.min_args_error % {'min_args': self.min_args,
                                       'actual_args': len(self.args)})
        if self.max_args is not None and len(self.args) > self.max_args:
            raise BadCommand(
                self.max_args_error % {'max_args': self.max_args,
                                       'actual_args': len(self.args)})
        for var_name, option_name in self.required_args:
            if not getattr(self.options, var_name, None):
                raise BadCommand(
                    'You must provide the option %s' % option_name)
        result = self.command()
        if result is None:
            return self.return_code
        else:
            return result

    def parse_args(self, args):
        if self.usage:
            usage = ' ' + self.usage
        else:
            usage = ''
        self.parser.usage = "%%prog [options]%s\n%s" % (
            usage, self.summary)
        self.parser.prog = self._prog_name()
        if self.description:
            desc = self.description
            desc = textwrap.dedent(desc)
            self.parser.description = desc
        self.options, self.args = self.parser.parse_args(args)

    def _prog_name(self):
        return '%s %s' % (os.path.basename(sys.argv[0]), self.command_name)

    ########################################
    ## Utility methods
    ########################################

    def here(cls):
        mod = sys.modules[cls.__module__]
        return os.path.dirname(mod.__file__)

    here = classmethod(here)

    def ask(self, prompt, safe=False, default=True):
        """
        Prompt the user.  Default can be true, false, ``'careful'`` or
        ``'none'``.  If ``'none'`` then the user must enter y/n.  If
        ``'careful'`` then the user must enter yes/no (long form).

        If the interactive option is over two (``-ii``) then ``safe``
        will be used as a default.  This option should be the
        do-nothing option.
        """
        # @@: Should careful be a separate argument?

        if self.options.interactive >= 2:
            default = safe
        if default == 'careful':
            prompt += ' [yes/no]?'
        elif default == 'none':
            prompt += ' [y/n]?'
        elif default:
            prompt += ' [Y/n]? '
        else:
            prompt += ' [y/N]? '
        while 1:
            response = raw_input(prompt).strip().lower()
            if not response:
                if default in ('careful', 'none'):
                    print 'Please enter yes or no'
                    continue
                return default
            if default == 'careful':
                if response in ('yes', 'no'):
                    return response == 'yes'
                print 'Please enter "yes" or "no"'
                continue
            if response[0].lower() in ('y', 'n'):
                return response[0].lower() == 'y'
            print 'Y or N please'

    def challenge(self, prompt, default=NoDefault, should_echo=True):
        """
        Prompt the user for a variable.
        """
        if default is not NoDefault:
            prompt += ' [%r]' % default
        prompt += ': '
        while 1:
            if should_echo:
                prompt_method = raw_input
            else:
                prompt_method = getpass.getpass
            response = prompt_method(prompt).strip()
            if not response:
                if default is not NoDefault:
                    return default
                else:
                    continue
            else:
                return response

    def pad(self, s, length, dir='left'):
        if len(s) >= length:
            return s
        if dir == 'left':
            return s + ' ' * (length - len(s))
        else:
            return ' ' * (length - len(s)) + s

    def standard_parser(cls, verbose=True,
                        interactive=False,
                        no_interactive=False,
                        simulate=False,
                        quiet=False,
                        overwrite=False):
        """
        Create a standard ``OptionParser`` instance.

        Typically used like::

            class MyCommand(Command):
                parser = Command.standard_parser()

        Subclasses may redefine ``standard_parser``, so use the
        nearest superclass's class method.
        """
        parser = bool_optparse.BoolOptionParser()
        if verbose:
            parser.add_option('-v', '--verbose',
                              action='count',
                              dest='verbose',
                              default=0)
        if quiet:
            parser.add_option('-q', '--quiet',
                              action='count',
                              dest='quiet',
                              default=0)
        if no_interactive:
            parser.add_option('--no-interactive',
                              action="count",
                              dest="no_interactive",
                              default=0)
        if interactive:
            parser.add_option('-i', '--interactive',
                              action='count',
                              dest='interactive',
                              default=0)
        if simulate:
            parser.add_option('-n', '--simulate',
                              action='store_true',
                              dest='simulate',
                              default=False)
        if overwrite:
            parser.add_option('-f', '--overwrite',
                              dest="overwrite",
                              action="store_true",
                              help="Overwrite files (warnings will be emitted for non-matching files otherwise)")
        return parser

    standard_parser = classmethod(standard_parser)

    def shorten(self, fn, *paths):
        """
        Return a shorted form of the filename (relative to the current
        directory), typically for displaying in messages.  If
        ``*paths`` are present, then use os.path.join to create the
        full filename before shortening.
        """
        if paths:
            fn = os.path.join(fn, *paths)
        if fn.startswith(os.getcwd()):
            return fn[len(os.getcwd()):].lstrip(os.path.sep)
        else:
            return fn

    def ensure_dir(self, dir):
        """
        Ensure that the directory exists, creating it if necessary.
        Respects verbosity and simulation.
        """
        dir = dir.rstrip(os.sep)
        if not dir:
            # we either reached the parent-most directory, or we got
            # a relative directory
            # @@: Should we make sure we resolve relative directories
            # first?  Though presumably the current directory always
            # exists.
            return
        if not os.path.exists(dir):
            self.ensure_dir(os.path.dirname(dir))
            if self.verbose:
                print 'Creating %s' % self.shorten(dir)
            if not self.simulate:
                os.mkdir(dir)
        else:
            if self.verbose > 1:
                print "Directory already exists: %s" % self.shorten(dir)

    def ensure_file(self, filename, content):
        """
        Ensure a file named ``filename`` exists with the given
        content.  If ``--interactive`` has been enabled, this will ask
        the user what to do if a file exists with different content.
        """
        assert content is not None, (
            "You cannot pass a content of None")
        self.ensure_dir(os.path.dirname(filename))
        if not os.path.exists(filename):
            if self.verbose:
                print 'Creating %s' % filename
            if not self.simulate:
                f = open(filename, 'wb')
                f.write(content)
                f.close()
            return
        f = open(filename, 'rb')
        old_content = f.read()
        f.close()
        if content == old_content:
            if self.verbose > 1:
                print 'File %s matches expected content' % filename
            return
        if not self.options.overwrite:
            print 'Warning: file %s does not match expected content' % filename
            diff = difflib.context_diff(
                content.splitlines(),
                old_content.splitlines(),
                'expected ' + filename,
                filename)
            print '\n'.join(diff)
            if self.interactive:
                while 1:
                    s = raw_input(
                        'Overwrite file with new content? [y/N] ').strip().lower()
                    if not s:
                        s = 'n'
                    if s.startswith('y'):
                        break
                    if s.startswith('n'):
                        return
                    print 'Unknown response; Y or N please'
            else:
                return

        if self.verbose:
            print 'Overwriting %s with new content' % filename
        if not self.simulate:
            f = open(filename, 'wb')
            f.write(content)
            f.close()

    def insert_into_file(self, filename, marker_name, text,
                         indent=False):
        """
        Inserts ``text`` into the file, right after the given marker.
        Markers look like: ``-*- <marker_name>[:]? -*-``, and the text
        will go on the immediately following line.

        Raises ``ValueError`` if the marker is not found.

        If ``indent`` is true, then the text will be indented at the
        same level as the marker.
        """
        if not text.endswith('\n'):
            raise ValueError(
                "The text must end with a newline: %r" % text)
        if not os.path.exists(filename) and self.simulate:
            # If we are doing a simulation, it's expected that some
            # files won't exist...
            if self.verbose:
                print 'Would (if not simulating) insert text into %s' % (
                    self.shorten(filename))
            return

        f = open(filename)
        lines = f.readlines()
        f.close()
        regex = re.compile(r'-\*-\s+%s:?\s+-\*-' % re.escape(marker_name),
                           re.I)
        for i in range(len(lines)):
            if regex.search(lines[i]):
                # Found it!
                if (lines[i:] and len(lines[i:]) > 1 and
                    ''.join(lines[i + 1:]).strip().startswith(text.strip())):
                    # Already have it!
                    print 'Warning: line already found in %s (not inserting' % filename
                    print '  %s' % lines[i]
                    return

                if indent:
                    text = text.lstrip()
                    match = re.search(r'^[ \t]*', lines[i])
                    text = match.group(0) + text
                lines[i + 1:i + 1] = [text]
                break
        else:
            errstr = (
                "Marker '-*- %s -*-' not found in %s"
                % (marker_name, filename))
            if 1 or self.simulate:  # @@: being permissive right now
                print 'Warning: %s' % errstr
            else:
                raise ValueError(errstr)
        if self.verbose:
            print 'Updating %s' % self.shorten(filename)
        if not self.simulate:
            f = open(filename, 'w')
            f.write(''.join(lines))
            f.close()

    def run_command(self, cmd, *args, **kw):
        """
        Runs the command, respecting verbosity and simulation.
        Returns stdout, or None if simulating.

        Keyword arguments:

        cwd:
            the current working directory to run the command in
        capture_stderr:
            if true, then both stdout and stderr will be returned
        expect_returncode:
            if true, then don't fail if the return code is not 0
        force_no_simulate:
            if true, run the command even if --simulate
        """
        if subprocess is None:
            raise RuntimeError('Environment does not support subprocess '
                               'module, cannot run command.')
        cmd = self.quote_first_command_arg(cmd)
        cwd = kw.pop('cwd', os.getcwd())
        capture_stderr = kw.pop('capture_stderr', False)
        expect_returncode = kw.pop('expect_returncode', False)
        force = kw.pop('force_no_simulate', False)
        warn_returncode = kw.pop('warn_returncode', False)
        if warn_returncode:
            expect_returncode = True
        simulate = self.simulate
        if force:
            simulate = False
        assert not kw, ("Arguments not expected: %s" % kw)
        if capture_stderr:
            stderr_pipe = subprocess.STDOUT
        else:
            stderr_pipe = subprocess.PIPE
        try:
            proc = subprocess.Popen([cmd] + list(args),
                                    cwd=cwd,
                                    stderr=stderr_pipe,
                                    stdout=subprocess.PIPE)
        except OSError, e:
            if e.errno != 2:
                # File not found
                raise
            raise OSError(
                "The expected executable %s was not found (%s)"
                % (cmd, e))
        if self.verbose:
            print 'Running %s %s' % (cmd, ' '.join(args))
        if simulate:
            return None
        stdout, stderr = proc.communicate()
        if proc.returncode and not expect_returncode:
            if not self.verbose:
                print 'Running %s %s' % (cmd, ' '.join(args))
            print 'Error (exit code: %s)' % proc.returncode
            if stderr:
                print stderr
            raise OSError("Error executing command %s" % cmd)
        if self.verbose > 2:
            if stderr:
                print 'Command error output:'
                print stderr
            if stdout:
                print 'Command output:'
                print stdout
        elif proc.returncode and warn_returncode:
            print 'Warning: command failed (%s %s)' % (cmd, ' '.join(args))
            print 'Exited with code %s' % proc.returncode
        return stdout

    def quote_first_command_arg(self, arg):
        """
        There's a bug in Windows when running an executable that's
        located inside a path with a space in it.  This method handles
        that case, or on non-Windows systems or an executable with no
        spaces, it just leaves well enough alone.
        """
        if (sys.platform != 'win32'
                or ' ' not in arg):
            # Problem does not apply:
            return arg
        try:
            import win32api
        except ImportError:
            raise ValueError(
                "The executable %r contains a space, and in order to "
                "handle this issue you must have the win32api module "
                "installed" % arg)
        arg = win32api.GetShortPathName(arg)
        return arg

    def write_file(self, filename, content, source=None,
                   binary=True):
        """
        Like ``ensure_file``, but without the interactivity.  Mostly
        deprecated.  (I think I forgot it existed)
        """
        import warnings
        warnings.warn(
            "command.write_file has been replaced with "
            "command.ensure_file",
            DeprecationWarning, 2)
        if os.path.exists(filename):
            if binary:
                f = open(filename, 'rb')
            else:
                f = open(filename, 'r')
            old_content = f.read()
            f.close()
            if content == old_content:
                if self.verbose:
                    print 'File %s exists with same content' % (
                        self.shorten(filename))
                return
            if (not self.simulate and self.options.interactive):
                if not self.ask('Overwrite file %s?' % filename):
                    return
        if self.verbose > 1 and source:
            print 'Writing %s from %s' % (self.shorten(filename),
                                          self.shorten(source))
        elif self.verbose:
            print 'Writing %s' % self.shorten(filename)
        if not self.simulate:
            already_existed = os.path.exists(filename)
            if binary:
                f = open(filename, 'wb')
            else:
                f = open(filename, 'w')
            f.write(content)
            f.close()

    def parse_vars(self, args):
        """
        Given variables like ``['a=b', 'c=d']`` turns it into ``{'a':
        'b', 'c': 'd'}``
        """
        result = {}
        for arg in args:
            if '=' not in arg:
                raise BadCommand(
                    'Variable assignment %r invalid (no "=")'
                    % arg)
            name, value = arg.split('=', 1)
            result[name] = value
        return result

    def read_vars(self, config, section='pastescript'):
        """
        Given a configuration filename, this will return a map of values.
        """
        result = {}
        p = ConfigParser.RawConfigParser()
        p.read([config])
        if p.has_section(section):
            for key, value in p.items(section):
                if key.endswith('__eval__'):
                    result[key[:-len('__eval__')]] = eval(value)
                else:
                    result[key] = value
        return result

    def write_vars(self, config, vars, section='pastescript'):
        """
        Given a configuration filename, this will add items in the
        vars mapping to the configuration file.  Will create the
        configuration file if it doesn't exist.
        """
        modified = False

        p = ConfigParser.RawConfigParser()
        if not os.path.exists(config):
            f = open(config, 'w')
            f.write('')
            f.close()
            modified = True
        p.read([config])
        if not p.has_section(section):
            p.add_section(section)
            modified = True

        existing_options = p.options(section)
        for key, value in vars.items():
            if (key not in existing_options and
                    '%s__eval__' % key not in existing_options):
                if not isinstance(value, str):
                    p.set(section, '%s__eval__' % key, repr(value))
                else:
                    p.set(section, key, value)
                modified = True

        if modified:
            p.write(open(config, 'w'))

    def indent_block(self, text, indent=2, initial=None):
        """
        Indent the block of text (each line is indented).  If you give
        ``initial``, then that is used in lieue of ``indent`` for the
        first line.
        """
        if initial is None:
            initial = indent
        lines = text.splitlines()
        first = (' ' * initial) + lines[0]
        rest = [(' ' * indent) + l for l in lines[1:]]
        return '\n'.join([first] + rest)


class CreateDistroCommand(Command):
    usage = 'PACKAGE_NAME [VAR=VALUE VAR2=VALUE2 ...]'
    summary = "Create the file layout for a Python distribution"
    short_description = summary

    description = """\
    Create a new project.  Projects are typically Python packages,
    ready for distribution.  Projects are created from templates, and
    represent different kinds of projects -- associated with a
    particular framework for instance.
    """

    parser = Command.standard_parser(
        simulate=True, no_interactive=True, quiet=True, overwrite=True)
    parser.add_option('-t', '--template',
                      dest='templates',
                      metavar='TEMPLATE',
                      action='append',
                      help="Add a template to the create process")
    parser.add_option('-o', '--output-dir',
                      dest='output_dir',
                      metavar='DIR',
                      default='.',
                      help="Write put the directory into DIR (default current directory)")
    parser.add_option('--list-templates',
                      dest='list_templates',
                      action='store_true',
                      help="List all templates available")
    parser.add_option('--list-variables',
                      dest="list_variables",
                      action="store_true",
                      help="List all variables expected by the given template (does not create a package)")
    parser.add_option('--inspect-files',
                      dest='inspect_files',
                      action='store_true',
                      help="Show where the files in the given (already created) directory came from (useful when using multiple templates)")
    parser.add_option('--config',
                      action='store',
                      dest='config',
                      help="Template variables file")

    _bad_chars_re = re.compile('[^a-zA-Z0-9_]')

    default_verbosity = 1
    default_interactive = 1

    def __init__(self):
        self.command_name = 'create'

    def command(self):
        if self.options.list_templates:
            return self.list_templates()
        asked_tmpls = self.options.templates or ['basic_package']
        templates = []
        for tmpl_name in asked_tmpls:
            self.extend_templates(templates, tmpl_name)
        if self.options.list_variables:
            return self.list_variables(templates)
        if self.verbose:
            print 'Selected and implied templates:'
            max_tmpl_name = max([len(tmpl_name) for tmpl_name, tmpl in templates])
            for tmpl_name, tmpl in templates:
                print '  %s%s  %s' % (
                    tmpl_name, ' '*(max_tmpl_name-len(tmpl_name)),
                    tmpl.summary)
            print
        if not self.args:
            if self.interactive:
                dist_name = self.challenge('Enter project name')
            else:
                raise BadCommand('You must provide a PACKAGE_NAME')
        else:
            dist_name = self.args[0].lstrip(os.path.sep)

        templates = [tmpl for name, tmpl in templates]
        output_dir = os.path.join(self.options.output_dir, dist_name)
 
        pkg_name = self._bad_chars_re.sub('', dist_name.lower())
        vars = {'project': dist_name,
                'package': pkg_name,
                'egg': pluginlib.egg_name(dist_name),
                }
        vars.update(self.parse_vars(self.args[1:]))
        if self.options.config and os.path.exists(self.options.config):
            for key, value in self.read_vars(self.options.config).items():
                vars.setdefault(key, value)

        if self.verbose:  # @@: > 1?
            self.display_vars(vars)

        if self.options.inspect_files:
            self.inspect_files(
                output_dir, templates, vars)
            return
        if not os.path.exists(output_dir):
            # We want to avoid asking questions in copydir if the path
            # doesn't exist yet
            copydir.all_answer = 'y'

        # First we want to make sure all the templates get a chance to
        # set their variables, all at once, with the most specialized
        # template going first (the last template is the most
        # specialized)...
        for template in templates[::-1]:
            vars = template.check_vars(vars, self)

        # Gather all the templates egg_plugins into one var
        egg_plugins = set()
        for template in templates:
            egg_plugins.update(template.egg_plugins)
        egg_plugins = list(egg_plugins)
        egg_plugins.sort()
        vars['egg_plugins'] = egg_plugins

        for template in templates:
            self.create_template(
                template, output_dir, vars)

        package_dir = vars.get('package_dir', None)
        if package_dir:
            output_dir = os.path.join(output_dir, package_dir)
        
        if self.options.config:
            write_vars = vars.copy()
            del write_vars['project']
            del write_vars['package']
            self.write_vars(self.options.config, write_vars)
        
    def create_template(self, template, output_dir, vars):
        if self.verbose:
            print 'Creating template %s' % template.name
        template.run(self, output_dir, vars)

    ignore_egg_info_files = [
        'top_level.txt',
        'entry_points.txt',
        'requires.txt',
        'PKG-INFO',
        'namespace_packages.txt',
        'SOURCES.txt',
        'dependency_links.txt',
        'not-zip-safe']

    def extend_templates(self, templates, tmpl_name):
        if '#' in tmpl_name:
            dist_name, tmpl_name = tmpl_name.split('#', 1)
        else:
            dist_name, tmpl_name = None, tmpl_name
        if dist_name is None:
            for entry in self.all_entry_points():
                if entry.name == tmpl_name:
                    tmpl = entry.load()(entry.name)
                    dist_name = entry.dist.project_name
                    break
            else:
                raise LookupError(
                    'Template by name %r not found' % tmpl_name)
        else:
            dist = pkg_resources.get_distribution(dist_name)
            entry = dist.get_entry_info(
                'paste.paster_create_template', tmpl_name)
            tmpl = entry.load()(entry.name)
        full_name = '%s#%s' % (dist_name, tmpl_name)
        for item_full_name, item_tmpl in templates:
            if item_full_name == full_name:
                # Already loaded
                return
        for req_name in tmpl.required_templates:
            self.extend_templates(templates, req_name)
        templates.append((full_name, tmpl))
        
    def all_entry_points(self):
        if not hasattr(self, '_entry_points'):
            self._entry_points = list(pkg_resources.iter_entry_points(
            'paste.paster_create_template'))
        return self._entry_points

    def display_vars(self, vars):
        vars = vars.items()
        vars.sort()
        print 'Variables:'
        max_var = max([len(n) for n, v in vars])
        for name, value in vars:
            print '  %s:%s  %s' % (
                name, ' '*(max_var-len(name)), value)
        
    def list_templates(self):
        templates = []
        for entry in self.all_entry_points():
            try:
                templates.append(entry.load()(entry.name))
            except Exception, e:
                # We will not be stopped!
                print 'Warning: could not load entry point %s (%s: %s)' % (
                    entry.name, e.__class__.__name__, e)
        max_name = max([len(t.name) for t in templates])
        templates.sort(lambda a, b: cmp(a.name, b.name))
        print 'Available templates:'
        for template in templates:
            # @@: Wrap description
            print '  %s:%s  %s' % (
                template.name,
                ' '*(max_name-len(template.name)),
                template.summary)
        
    def inspect_files(self, output_dir, templates, vars):
        file_sources = {}
        for template in templates:
            self._find_files(template, vars, file_sources)
        self._show_files(output_dir, file_sources)
        self._show_leftovers(output_dir, file_sources)

    def _find_files(self, template, vars, file_sources):
        tmpl_dir = template.template_dir()
        self._find_template_files(
            template, tmpl_dir, vars, file_sources)

    def _find_template_files(self, template, tmpl_dir, vars,
                             file_sources, join=''):
        full_dir = os.path.join(tmpl_dir, join)
        for name in os.listdir(full_dir):
            if name.startswith('.'):
                continue
            if os.path.isdir(os.path.join(full_dir, name)):
                self._find_template_files(
                    template, tmpl_dir, vars, file_sources,
                    join=os.path.join(join, name))
                continue
            partial = os.path.join(join, name)
            for name, value in vars.items():
                partial = partial.replace('+%s+' % name, value)
            if partial.endswith('_tmpl'):
                partial = partial[:-5]
            file_sources.setdefault(partial, []).append(template)

    _ignore_filenames = ['.*', '*.pyc', '*.bak*']
    _ignore_dirs = ['CVS', '_darcs', '.svn']

    def _show_files(self, output_dir, file_sources, join='', indent=0):
        pad = ' '*(2*indent)
        full_dir = os.path.join(output_dir, join)
        names = os.listdir(full_dir)
        dirs = [n for n in names
                if os.path.isdir(os.path.join(full_dir, n))]
        dirs.sort()
        names.sort()
        for name in names:
            skip_this = False
            for ext in self._ignore_filenames:
                if fnmatch.fnmatch(name, ext):
                    if self.verbose > 1:
                        print '%sIgnoring %s' % (pad, name)
                    skip_this = True
                    break
            if skip_this:
                continue
            partial = os.path.join(join, name)
            if partial not in file_sources:
                if self.verbose > 1:
                    print '%s%s (not from template)' % (pad, name)
                continue
            templates = file_sources.pop(partial)
            print '%s%s from:' % (pad, name)
            for template in templates:
                print '%s  %s' % (pad, template.name)
        for dir in dirs:
            if dir in self._ignore_dirs:
                continue
            print '%sRecursing into %s/' % (pad, dir)
            self._show_files(
                output_dir, file_sources,
                join=os.path.join(join, dir),
                indent=indent+1)

    def _show_leftovers(self, output_dir, file_sources):
        if not file_sources:
            return
        print
        print 'These files were supposed to be generated by templates'
        print 'but were not found:'
        file_sources = file_sources.items()
        file_sources.sort()
        for partial, templates in file_sources:
            print '  %s from:' % partial
            for template in templates:
                print '    %s' % template.name

    def list_variables(self, templates):
        for tmpl_name, tmpl in templates:
            if not tmpl.read_vars():
                if self.verbose > 1:
                    self._show_template_vars(
                        tmpl_name, tmpl, 'No variables found')
                continue
            self._show_template_vars(tmpl_name, tmpl)

    def _show_template_vars(self, tmpl_name, tmpl, message=None):
        title = '%s (from %s)' % (tmpl.name, tmpl_name)
        print title
        print '-' * len(title)
        if message is not None:
            print '  %s' % message
            print
            return
        tmpl.print_vars(indent=2)
