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
Issue 2647 at tigris.org:
Verify that a dependent import library action is built
"""

# TODO(sgk):  The test infrastructure now adds --warn=no-visual-c-missing
# by default, which is not recognized by pre-1.3 SCons versions.
# Setting this to a recognized option allows this script to work
# and be compared with 1.2.0.  We should remove this before checking in.
import os
os.environ['TESTSCONS_SCONSFLAGS'] = '--debug=stacktrace'

import TestSCons

test = TestSCons.TestSCons()

test.subdir('sub1')

test.write('SConstruct', """
env = Environment()

# TODO(sgk):  work around earlier versions not detecting Visual C
# on my system.  Remove before checkin.
import os
env['ENV']['INCLUDE'] = os.environ['INCLUDE']
env['ENV']['LIB'] = os.environ['LIB']
env['ENV']['LIBPATH'] = os.environ['LIBPATH']
env['ENV']['PATH'] = os.environ['PATH']

result = env.SharedLibrary("sub1/a.cpp", no_import_lib=True)
env.Install("test", "sub1/a.lib")
env.Depends("sub1/a.lib", result)
""")

test.write(['sub1', 'a.cpp'], """\
#include <cstdio>
#include <stdlib.h>

__declspec(dllexport) void foo()
{
        std::printf("Hello\\n");
}
""")

test.run(arguments = 'test')

test.must_exist(['sub1', 'a.lib'])

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
