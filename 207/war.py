"""SCons.Tool.war

Tool-specific initialization for zip.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

#
# Copyright (c) 2001, 2002, 2003, 2004 The SCons Foundation
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = ""

import os.path

import SCons.Builder
import SCons.Node.FS
from SCons.Node.FS import _my_normcase,Dir,File
import SCons.Util
import fnmatch

try:
    import zipfile
    internal_zip = 1
except ImportError:
    internal_zip = 0

zipcompression = zipfile.ZIP_DEFLATED
def warMessage(target, source, env):
    return 'Building WAR file: '+str(target[0])+' ...'
def zip(target, source, env):
    
    xfiles=env['WARXFILES']
    xdirs=env['WARXDIRS']
    compression = env.get('WARCOMPRESSION', 0)
    zf = zipfile.ZipFile(str(target[0]), 'w', compression)
    for s in source:
       if isinstance(s,Dir):
          sdir=s.rdir().get_abspath()
          for root, dirs, names  in os.walk(sdir):
             if xdirs:
                map(lambda r, dirs=dirs: dirs.remove(r), filter(lambda f, xdirs=xdirs: f in xdirs, dirs))
             if xfiles:
                map(lambda r, names=names: names.remove(r), filter(lambda f, xfiles=xfiles: f in xfiles, names))
                map(lambda r, names=names: names.remove(r), filter(lambda f, xfiles=xfiles: fnmatch.fnmatchcase(f,'*.jar'), names))
             for name in names:
                file=os.path.join(root,name)
                zf.write(file,file.replace(sdir+os.sep,''))
       if isinstance(s,File):
           file=str(s)
           pos=file.rfind('classes')
           if pos == -1:
               basename=os.path.basename(file)
               zf.write(file,basename)
           else:
               zf.write(file,os.path.join('WEB-INF',file[pos:]))
    #copy all .jar files from JAVACLASSPATH to WEB-INF/lib
    if env.has_key('JAVACLASSPATH') and env['JAVACLASSPATH']:
       for jarfile in env['JAVACLASSPATH']:
          basename=os.path.basename(jarfile)
          zf.write(jarfile,os.path.join('WEB-INF','lib',basename))
    if env.has_key('JAPPLETS') and env['JAPPLETS']:
       for jarfile in env['JAPPLETS']:
          basename=os.path.basename(jarfile)
          zf.write(jarfile,os.path.join('applets',basename))
    zf.close()

warAction = SCons.Action.Action(zip, strfunction=warMessage, varlist=['WARCOMPRESSION'])

WarBuilder = SCons.Builder.Builder(action = '$WARCOM',
                                   source_factory = SCons.Node.FS.default_fs.Entry,
                                   suffix = '$WARSUFFIX')


def generate(env):
    """Add Builders and construction variables for zip to an Environment."""
    try:
        bld = env['BUILDERS']['War']
    except KeyError:
        bld = WarBuilder
        env['BUILDERS']['War'] = bld
    env['WARFLAGS']   = SCons.Util.CLVar('')
    env['WARCOM']     = warAction
    env['WARCOMPRESSION'] =  zipcompression
    env['WARSUFFIX']  = '.war'
    env['WARXFILES'] = None
    env['WARXDIRS'] = None

def exists(env):
    return internal_zip or env.Detect('zip')
