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

class _Processor():  ## (object)
    '''Processor to handle suppression of OK'd PyChecker
       warning messages, marked as OK in the source code.

       Adapted from Python Cookbook recipe at ActiveState
       <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/546532>.
    '''
    _name = ''  # source file name
    _code = []  # source code lines
    _dirs = ()  # source file directories
    dbg   = 0   # debug print
    OK    = '#PYCHECKER '  # source marker
    OKd   = True  # print OK'd warnings

    def __init__(self, *dirs):
        self._dirs = dirs

    def debugf(self, fmt, *args):
        '''Debug print.
        '''
        if self.dbg:
            f = 'DEBUG ' + fmt
            if args:
                print(f % args)
            else:
                print(f)

    def get(self, name):
        '''Get source code for given file.
        '''
        self._code = []
        self._name = name
        if name[-3:] == '.py':  ## name.endswith('.py')
            self.debugf('looking for file: %s', name)
            if os.path.isabs(name):
                 # assert(is.path.join('', name) == name)
                ds = ('',)
            else:
                ds = self._dirs
            for d in ds:  # find file
                try:
                    t = os.path.join(d, name)
                    f = open(t, 'r')
                    s = f.readlines()
                    f.close()
                    self.debugf('found file: %s (%s lines)', t, len(s))
                    self._code = s
                    break
                except (IOError, OSError):
                    pass
            else:
                self.debugf('file not found: %s', name)

    def isOK(self, name, line):
        '''Check whether source line is marked.
        '''
        if name != self._name:
            self.get(name)
        try:  # get source line
            s = self._code[int(line) - 1]
            p = string.find(s, self.OK)
            if p > 0:  # line OK'd
                return string.rstrip(s[p:])
        except (ValueError, IndexError):
            self.debugf('no line %s in file: %s', line, self._name)
        return ''  # not OK'd, not found, etc.

    def process(self, output, *removes):
        '''Process output, passed as single string.
        '''
        ms = []  # non-OK'd warning messages
        for m in string.split(output, os.linesep):  # process each message
            m = string.rstrip(m)
            if m:  # only non-blank message
                s, ok = string.split(m, ':', 2), ''
                if len(s) > 2:  # file name, line number, rest
                    if s[1] and s[1][0] in string.digits:  ## s[1].isdigit()
                        ok = self.isOK(s[0], s[1])
                for r in removes:
                    m = string.replace(m, r, '')
                if not ok:
                    ms.append(m)
                elif self.OKd:
                    print('%s - %s' % (m, ok))
        return string.join(ms, os.linesep)  # as string

for file in files:

    file = os.path.join(src_engine, file)
    args = default_arguments + per_file_arguments.get(file, []) + [file]
    post = _Processor(src_engine, '.')

    test.run(program=program, arguments=args, status=None, stderr=None)

    stdout = post.process(test.stdout(), src_engine_)

    stderr = string.replace(test.stderr(), pywintypes_warning, '')
    stderr = post.process(stderr, src_engine_)

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
