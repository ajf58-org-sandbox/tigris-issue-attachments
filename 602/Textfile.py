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

import os
import os.path
import string
import time
import TestSCons

test = TestSCons.TestSCons()

foo1  = test.workpath('foo1.txt')
foo2  = test.workpath('foo2.txt')
foo1a = test.workpath('foo1a.txt')
foo2a = test.workpath('foo2a.txt')
foo_args = 'foo1.txt foo2.txt foo1a.txt foo2a.txt'

test.write('SConstruct', """
env = Environment(tools=['textfile'])
data0 = ['Goethe', 'Schiller']
data  = ['lalala', 42, data0, 'tanteratei']

env.Textfile('foo1', data)
env.Textfile('foo2', data, LINESEPERATOR='|*')
env.Textfile('foo1a.txt', data + [''])
env.Textfile('foo2a.txt', data + [''], LINESEPERATOR='|*')
""")

textparts = ['lalala', '42',
             'Goethe', 'Schiller',
             'tanteratei']
foo1Text  = string.join(textparts, os.linesep)
foo2Text  = string.join(textparts, '|*')
foo1aText = foo1Text + os.linesep
foo2aText = foo2Text + '|*'

test.run(arguments = '.')

#test.run(program = foo2, stdout = "foo2.txt\n")
#test.run(program = foo1, stdout = "foo1.txt\n")

test.up_to_date(arguments = '.')

# make sure, the contents is as expected
#print repr(open(foo1).read())
#print repr(open(foo2).read())
test.fail_test(foo1Text  != open(foo1 ).read())
test.fail_test(foo2Text  != open(foo2 ).read())
test.fail_test(foo1aText != open(foo1a).read())
test.fail_test(foo2aText != open(foo2a).read())

# make sure the files didn't get rewritten, because nothing changed:
oldtime1  = os.path.getmtime(foo1)
oldtime2  = os.path.getmtime(foo2)
oldtime1a = os.path.getmtime(foo1a)
oldtime2a = os.path.getmtime(foo2a)
time.sleep(2) # introduce a small delay, to make the test valid
test.run(arguments = '.')
test.fail_test(oldtime1  != os.path.getmtime(foo1 ))
test.fail_test(oldtime2  != os.path.getmtime(foo2 ))
test.fail_test(oldtime1a != os.path.getmtime(foo1a))
test.fail_test(oldtime2a != os.path.getmtime(foo2a))

# write the contents and 
# make sure the files didn't get rewritten, because nothing changed:
test.write(foo1 , foo1Text)
test.write(foo2 , foo2Text)
test.write(foo1a, foo1aText)
test.write(foo2a, foo2aText)
oldtime1  = os.path.getmtime(foo1)
oldtime2  = os.path.getmtime(foo2)
oldtime1a = os.path.getmtime(foo1a)
oldtime2a = os.path.getmtime(foo2a)
time.sleep(2) # introduce a small delay, to make the test valid
test.run(arguments = '.')
test.fail_test(oldtime1  != os.path.getmtime(foo1 ))
test.fail_test(oldtime2  != os.path.getmtime(foo2 ))
test.fail_test(oldtime1a != os.path.getmtime(foo1a))
test.fail_test(oldtime2a != os.path.getmtime(foo2a))

test.pass_test()

 	  	 
