#!/bin/sh
#
# test big files
#
tmp=/tmp/$$
here=`pwd`
if [ $? -ne 0 ]; then exit 1; fi

fail()
{
        echo FAILED 1>&2
	bash
        cd $here
        rm -rf $tmp
        exit 1
}

pass()
{
	echo PASSED 1>&2
        cd $here
        rm -rf $tmp
        exit 0
}
trap "fail" 1 2 3 15

mkdir $tmp
if [ $? -ne 0 ]; then exit 1; fi
cd $tmp
if [ $? -ne 0 ]; then fail; fi

dd if=/dev/zero of=test.big seek=900 bs=1M count=0 2>/dev/null
if [ $? -ne 0 ]; then fail; fi

cat >test.scons << 'EOF'
import os
bigfile = File('test.big')
def get_size(target,source,env=None):
    size = os.stat(source[0].abspath).st_size
    dest = open(target[0].abspath,'w')
    dest.write(str(size))
    dest.close()
size = File('test.size')
dep = Command(size,bigfile,Action(get_size))
EOF

# The result should be like this:
echo -n 943718400 > test.ok

scons -Q -f test.scons test.size
if [ $? -ne 0 ]; then fail; fi

cmp test.ok test.size
if [ $? -ne 0 ]; then fail; fi

pass
