""" Fixer for string.func(str, any) --> str.func(any)
    Also comments out 'import string' which can be uncommented if other string
    module attributes are used.

    If string is imported as something else (ie: import string as str;
    str.func(spam, eggs)) method calls will not get fixed.
    """

# TODO: warn about 'from string import ...'
# TODO: string.(atof|atoi|atol)(*args) ==> (float|int|long)(*args)
# TODO: remove string from a list of imports (e.g., 'import os, sys, string')

# Local imports
from .. import fixer_base
from .. import pytree
from ..pgen2 import token

class FixStrFuncs(fixer_base.BaseFix):
    str_funcs = "(" + '|'.join([repr(t) for t in [
              'capitalize',
              'center',
              'count',
              'decode',
              'encode',
              'endswith',
              'expandtabs',
              'find',
              'index',
              'isalnum',
              'isalpha',
              'isdigit',
              'islower',
              'isspace',
              'istitle',
              'isupper',
              #'join', --- special case; str arg not first
              'ljust',
              'lower',
              'lstrip',
              'replace',
              'rfind',
              'rindex',
              'rjust',
              'rstrip',
              'split',
              'splitlines',
              'startswith',
              'strip',
              'swapcase',
              'title',
              'translate',
              'upper',
          ]]) + ")"

    # There must be a better way to specify these patterns, since all
    # except one are variations on one theme.
    PATTERN = """
              power< mod='string' trailer< '.' %(str_funcs)s >
                  trailer< '(' arglist< arg=any comma=',' rest=[any] > ')' >
              >
              |
              power< mod='string' trailer< '.' %(str_funcs)s >
                  trailer< '(' arglist< arg=any comma=',' rest=[any]
                      ',' [any]
                  > ')' >
              >
              |
              power< mod='string' trailer< '.' %(str_funcs)s >
                  trailer< '(' arglist< arg=any comma=',' rest=[any]
                      ',' [any] ',' [any]
                  > ')' >
              >
              |
              power< mod='string' trailer< '.' %(str_funcs)s >
                  trailer< '(' arg=any ')' >
              >
              |
              power< mod='string' trailer< '.' join='join' >
                  trailer< '(' arglist< any comma=',' arg=any > ')' >
              >
              |
              power< mod='string' trailer< '.' 'join' >
                  trailer< '(' any ')' >
              >
              |
              import_name< imp='import' 'string' >
              |
              power< 'string' trailer< '.' fun=any > trailer< '(' any ')' > >
              |
              power< 'string' trailer< '.' attr=any > >
              """ %(locals())

    def transform(self, node, results):
        #for k,v in sorted(results.items()):
        #    print('result[%s] ==='%k, repr(v))
        #print()
        if 'imp' in results:
            # comment out import line in case it's still used
            imp = results['imp']
            imp.set_prefix('#' + imp.get_prefix())
            return
        if 'fun' in results: # unknown name
            self.warning(node,
                         "Found string module function `%s'" % results['fun'])
            return
        if 'attr' in results: # unknown attribute
            self.warning(node,
                         "Found string module attribute `%s'" % results['attr'])
            return
        if 'arg' not in results: # one-arg join()
            # default string is space
            arg = pytree.Leaf(token.STRING, "' '")
        else:
            # string arg, pull it out of arglist
            arg = results['arg']
            arg.remove()
            if (arg.type not in (token.NAME, token.STRING, self.syms.atom) and
                (arg.type != self.syms.power or
                 arg.children[-2].type == token.DOUBLESTAR)):
                # Need to parenthesize
                arg = self.parenthesize(arg)
            if 'comma' in results: # more than one arg
                # remove comma separating args
                results['comma'].remove()
                if 'rest' in results: # not two-arg join()
                    # adjust spacing on new initial arg
                    results['rest'][0].set_prefix(arg.get_prefix())
        # replace 'string' with string arg
        mod = results['mod']
        arg.set_prefix(mod.get_prefix())
        mod.replace(arg)
