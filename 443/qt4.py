"""SCons.Tool.qt4

Tool-specific initialization for customised set of
default tools with qt. This has some updates for Qt4
to add support for things like the resource compiler.

"""

import os.path
import re

import SCons.Action
import SCons.Builder
import SCons.Scanner
import SCons.Util

def rccScannerFunc(node, env, path):
    lookout = []
    lookout.append(str(node.rfile().dir))
    includes = re.findall("<file.*?>(.*?)</file>", node.get_contents())
    result = []
    for incFile in includes:
        dep = env.FindFile(incFile,lookout)
        if dep:
            result.append(dep)
    return result

rccScanner = SCons.Scanner.Base(rccScannerFunc,
                                name = "RccScanner",
                                node_class = SCons.Node.FS.File,
                                node_factory = SCons.Node.FS.File,
                                recursive = 0)

def generate(env):

    import SCons.Tool

    # The library names on Windows are different to unix.
    # On Windows, all library names have a trailing "4"
    # for Qt4, whereas this version number is embedded in
    # the trailing library version number for shared libraries
    # under unix. Therefore, we have to name the libraries
    # differently, since the base name is different.

    import sys
    if sys.platform == 'win32':
        if env['debug']:
            qtlibsuffix = 'd4'
        else:
            qtlibsuffix = '4'
    else:
        qtlibsuffix = ''

    env.Replace(QtCore     = 'QtCore'     + qtlibsuffix)
    env.Replace(QtDesigner = 'QtDesigner' + qtlibsuffix)
    env.Replace(QtGui      = 'QtGui'      + qtlibsuffix)
    env.Replace(QtNetwork  = 'QtNetwork'  + qtlibsuffix)
    env.Replace(QtOpenGL   = 'QtOpenGL'   + qtlibsuffix)
    env.Replace(QtSql      = 'QtSql'      + qtlibsuffix)
    env.Replace(QtSvg      = 'QtSvg'      + qtlibsuffix)
    env.Replace(QtTest     = 'QtTest'     + qtlibsuffix)
    env.Replace(QtXml      = 'QtXml'      + qtlibsuffix)

    # Get the default Qt stuff from SCons
    env.Tool('qt')

    # Add some basic support for resource files
    env.SetDefault(QT_RCC = os.path.join('$QT_BINPATH','rcc'),

                   # suffixes/prefixes for the target(s)
                   QT_RCCSRCPREFIX = 'rcc_',
                   QT_RCCSRCSUFFIX = '$CXXFILESUFFIX',
                   QT_RCCBINPREFIX = '',
                   QT_RCCBINSUFFIX = '.rcc',

                   # command to generate target(s) from a .qrc file
                   QT_RCCSRCCOM = [
                    SCons.Util.CLVar('$QT_RCC -o $TARGET $SOURCE')],
                   QT_RCCBINCOM = [
                    SCons.Util.CLVar('$QT_RCC -binary -o $TARGET $SOURCE')])

    # ... and the corresponding builders
    rccSrcBld = SCons.Builder.Builder(action=SCons.Action.Action('$QT_RCCSRCCOM', '$QT_RCCSRCCOMSTR'),
                                      src_suffix='.qrc',
                                      suffix='$QT_RCCSRCSUFFIX',
                                      prefix='$QT_RCCSRCPREFIX',
                                      source_scanner=rccScanner)
    rccBinBld = SCons.Builder.Builder(action=SCons.Action.Action('$QT_RCCBINCOM', '$QT_RCCBINCOMSTR'),
                                      src_suffix='.qrc',
                                      suffix='$QT_RCCBINSUFFIX',
                                      prefix='$QT_RCCBINPREFIX',
                                      source_scanner=rccScanner)

    # register the builders
    env['BUILDERS']['RccSrc'] = rccSrcBld
    env['BUILDERS']['RccBin'] = rccBinBld

    # Add some stuff to the C++ include path
    env.AppendUnique(CPPPATH = ['$QTDIR/include/QtCore'])

    # To make the Q_INTERFACES() macro work with moc, we need
    # the CPPPATH contents to be included. However, moc uses
    # -I on all platforms, whereas _CPPINCPATH uses /I under
    # Windows and -I under unix. Therefore, we have to construct
    # our own set of include flags.
    env['_MOCINCFLAGS'] = '$( ${_concat("-I", CPPPATH, None, __env__, RDirs)} $)'
    env.AppendUnique(QT_MOCFROMHFLAGS = ['$_MOCINCFLAGS'])

    # The following is not needed for Qt4 (was for Qt3)
    #env.AppendUnique(CPPDEFINES = ['QT_THREAD_SUPPORT'])

    env.Replace(QT_LIB = '$QtCore')

