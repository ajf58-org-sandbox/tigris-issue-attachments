# Cope with scons's failure to set SONAME in its builtins.
# Inspired by Richard Levitte's (slightly buggy) code at
# http://markmail.org/​message/spttz3o4xrsf​tofr

def VersionedSharedLibrary(env, libname, libversion, lib_objs=[], parse_flags=[]):
    platform = env.subst('$PLATFORM')
    shlib_pre_action = None
    shlib_suffix = env.subst('$SHLIBSUFFIX')
    shlib_post_action = None
    shlink_flags = SCons.Util.CLVar(env​.subst('$SHLINKFLAG​S'))

    if platform == 'posix':
        shlib_post_action = ['rm -f $TARGET','ln -s ${SOURCE.file} $TARGET']
        shlib_post_action_output_re = [
            '%s\\.[0-9\\.]*$' % re.escape(shlib_suffix),
            shlib_suffix ]
        shlib_suffix += '.' + libversion
        (major, age, revision) = libversion.split(".")
        soname = libname + "." + major
        shlink_flags += [ '-Wl,-Bsymbolic', '-Wl,-soname=%s' % soname ]
    elif platform == 'aix':
        shlib_pre_action = [
            "nm -Pg $SOURCES &gt; ${TARGET}.tmp1",
            "grep ' [BDT] ' &lt; ${TARGET}.tmp1 &gt; ${TARGET}.tmp2",
            "cut -f1 -d' ' &lt; ${TARGET}.tmp2 &gt; ${TARGET}",
            "rm -f ${TARGET}.tmp[12]" ]
        shlib_pre_action_output_re = [ '$', '.exp' ]
        shlib_post_action = [ 'rm -f $TARGET', 'ln -s $SOURCE $TARGET' ]
        shlib_post_action_output_re = [
            '%s\\.[0-9\\.]*' % re.escape(shlib_suffix),
            shlib_suffix ]
        shlib_suffix += '.' + libversion
        shlink_flags += ['-G', '-bE:${TARGET}.exp', '-bM:SRE']
    elif platform == 'cygwin':
        shlink_flags += [ '-Wl,-Bsymbolic',
                          '-Wl,--out-implib,$​{TARGET.base}.a' ]
    elif platform == 'darwin':
        shlib_suffix = '.' + libversion + shlib_suffix
        shlink_flags += [ '-current_version', '%s' % libversion,
                          '-undefined', 'dynamic_lookup' ]

    lib = env.SharedLibrary(li​bname,lib_objs,
                            SHLIBSUFFIX=shlib_suffix,
                            SHLINKFLAGS=shlink_flags, parse_flags=parse_flags)

    if shlib_pre_action:
        shlib_pre_action_output = re.sub(shlib_pre_act​ion_output_re[0],
                                         shlib_pre_action_output_re[1],
                                         str(lib[0]))
        env.Command(shlib_pr​e_action_output, [ lib_objs ],
                     shlib_pre_action)
        env.Depends(lib, shlib_pre_action_output)
    if shlib_post_action:
        shlib_post_action_output = re.sub(shlib_post_ac​tion_output_re[0],
                                          shlib_post_action_output_re[1],
                                          str(lib[0]))
        env.Command(shlib_po​st_action_output, lib, shlib_post_action)
    return lib

def InstallVersionedShar​edLibrary(env, destination, lib):
    platform = env.subst('$PLATFORM')
    shlib_suffix = env.subst('$SHLIBSUFFIX')
    shlib_install_pre_action = None
    shlib_install_post_action = None

    if platform == 'posix':
        shlib_post_action = [ 'rm -f $TARGET',
                              'ln -s ${SOURCE.file} $TARGET' ]
        shlib_post_action_output_re = ['%s\\.[0-9\\.]*$' % re.escape(shlib_suffix),
                                       shlib_suffix ]
        shlib_install_post_action = shlib_post_action
        shlib_install_post_a​ction_output_re = shlib_post_action_output_re

    ilib = env.Install(destination, lib)

    if shlib_install_pre_action:
        shlib_install_pre_action_output = re.sub(shlib_install​_pre_action_output_r​e[0],
                                                 shlib_install_pre_ac​tion_output_re[1],
                                                 str(ilib[0]))
        env.Command(shlib_in​stall_pre_action_out​put, ilib,
                    shlib_install_pre_action)
        env.Depends(shlib_in​stall_pre_action_out​put, ilib)

    if shlib_install_post_action:
        shlib_install_post_a​ction_output = re.sub(shlib_install​_post_action_output_​re[0],
                                                  shlib_install_post_a​ction_output_re[1],
                                                  str(ilib[0]))
        env.Command(shlib_in​stall_post_action_ou​tput, ilib,
                    shlib_install_post_action)
    return ilib


