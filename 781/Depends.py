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
Verify use of a batch builder when an explicit dependency is
declared between two target files in the same batch.
"""

import TestSCons

test = TestSCons.TestSCons()

test.write('SConstruct', """
def batch_build(target, source, env):
    for t, s in zip(target, source):
        fp = open(str(t), 'wb')
        fp.write(open(str(s), 'rb').read())
def cat(target, source, env):
    fp = open(str(target[0]), 'wb')
    for s in source:
        fp.write(open(str(s), 'rb').read())
    fp.close
    return 0
env = Environment()
bb = Action(batch_build, batch_key=True)
env['BUILDERS']['Batch'] = Builder(action=bb)
env['BUILDERS']['Cat'] = Builder(action=cat)
f1 = env.Batch('f1.out', 'f1.in')
f2 = env.Batch('f2.out', 'f2.in')
env.Depends(f1, f2)
env.Cat("f.out", [f1, f2])
""")

test.write('f1.in', "f1.in\n")
test.write('f2.in', "f2.in\n")

expect = test.wrap_stdout("""\
batch_build(["f2.out"], ["f2.in"])
batch_build(["f1.out"], ["f1.in"])
cat(["f.out"], ["f1.out", "f2.out"])
""")

test.run(stdout = expect)

test.must_match('f1.out', "f1.in\n")
test.must_match('f2.out', "f2.in\n")
test.must_match('f.out', "f1.in\nf2.in\n")

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
