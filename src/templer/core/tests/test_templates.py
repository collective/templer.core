# -*- coding: utf-8 -*-

__docformat__ = 'restructuredtext'

import unittest2 as unittest

import doctest
import sys
import os
import shutil
import subprocess
import tempfile

current_dir = os.path.abspath(os.path.dirname(__file__))


def rmdir(*args):
    dirname = os.path.join(*args)
    if os.path.isdir(dirname):
        shutil.rmtree(dirname)


def templer(cmd, runner=None):
    print "templer %s" % cmd
    from templer.core.control_script import run
    args = cmd.split()
    kwargs = {'exit': False}
    if runner is not None:
        kwargs['runner'] = runner
    run(*args, **kwargs)


# BBB
paster = templer


def read_sh(cmd):
    _cmd_list = cmd.strip().split(" ")
    proc = subprocess.Popen(_cmd_list,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT)
    proc.wait()
    results = proc.stdout.read()
    proc.stdout.close()
    return results


def exit_code_sh(cmd):
    _cmd_list = cmd.strip().split(" ")
    proc = subprocess.Popen(_cmd_list,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    proc.wait()
    return proc.returncode


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
    open(filename, 'w').write(kwargs.get('data', ''))


def clean_working_set():
    """remove pkg entries created during tests"""
    from pkg_resources import working_set as ws
    #cleanup entries in the working set
    for k, v in ws.by_key.items():
        if not os.path.exists(v.location):
            del ws.by_key[k]

    for i in reversed(range(len(ws.entries))):
        if not os.path.exists(ws.entries[i]):
            del ws.entries[i]

    sys.path = ws.entries[:]


def _testSetUp(test):
    test.orig_dir = os.getcwd()
    test.temp_dir = tempfile.mkdtemp()
    cd(test.temp_dir)


def _testTearDown(test):
    cd(test.orig_dir)
    shutil.rmtree(test.temp_dir, ignore_errors=True)
    test.temp_dir = None
    clean_working_set()


def doc_suite(test_dir, setUp=_testSetUp, tearDown=_testTearDown, globs=None):
    """Returns a test suite, based on doctests found in /docs."""
    suite = []
    if globs is None:
        globs = globals()

    flags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE |
             doctest.REPORT_ONLY_FIRST_FAILURE)

    doctest_dir = os.path.join(test_dir, 'docs')

    # filtering files on extension
    docs = [os.path.join(doctest_dir, doc) for doc in
            os.listdir(doctest_dir) if doc.endswith('.txt')]

    for test in docs:
        suite.append(doctest.DocFileSuite(test, optionflags=flags,
                                          globs=globs, setUp=setUp,
                                          tearDown=tearDown,
                                          module_relative=False))

    return unittest.TestSuite(suite)


def test_suite():
    """returns the test suite"""
    suite = doc_suite(current_dir)
    return suite

if __name__ == '__main__':
    unittest.main(defaultTest='test_suite')
