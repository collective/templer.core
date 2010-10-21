# -*- coding: utf-8 -*-
"""
Grabs the tests in doctest
"""
__docformat__ = 'restructuredtext'

import unittest
import doctest
import sys
import os
import shutil
import popen2
import tempfile

current_dir = os.path.abspath(os.path.dirname(__file__))

def rmdir(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)


def paster(cmd):
    print "paster %s" % cmd
    from paste.script import command
    #the overwite option for the create command defaults to True
    #but in the paste.script.command it defaults to False.
    #so we fixe it here
    if 'create' in cmd:
        cmd += " --overwrite=1"
    args = cmd.split()
    options, args = command.parser.parse_args(args)
    options.base_parser = command.parser
    command.system_plugins.extend(options.plugins or [])
    commands = command.get_commands()
    command_name = args[0]
    if command_name not in commands:
        command = command.NotFoundCommand
    else:
        command = commands[command_name].load()
    runner = command(command_name)
    runner.run(args[1:])


def read_sh(cmd):
    _cmd = cmd
    old = sys.stdout 
    child_stdout_and_stderr, child_stdin = popen2.popen4(_cmd)
    child_stdin.close()
    return child_stdout_and_stderr.read()


def ls(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        filenames = os.listdir(dirname)
        for filename in sorted(filenames):
            # Depending on how pristine your testing env is, the
            # Paster/PasteScript eggs may end up here; this ins't
            # very predictable. Hide them.
            if filename.endswith('.egg'):
                continue
            print filename
    else:
        print 'No directory named %s' % dirname


def cd(*args):
    dirname = os.path.join(*args)
    os.chdir(dirname)


def config(filename):
    return os.path.join(current_dir, filename)


def cat(*args):
    filename = os.path.join(*args)
    if os.path.isfile(filename):
        print open(filename).read()
    else:
        print 'No file named %s' % filename


def touch(*args, **kwargs):
    filename = os.path.join(*args)
    open(filename, 'w').write(kwargs.get('data',''))


class ZopeSkelLayer:

    temp_dir = None

    @classmethod
    def testSetUp(self):
        self.temp_dir = tempfile.mkdtemp()
        cd(self.temp_dir)
      
    @classmethod
    def testTearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        self.temp_dir = None

        from pkg_resources import working_set as ws
        #cleanup entries in the working set
        for k, v in ws.by_key.items():
            if not os.path.exists(v.location):
                del ws.by_key[k]

        for i in reversed(range(len(ws.entries))):
            if not os.path.exists(ws.entries[i]):
                del ws.entries[i]

        sys.path = ws.entries[:]

def testSetUp(test):
    test.temp_dir = tempfile.mkdtemp()
    cd(test.temp_dir)

def testTearDown(test):
    shutil.rmtree(test.temp_dir, ignore_errors=True)
    test.temp_dir = None

    from pkg_resources import working_set as ws
    #cleanup entries in the working set
    for k, v in ws.by_key.items():
        if not os.path.exists(v.location):
            del ws.by_key[k]

    for i in reversed(range(len(ws.entries))):
        if not os.path.exists(ws.entries[i]):
            del ws.entries[i]

    sys.path = ws.entries[:]

