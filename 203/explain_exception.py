#!/usr/bin/env python

import os.path
import string
import sys
import TestSCons

_python_ = TestSCons._python_

test = TestSCons.TestSCons()

args = "--debug=explain"

test.subdir('src')

test.write(['src', 'SConstruct'],"""
env = Environment()

def action( source, target, env ):
    target[0].get_csig()
    f = open( str(target[0]), 'w' )
    for s in source:
        f.write( s.get_contents() )
    f.close()

builder = env.Builder( action=action )

builder( env, target = "target.txt", source = "source.txt" )
""")

test.write(["src", "source.txt"], "a" )


## first build
expect_build = test.wrap_stdout("""\
scons: building `target.txt' because it doesn't exist
action(["target.txt"], ["source.txt"])
""")

test.run(chdir='src', arguments=args, stdout=expect_build )


## now change source.txt
test.write(["src", "source.txt"], "b" )

## second build
expect_rebuild = test.wrap_stdout("""\
scons: rebuilding `target.txt' because `source.txt' changed
action(["target.txt"], ["source.txt"])
""")

test.run(chdir='src', arguments=args, stdout=expect_rebuild )

