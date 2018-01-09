#!/usr/bin/env python

import os.path
import string
import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

test.subdir('src')

test.write(['src', 'SConstruct'],"""
env = Environment()

env.SetOption("max_drift", 1)
env.TargetSignatures( "content" )

def action( source, target, env ):
    f = open( str(target[0]), 'w' )
    for s in source:
        f.write( s.get_contents() )
    f.close()

builder = env.Builder( action=action )

builder( env, target = "target1.txt", source = "source1.txt" )
builder( env, target = "target2.txt", source = "target1.txt" )
""")

test.write(["src", "source1.txt"], "a" )


## first build - should build target1.txt and target2.txt
expect_build_both = test.wrap_stdout("""\
action(["target1.txt"], ["source1.txt"])
action(["target2.txt"], ["target1.txt"])
""")

test.run(chdir='src', stdout=expect_build_both )


# run it again...it shouldn't need to rebuild anything this time
expect_up_to_date = test.wrap_stdout("""\
scons: `.' is up to date.
""")

test.run(chdir='src', stdout=expect_up_to_date )


## now change source1.txt
test.write(["src", "source1.txt"], "b" )

## should build both...
test.run(chdir='src', stdout=expect_build_both)

## ...but not the second time
test.run(chdir='src', stdout=expect_up_to_date)


