
# Local imports
from ..pgen2 import token
from .. import fixer_base
from ..fixer_util import Name

_TYPE_MAPPING = {
        'BooleanType' : 'bool',
        'BufferType' : 'memoryview',
        'ClassType' : 'type',
        'ComplexType' : 'complex',
        'DictType': 'dict',
        'DictionaryType' : 'dict',
        'EllipsisType' : 'type(Ellipsis)',
        #'FileType' : 'io.IOBase',
        'FloatType': 'float',
        'IntType': 'int',
        'ListType': 'list',
        'LongType': 'long',
        'ObjectType' : 'object',
        'NoneType': 'type(None)',
        'NotImplementedType' : 'type(NotImplemented)',
        'SliceType' : 'slice',
        'StringType': 'str', # XXX ?
        #'StringTypes' : 'str', # XXX ?
        'TupleType': 'tuple',
        'TypeType' : 'type',
        'UnicodeType': 'unicode',
        'XRangeType' : 'range',
    }

_pats = ["power< 'types' trailer< '.' name='%s' > >" % t for t in _TYPE_MAPPING]

_something = set()
def _type_atom(new_type, *match):
    pat = ' '.join(map(repr, match))
    _pats.append("power< 'type' trailer< '(' %s=atom< %s > ')' > >"
                        % (new_type, pat))
    _something.add(new_type)
def _type_leaf(new_type, *match):
    pat = ' '.join(map(repr, match))
    _pats.append("power< 'type' trailer< '(' %s=%s ')' > >" % (new_type, pat))
    _something.add(new_type)

_type_atom('list', '[', ']')
_type_atom('dict', '{', '}')
_type_atom('tuple', '(', ')')
_type_leaf('str', "''")
_type_leaf('str', '""')
#_pats.append("power< 'type' WHAT=any+ >")

class FixTypes1(fixer_base.BaseFix):

    explicit = True # SCons-specific; don't apply by default

    PATTERN = '|'.join(_pats)

    def transform(self, node, results):
        if "name" in results:
            new_value = _TYPE_MAPPING.get(results["name"].value)
            if new_value:
                return Name(new_value, prefix=node.get_prefix())
            return None
        for new_value in _something:
            if new_value not in results: continue
            return Name(new_value, prefix=node.get_prefix())
        #print('==========', str(node))
        #print(repr(node))
        return None
