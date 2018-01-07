# -*- python -*-
"""
Textfile builder for SCons.

Generation of Textfiles from strings (and lists of strings) by itself.

    Create file 'target' which typically is a textfile.
    'source' may be any combination of strings, Nodes or list.

    Please not that any string passed to this function will be written
    to the file. Thus for naming files to be includes, use a File()
    node instead of the filename.

    'linesep' will be put between any part written and defaults to
    os.linesep.

"""

import os
import SCons
from SCons.Node.Python import Value
from SCons.Node import Node
from SCons.Util import is_List, is_String


def _action( target, source, env ):
    # prepare the line seperator
    linesep = source.pop(0)
    if linesep == None:
        linesep = os.linesep
    elif not is_String(linesep):
        if not isinstance(linesep, Value):
            raise TypeError, \
                  'unexpected type/class for LineSeperator: %s' % repr(linesep)
        else:
            linesep = linesep.get_contents()    
    # write the file
    fd = open(target[0].get_path(), "w")
    # seperate lines by 'linesep' only if linesep is not empty
    if linesep:
        lsep = ''
        for s in source:
            fd.writelines( (lsep, s.get_contents()) )
            lsep = linesep
    else:
        for s in source:
            fd.write(s.get_contents())
    fd.close()


def _strfunc(target, source, env):
    return "Creating textfile '%s'" % target[0]

def _convert_list(target, source, env):

    def _convert_list_R(newlist, sources):
        for elem in sources:
            if is_List(elem):
                _convert_list_R(newlist, elem)
            elif not isinstance(elem, Node):
                newlist.append(Value(elem))
            else:
                newlist.append(elem)

    newlist = [env['LINESEPERATOR']]
    _convert_list_R(newlist, source)
    return target, newlist


_builder = SCons.Builder.Builder(
    action = SCons.Action.Action(_action, _strfunc),
    source_factory = Value,
    emitter = _convert_list,
    suffix = '$TEXTFILESUFFIX',
    )

def generate(env):
    env['BUILDERS']['Textfile'] = _builder
    env['LINESEPERATOR'] = os.linesep
    env['TEXTFILESUFFIX'] = '.txt'

def exists(env):
    return 1

 	  	 
