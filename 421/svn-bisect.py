#!/usr/bin/env python
# -*- Python -*-

import sys
from optparse import OptionParser
import subprocess

parser = OptionParser(usage="%prog lower-revision upper-revision test_script arg1 arg2",
                      description="Binary search for a bug in a SVN checkout")

(options,script_args) = parser.parse_args()

if len(script_args) < 1:
    parser.error("Need a lower revision!")
elif len(script_args) < 2:
    parser.error("Need an upper revision!")
elif len(script_args) < 3:
    parser.error("Need a script to run!")

lower = int(script_args[0])
upper = int(script_args[1])
script = script_args[2:]

def error(s):
    print >>sys.stderr, "**************", s, "**************"
    sys.exit(1)    

def updaterevisions(lower,upper):
    print "************** %s revisions to test (bug bracketed by [%s,%s])" % (int((upper-lower+1)/2),lower,upper)

def testfail(revision,script_and_args):
    "Return true if test fails"
    print "Updating to revision %s" % revision
    if subprocess.call(["svn","up","-r",str(revision)]) != 0:
        raise RuntimeError, "SVN did not update properly to revision %s" % revision
    return subprocess.call(script_and_args,shell=False) != 0

###updaterevisions(lower,upper)

print "************** Testing lower revision", lower
lowerfails = testfail(lower,script)
print "************** Testing upper revision", upper
upperfails = testfail(upper,script)
if upperfails == lowerfails:
    error("Upper and lower revisions must bracket the failure!")

while upper-lower > 1:
    msg = "************** %s revisions to test (bug bracketed by [%s,%s])"
    print msg % (int((upper-lower+1)/2),lower,upper)

    mid = int((lower + upper)/2)
    midfails = testfail(mid,script)
    if midfails == lowerfails:
        lower = mid
        lowerfails = midfails
    else:
        upper = mid
        upperfails = midfails

if upperfails == lowerfails: lower = upper
print "The error was caused by change %s" % lower
