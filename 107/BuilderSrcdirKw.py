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

import TestSCons
test = TestSCons.TestSCons()
#test.verbose_set(10000)

test.subdir('foo')
test.write(['foo','f1.c'], '#include<stdio.h>\nvoid f1(void){printf("f1\\n");}\n')
test.write(['foo','f2.c'], '#include<stdio.h>\nvoid f2(void){printf("f2\\n");}\n')
test.write(['foo','f3.c'], '#include<stdio.h>\nvoid f3(void){printf("f3\\n");}\n')
test.write(['foo','main.c'], """
#include<stdio.h>
extern void f1(void);
extern void f2(void);
extern void f3(void);
int main(void){f1(); f2(); f3(); return 0;}
""")
expected="f1\nf2\nf3\n"

test.write('SConstruct',"Program(target='bar',source=['main.c','f1.c','f2.c','f3.c'],srcdir='foo')\n")
test.run('.')
test.run(program=test.workpath('bar'),stdout=expected)
test.pass_test()
