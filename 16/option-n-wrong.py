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

import os
import os.path
import re
import string
import sys
import TestCmd
import TestSCons

python = TestSCons.python

test = TestSCons.TestSCons()

test.write('copy.py', r"""
import sys
open(sys.argv[2],'wb').write(open(sys.argv[1],'rb').read())
sys.exit(0)
""")

test.write('build.py', r"""
import sys
iname,oname = sys.argv[1:3]
if iname[0] == '-':
    iname,oname = sys.argv[2:4]
input = open(iname, 'rb')
output = open(oname, 'wb')

def process(infp, outfp):
    for line in infp.readlines():
        if line[:8] == 'include ':
            process(open(line[8:-1], 'rb'), outfp)
        else:
            outfp.write(line)

process(input, output)

sys.exit(0)
""")

test.write('f1.in', "f1.in\ninclude f2.out\n")
test.write('f2.in', "f2.in\n")

######################################################################
## First pass: simple build, verify basic operation as expected

test.write('SConstruct', """

import re

def my_scan(node, env, scanpaths):
    return re.compile(r'^include\s+(\S+)$', re.M).findall(
                                               node.get_contents())

myscan = Scanner(name='MyScan', function=my_scan)

MyBuild = Builder(action = r'%s build.py $SOURCE $TARGETS',
                  source_scanner = myscan)
env = Environment(BUILDERS = { 'MyBuild' : MyBuild })
env.MyBuild(target = 'f1.out', source = 'f1.in')
env.MyBuild(target = 'f2.out', source = 'f2.in')
""" % python)

# First do a normal build; remember what is actually performed

test.run(arguments='.')
build_ops = test.stdout()

test.must_match('f1.out', "f1.in\nf2.in\n")
test.must_match('f2.out', "f2.in\n")

# Now clean things up

test.run(arguments='-c')

# Now do a pretend build and verify the output matches what would have
# actually been seen on a normal build.

test.run(arguments='--no-cache -n .', stdout=build_ops)


######################################################################
## Second pass: scanner operates on derived target that does not exist,
## implicit dependency is not shown during no-exec build.


test.write('SConstruct', """

import re

def my_scan(node, env, scanpaths):
    return re.compile(r'^include\s+(\S+)$', re.M).findall(
                                               node.get_contents())

myscan = Scanner(name='MyScan', function=my_scan)

MyBuild1 = Builder(action = r'%(python)s copy.py $SOURCE $TARGETS')
MyBuild2 = Builder(action = r'%(python)s build.py $SOURCE $TARGETS',
                   source_scanner = myscan)
env = Environment(BUILDERS = { 'bld1' : MyBuild1, 'bld2' : MyBuild2 })

f1 = env.bld1(target = 'f1.out', source = 'f1.in')
f2 = env.bld1(target = 'f2.out', source = 'f2.in')
final = env.bld2(target = 'f1.final', source = f1)
Default(final)
""" % {'python':python} )

# First do a normal build; remember what is actually performed

test.run(arguments='.')
build_ops = test.stdout()

# Now clean things up

test.run(arguments='-c')

failed = 0
def cmp_stdout(normal, noexec, reason):
    if normal != noexec:
        print '==== noexec build output mismatch ================'
        print '===\n===','\n=== '.join(reason.split('\n')),'\n==='
        print 'NORMAL: ','\n         '.join(build_ops.split('\n'))
        print 'NOEXEC: ','\n         '.join(test.stdout().split('\n')),
        #print '======================================'
        print
        return 1
    return 0


# Now do a pretend build: note that the order of the pretend build is
# wrong.

test.run(arguments='--no-cache -n .')

if cmp_stdout(build_ops, test.stdout(), """\
Second-level source's implicit dependency not detected,
targets built in incorrect order."""):
    failed = 1

# Now do a pretend build with a target that would have an implicit
# dependency and note that the implicit dependency is not shown as
# built.

test.run(arguments='--no-cache -n')

if cmp_stdout(build_ops, test.stdout(), """\
Implicit source not built as needed for primary target."""):
    failed = 1

# Prove that the test is correct.

test.run(arguments='--no-cache .')
if cmp_stdout(build_ops, test.stdout(), """\
TEST NOT WORKING CORRECTLY; OUTPUT SHOULD HAVE MATCHED."""):
    raise 'Test Is Invalid'


######################################################################
## Third pass: list of actions fails because settings made by previous
## actions are not performed and therefore not available to subsequent
## actions.

test.write('SConstruct', """

def action1(target, source, env):
    env.PrependENVPath('PATH', 'TESTPATH')

def action2_show(target, source, env):
    return 'PATH is %%s'%%str(env['ENV']['PATH'])

def action2(target, source, env):
    pass

def action3(target, source, env):
    env['BLDFLAGS'] = '-FLAG=PRESENT'

actionlist = [ Action(action1, None),
               Action(action2, action2_show) ]

MyBuild1 = Builder(action = actionlist)
MyBuild2 = Builder(action = [ Action(action3, None), "$BLDCOM" ])
env = Environment(BUILDERS = { 'bld1' : MyBuild1,
                               'bld2' : MyBuild2},
                  BLDCOM = "$BLDCMD $BLDFLAGS $SOURCE $TARGET",
                  BLDCMD = "%s build.py",
                  BLDFLAGS = "")

env.bld1(target = 'f1.out', source = 'f1.in')
env.bld2(target = 'f2.out', source = 'f2.in')
""" % python)

# First do a normal build; remember what is actually performed

test.run(arguments='.')
build_ops = test.stdout()

# Now clean things up

test.run(arguments='-c')

test.run(arguments='--no-cache -n .')

if cmp_stdout(build_ops, test.stdout(), """\
Action operations not propagated to dependent actions."""):
    failed = 1


test.fail_test(failed)
test.pass_test()
