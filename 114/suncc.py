import cc
import os
import SCons.Util

def get_cc(env):
    ccVersion = None

    pkginfo = 'pkginfo'
    pkgchk = 'pkgchk'

    for package in ['SPROcc']:
        cmd = "%s -l %s 2>/dev/null | grep '^ *VERSION:'" % (pkginfo, package)
        line = os.popen(cmd).readline()
        if line:
            ccVersion = line.split()[-1]
            cmd = "%s -l %s 2>/dev/null | grep '^Pathname:.*/bin/cc$' | grep -v '/SC[0-9]*\.[0-9]*/'" % (pkgchk, package)
            line = os.popen(cmd).readline()
            ccPath = os.path.dirname(line.split()[-1])
            break
    return (ccPath, 'cc', 'cc', ccVersion)

def generate(env):
    """
    Add Builders and construction variables for Forte C and C++ compilers
    to an Environment.
    """
    path,ccc,shcc,version=get_cc(env)
    if path:
        ccc = os.path.join(path,ccc)
        shcc = os.path.join(path,shcc)
    cc.generate(env)

    env['CC']        = ccc
    env['SHCC']      = shcc
    env['CCVERSION'] = version
    env['SHCCFLAGS'] = SCons.Util.CLVar('$CCFLAGS -KPIC')
    env['SHOBJPREFIX'] = 'so_'
    env['SHOBJSUFFIX'] = '.o'

def exists(env):
    path,ccc,shcc,version=get_cc(env)
    if path and ccc:
        ccc = os.path.join(path,ccc)
        if os.path.exists(ccc): return ccc
    return None
