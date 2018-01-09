#!/usr/bin/env python
#
# __COPYRIGHT__
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

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Verify correct execution when an implicit dependency that we use
via --implicit-cache is deleted from disk.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment(CPPPATH = ['.'])
env.Program('foo.c')
""")

test.write('foo.c', """\
#include <stdio.h>
#include <stdlib.h>
#ifdef FOO
#include <depends.h>
#endif
int
main(int argc, char *argv)
{
    printf("foo.c\\n");
    exit (0);
}
""")

test.write('depends.h', """\
#define STRING  "depends.h"
""")

# Populate the .sconsign file with the implicit dependency.
test.run(arguments='foo.o')
print test.stdout()

test.up_to_date(arguments='foo.o')

# Remove the implicit dependency.
test.unlink('depends.h')

test.run(arguments='--implicit-deps-unchanged foo.o')
#test.run(arguments='--implicit-deps-changed foo.o')
#test.run(arguments='--implicit-cache foo.o')
print test.stdout()


test.pass_test()
