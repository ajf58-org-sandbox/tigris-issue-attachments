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
XXX Put a description of the test here.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment(S=['main.c', 'f1.c', 'f2.c'])
env.Program('foo', "$S")
""")

test.write('main.c', """\
int
main(int argc, char *argv[]) {
        f1();
        f2();
        printf("main.c\n");
        exit (0);
}
""")

test.write('f1.c', """\
void
f1() {
        printf("f1.c\n");
}
""")

test.write('f2.c', """\
void
f2() {
        printf("f2.c\n");
}
""")

test.run(arguments = '.')

test.run(program = test.workpath('foo'), stdout = "f1.c\nf2.c\nmain.c\n")

test.pass_test()
