# Copyright 2006 Google, Inc. All Rights Reserved.
# Licensed to PSF under a Contributor Agreement.

"""Fixer for apply().

This converts apply(func, v, k) into (func)(*v, **k)."""

# Local imports
from .. import pytree
from ..pgen2 import token
from .. import fixer_base
from ..fixer_util import Call, Comma

class FixApply1(fixer_base.BaseFix):

    PATTERN = """
    power< 'apply'
        trailer<
            '('
            (
            arglist<
                (not argument<NAME '=' any>) func=any ','
                (not argument<NAME '=' any>) args=
                    atom< '(' tupl=[any] ')' > [','
                (not argument<NAME '=' any>) kwds=any] [',']
            >
            |
            arglist<
                (not argument<NAME '=' any>) func=any ','
                (not argument<NAME '=' any>) args=any [','
                (not argument<NAME '=' any>) kwds=
                    atom< '{' nokw='}' > ] [',']
            >
            |
            arglist<
                (not argument<NAME '=' any>) func=any ','
                (not argument<NAME '=' any>) args=any [','
                (not argument<NAME '=' any>) kwds=any] [',']
            >
            )
            ')'
        >
    >
    """

    def transform(self, node, results):
        #for k,v in sorted(results.items()):
        #    print('result[%s] ==='%k, repr(v))
        #print()
        syms = self.syms
        assert results
        kwds = results.get("kwds")
        func = results["func"].clone()
        lead_blanks = func.get_prefix()
        func.set_prefix("")
        if (func.type not in (token.NAME, syms.atom) and
            (func.type != syms.power or
             func.children[-2].type == token.DOUBLESTAR)):
            # Need to parenthesize
            func = self.parenthesize(func)
        tupl = results.get("tupl")
        if tupl is None:
            # not an explicit tuple for args
            args = results["args"].clone()
            args.set_prefix(lead_blanks)
            l_newargs = [pytree.Leaf(token.STAR, "*"), args]
            comma = True
        elif len(tupl) == 0:
            # an empty tuple for args, don't generate any
            l_newargs = []
            kwds.set_prefix(lead_blanks)
            comma = False
        else:
            # a tuple for args, list arguments instad
            tupl = tupl[0].clone()
            tupl.set_prefix(lead_blanks)
            if len(tupl.children) and tupl.children[-1].type == token.COMMA:
                tupl.children[-1].remove()
            l_newargs = [tupl]
            comma = True
        if kwds is not None and results.get("nokw") is None:
            # keywords and not an empty dict
            kwds = kwds.clone()
            kw_prefix = kwds.get_prefix()
            kwds.set_prefix("")
            if comma: l_newargs.append(Comma())
            l_newargs.extend([pytree.Leaf(token.DOUBLESTAR, "**",
                                          prefix=kw_prefix),
                              kwds])
        # XXX Sometimes we could be cleverer, e.g. apply(f, (x, y) + t)
        # can be translated into f(x, y, *t) instead of f(*(x, y) + t)
        #new = pytree.Node(syms.power, (func, ArgList(l_newargs)))
        return Call(func, l_newargs, prefix=node.get_prefix())
