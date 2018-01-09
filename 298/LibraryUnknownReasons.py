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

__revision__ = "?"

import TestSCons
import sys

test = TestSCons.TestSCons()

#Tests whether repeated source files causes rebuilds for "unknown reasons".

if sys.platform == 'win32':

    #Forcing use of mingw/cygwin gcc here.
    #MSVC 2005, at least, complains about repeated objects which
    #gives the user a hint that something is wrong even though
    #--debug-explain cannot currently tell us what it is. 0.97.0d20071212
    #Here is the snippet of MSVC output
    #scons: rebuilding `foo1.lib' for unknown reasons
    #lib /nologo /OUT:foo1.lib f1.obj f1.obj
    #f1.obj : warning LNK4042: object specified more than once; extras ignored

    test.write('SConstruct', """
path = [ 'C:/cygwin/bin',
         'C:/cygwin/usr/bin' ]

env = Environment(ENV   = {'PATH' : path },
                  tools = ['mingw'],
                  LIBS = [ 'foo1' ],
                  LIBPATH = [ '.' ])
env.Library(target = 'foo1', source = ['f1.c', 'f1.c'])
""")
else:
    test.write('SConstruct', """
env = Environment(LIBS = [ 'foo1' ],
                  LIBPATH = [ '.' ])
env.Library(target = 'foo1', source = ['f1.c', 'f1.c'])
""")

test.write('f1.c', r"""
#include <stdio.h>
void
f1(void)
{
        printf("f1.c\n");
}
""")

args = '. --debug=explain'

expect = """
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
scons: building `f1.o' because it doesn't exist
gcc -o f1.o -c f1.c
scons: building `libfoo1.a' because it doesn't exist
ar rc libfoo1.a f1.o f1.o
ranlib libfoo1.a
scons: done building targets.
"""

#test.run(arguments=args, stderr=TestSCons.noisy_ar, match=expect)

test.run(arguments=args)

expect_at_the_moment_but_shouldnt = """
scons: Reading SConscript files ...
scons: done reading SConscript files.
scons: Building targets ...
scons: rebuilding `libfoo1.a' for unknown reasons
ar rc libfoo1.a f1.o f1.o
ranlib libfoo1.a
scons: done building targets.
"""
test.up_to_date(arguments='.')

test.pass_test()
