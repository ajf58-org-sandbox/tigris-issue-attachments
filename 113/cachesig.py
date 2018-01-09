#!/usr/bin/env python
#
# This is an end-to-end SCons test.  It should be invoked via:
# python ./runtest.py test/cachesig.py

# Demonstrate a regression between 0.96.1 and 0.96.3.
#
# SCons incorrectly believes files are stale if they were retrieved
# from the cache in a previous invocation.
#
# The behavior was observed on a debian box for which 
# config.guess returns 'i686-pc-linux-gnu'.  Python 2.5 was used.
#
# The following suffer from the regression:
# - svn co -r 1747 http://scons.tigris.org/svn/scons/branches/core
# - svn co -r 1747 http://scons.tigris.org/svn/scons/trunk
# - The Nov. 6 'testing' release of 0.96.3
# 
# This tarball passes the test:
# - http://prdownloads.sourceforge.net/scons/scons-src-0.96.1.tar.gz
#
# What this script does:
# 1. Set up two identical C project directories called 'alpha' and
#    'beta', which use the same cache
# 2. Invoke scons on 'alpha'
# 3. Invoke scons on 'beta', which successfully draws output 
#    files from the cache
# 4. Invoke scons again, asserting (with -q) that 'beta' is up to date
#
# Step 4 fails.  In practice, this problem leads to lots 
# of unecessary fetches from the cache during incremental 
# builds (because they behave like non-incremental builds).

import TestSCons

test = TestSCons.TestSCons()

test.subdir('cache', 'alpha', 'beta')

foo_c = """
int main(){ return 0; }
"""

sconstruct = """
import os
CacheDir('%s')
Program('foo', 'foo.c')
""" % test.workpath('cache')

test.write('alpha/foo.c', foo_c)
test.write('alpha/SConstruct', sconstruct)

test.write('beta/foo.c', foo_c)
test.write('beta/SConstruct', sconstruct)

# First build, populates the cache
test.run(chdir = 'alpha', arguments = '.')

# Second build, everything is a cache hit
test.run(chdir = 'beta', arguments = '.')

# Since we just built 'beta', it ought to be up to date.
test.run(chdir = 'beta', arguments = '. -q')

test.pass_test()
