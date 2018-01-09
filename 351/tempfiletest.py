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
Put scons TEMPFILE support through some of it's paces
"""

import os
import stat

import TestSCons

test = TestSCons.TestSCons()

binPath = ['bin dir']
binName = ['testme.py']
test.subdir( binPath )
binFullName = os.path.normpath( binPath[0] + '/' + binName[0] )

test.write(binPath + binName, """\
#!/usr/bin/env python
import sys
if len( sys.argv ) != 2 :
    print( 'ERROR: expecting one and only one argument!' )
f = open( sys.argv[1][1:], 'r' )
contents = f.read()
f.close()
outFile, rest = contents.split( ' ' , 1 )
f = open( outFile, 'w' )
f.write( rest.strip() )
f.close()
""")

testme_py = test.workpath(binFullName)
st = os.stat(testme_py)
os.chmod(testme_py, st[stat.ST_MODE]|0111)

sourcePath = 'input dir'
sourceName = 'inputFile%d'
numFiles = 100
sourceTemplate = os.path.normpath( '%s/%s' % (sourcePath, sourceName) )
test.subdir( [sourcePath] )

test.write('SConstruct', """
import os
env = Environment(
    BUILDBIN = "%s",
    BUILDCOM = "${TEMPFILE('$\\"BUILDBIN\\" $TARGET $SOURCES')}",
    MAXLINELENGTH = 32,
)
env.Command('foo.out', ['%s' %% x for x in range(0,%d)], '$BUILDCOM')
""" % (binFullName,sourceTemplate,numFiles) )

for x in range(0, numFiles ) :
    test.write( [sourcePath,sourceName % x] , "dummy\n")

test.run(arguments = ' --quiet -Q .', stdout = '' )

output = ' '.join( ['"' + sourceTemplate % (x) + '"' for x in range(0, numFiles)] )
test.must_match( 'foo.out', output )

test.pass_test()
