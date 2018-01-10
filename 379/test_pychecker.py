#!/usr/bin/env python
#
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "/home/scons/scons/branch.0/baseline/src/test_pychecker.py 0.97.D001 2007/05/17 11:35:19 knight"

"""
Use pychecker to catch various Python coding errors.
"""

import os
import os.path
import string
import sys

import TestSCons

test = TestSCons.TestSCons()

#test.skip_test('Not ready for clean pychecker output; skipping test.\n')

try:
    import pychecker
except ImportError:
    pychecker = test.where_is('pychecker')
    if not pychecker:
        test.skip_test("Could not find 'pychecker'; skipping test(s).\n")
    program = pychecker
    default_arguments = []
else:
    pychecker = os.path.join(os.path.split(pychecker.__file__)[0], 'checker.py')
    program = sys.executable
    default_arguments = [pychecker]

try:
    cwd = os.environ['SCONS_CWD']
except KeyError:
    src_engine = os.environ['SCONS_LIB_DIR']
else:
    src_engine = os.path.join(cwd, 'build', 'scons-src', 'src', 'engine')
    if not os.path.exists(src_engine):
        src_engine = os.path.join(cwd, 'src', 'engine')

src_engine_ = os.path.join(src_engine, '')

MANIFEST = os.path.join(src_engine, 'MANIFEST.in')
files = string.split(open(MANIFEST).read())

files = filter(lambda f: f[-3:] == '.py', files)

ignore = [
    'SCons/compat/__init__.py',
    'SCons/compat/builtins.py',
    'SCons/compat/_subprocess.py',
    'SCons/Optik/__init__.py',
    'SCons/Optik/errors.py',
    'SCons/Optik/option.py',
    'SCons/Optik/option_parser.py',
]

u = {}
for file in files:
    u[file] = 1
for file in ignore:
    try:
        del u[file]
    except KeyError:
        pass

files = u.keys()

files.sort()

mismatches = []

default_arguments.extend([
    '--quiet',
    '--limit=1000',
])

if sys.platform == 'win32':
    default_arguments.extend([
        '--blacklist', '"pywintypes,pywintypes.error"',
    ])

per_file_arguments = {
    'SCons/__init__.py' : [
        '--varlist', '"__revision__,__version__,__build__,__buildsys__,__date__,__developer__"',
    ],
}

pywintypes_warning = "warning: couldn't find real module for class pywintypes.error (module name: pywintypes)\n"

os.environ['PYTHONPATH'] = src_engine

def debugf(fmt, *args, **kwds):
    '''Formatted print.
    '''
    if 0:  ## 1 or True
        fmt = 'DEBUG ' + fmt
        if kwds:  # either ...
            print(fmt % kwds)
        elif args:  # ... or
            print(fmt % args)
        else:
            print(fmt)

def pychecked(line, py, src, okd=''):
    '''Check whether source line is OK'd.
    '''
    try:  # get source line
        s = src[int(line) - 1]
        p = string.find(s, '#PYCHECKER ')
        if p > 0:  # line OK'd
            okd = string.rstrip(s[p:])
    except:  # ValueError, IndexError:
        debugf('no line %s in file: %s', line, py)
    return okd

def python_source(name, py, src, paths):
    '''Get source code for file name.
    '''
    if name != py and name[-3:] == '.py':  ## name.endswith('.py')
        py, src = name, []  # other source file
        debugf('looking for source file: %s', py)
        for p in paths:  # find file in dirs
            try:
                t = os.path.join(p, py)
                f = open(t, 'r')
                src = f.readlines()
                f.close()
                debugf('found file: %s (%s lines)', t, len(src))
                break
            except (IOError, OSError):
                pass
        else:
            debugf('file not found: %s', py)
    return py, src

OK_d = 1  # print OK'd PyChecker warning messages

def postprocess(output, paths=('', src_engine)):
    '''Process PyChecker output string.

       Adapted from Python Cookbook recipe at ActiveState
       <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/546532>.
    '''
    py  = ''  # source file name
    src = []  # source lines
    ms  = []  # non-OK'd warning messages
    for m in string.split(output, os.linesep):  # process each message
        m = string.rstrip(m)
        if m:  # only non-blank message
            s, okd = string.split(m, ':', 2), ''
            if len(s) > 2:  # file name, line number, rest
                if s[1] and s[1][0] in string.digits:  ## s[1].isdigit()
                    py, src = python_source(s[0], py, src, paths)
                    okd = pychecked(s[1], py, src, okd)
            if not okd:
                ms.append(m)
            elif OK_d:
                m = string.replace(m, src_engine_, '')
                print '%s - %s' % (m, okd)
    return string.join(ms, os.linesep)

for file in files:

    file = os.path.join(src_engine, file)
    args = default_arguments + per_file_arguments.get(file, []) + [file]

    test.run(program=program, arguments=args, status=None, stderr=None)

    stdout = postprocess(test.stdout())
    stdout = string.replace(stdout, src_engine_, '')

    stderr = postprocess(test.stderr())
    stderr = string.replace(stderr, src_engine_, '')
    stderr = string.replace(stderr, pywintypes_warning, '')

    if test.status or stdout or stderr:
        mismatches.append(os.linesep)
        mismatches.append(string.join([program] + args))
        mismatches.append(os.linesep)

        mismatches.append('STDOUT =====================================')
        mismatches.append(os.linesep)
        mismatches.append(stdout)

        if stderr:
            mismatches.append('STDERR =====================================')
            mismatches.append(os.linesep)
            mismatches.append(stderr)

if mismatches:
    print string.join(mismatches[1:], '')
    test.fail_test()

test.pass_test()
