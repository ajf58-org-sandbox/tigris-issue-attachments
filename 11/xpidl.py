#!/usr/bin/python
"""
Tool-specific initialization for for Mozilla's XPIDL compiler:
    env.XPCOMInterface('iTransString.idl', 
        XPIDLMODE=['header', 'doc', 'java', 'typelib'])
"""
import sys
import string

import SCons.Defaults
import SCons.Scanner.IDL
import SCons.Util

suffixes = {'header': '.h', 'typelib':'.xpt', 'doc':'.html', 'java':'.java'}

def xpidl_emitter(target, source, env):
    '''Can only do one source a time cause scons won't generate multi-tagets.'''
    ntarget = []
    mode = env['XPIDLMODE']
    base, ext = SCons.Util.splitext(str(target[0]))
    for m in range(len(mode)):
        ntarget.append(base + suffixes[mode[m]])
    return ntarget, source

idl_scanner = SCons.Scanner.IDL.IDLScan()

def xpidl_generator(source, target, env, for_signature):
    actions = []
    mode = env['XPIDLMODE']
    # Why scons doesn't do this for me?
    incflag = env.subst('$_XPIDLINCFLAGS')
    s0 = source[0]
    base, ext = SCons.Util.splitext(str(s0))
    for m in range(len(mode)):
        actions.append(string.join(['$XPIDL', incflag, '$XPIDLFLAGS', 
            '-m', mode[m], '-o', '${TARGET.base}', str(s0)], ' '))
    return actions

xpidl_builder = SCons.Builder.Builder(generator=xpidl_generator,
                src_suffix = '.idl',
                suffix = '.xpt',
                emitter = '$XPIDL_EMITTER',
                scanner = idl_scanner)

def generate(env):
    '''Generate XPCOMInterface builder.'''
    '''Parameters: 
        XPIDL:          xpidl compiler
        XPIDLFLAG:      command line flags
        XPIDLPATH:      include file path
        XPIDMODE:       output mode, -m [heard, typelib, doc, java]
    '''
    env['XPIDL'] = 'xpidl'
    env['XPIDLFLAGS'] = SCons.Util.CLVar('')
    env['XPIDLMODE'] = SCons.Util.CLVar('')

    # Add mozilla tool pathes.
    if sys.platform == 'win32':
        # FIXME: win32 users please fill this part.
        env['XPIDLPATH'] = SCons.Util.CLVar(env.Dir([]))
    else:
        env['XPIDLPATH'] = SCons.Util.CLVar(env.Dir(['/usr/share/idl/mozilla']))
        env['ENV']['PATH'] = SCons.Util.AppendPath(env['ENV']['PATH'], 
            '/usr/lib/mozilla')

    env['_XPIDLINCFLAGS'] = SCons.Util.CLVar('$( ${_concat(INCPREFIX, XPIDLPATH, INCSUFFIX, __env__, RDirs)} $)')

    env['BUILDERS']['XPCOMInterface'] = xpidl_builder
    env['XPIDL_EMITTER'] = xpidl_emitter

def exists(env):
    return env.Detect('xpidl')

# vim:ts=8:sw=4:expandtab

