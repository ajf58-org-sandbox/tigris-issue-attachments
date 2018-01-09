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

test.write('SConstruct', """
def posix_gen(source, target, env, for_signature):
    return 'echo PosixGen > ${SOURCE.posix.base}'
def win32_gen(source, target, env, for_signature):
    return 'echo Win32Gen > ${SOURCE.win32.base}'
env = Environment()
env.Append(BUILDERS = {
    'PosixGen' : Builder(generator = posix_gen),
    'Win32Gen' : Builder(generator = win32_gen),
    'PosixStr' : Builder(action = 'echo PosixStr > ${SOURCE.posix.base}'),
    'Win32Str' : Builder(action = 'echo Win32Str > ${SOURCE.win32.base}'),
})
env.PosixGen('posix_gen.txt')
env.Win32Gen('win32_gen.txt')
env.PosixStr('posix_str.txt')
env.Win32Str('win32_str.txt')
""")

test.write('posix_gen.txt', "\n")
test.write('win32_gen.txt', "\n")
test.write('posix_str.txt', "\n")
test.write('win32_str.txt', "\n")

test.run()
print test.stdout()

test.pass_test()
