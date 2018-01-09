#!/usr/bin/env python

import TestSCons

test = TestSCons.TestSCons()

test.write('test.foo', r"""
\documentclass{article}
\begin{document}
Hello world.
\end{document}
""")

test.write('SConstruct', """
env = Environment()

foo2latex = Builder(action = 'cat $SOURCE > $TARGET', \
                    suffix = '.latex', \
                    src_suffix = '.foo')
env.Append(BUILDERS = {'Foo2latex' : foo2latex})

pdf_bldr = env['BUILDERS']['PDF']
pdf_bldr.add_src_builder(foo2latex)

env.PDF('test.pdf', 'test.foo')
""")

test.run()
test.must_exist('test.pdf')
test.pass_test()
