"""
1. step: Create a shared library with flag "-h" and put result at special place.
2. step: Create the shared library. "Special versions" of cyclic dependents
   must be used for link step.
   
Very import flag "-norunpath" which prevents storage of library pathes.
Also settings of linker are changed.
"""

   def setup_link(self, env):
      """
      Define the shared library creation
      
      """
      if env["shared"]:
         if self._cycle_dependencies:
            # results of first builder are stored in subdirectory "code"
            self._install_1st_lib_path = "code"

            if not config.shared_library_1st in env['BUILDERS']:
               shlinkflags_name = config.shared_library_1st + "FLAGS"
               env[shlinkflags_name] = (
                  "-Qoption ld -zmuldefs -norunpath "
                  "-R /usr/lib:/opt/SUNWspro/lib -Qoption ld -znodefs").split()
               shlinkcom_name = config.shared_library_1st + "COM"
               env[shlinkcom_name] = \
                  "$SHLINK -G -h${TARGET.file} $" + shlinkflags_name + \
                  " $SOURCES -o $TARGET $_LIBDIRFLAGS"
               env["BUILDERS"][config.shared_library_1st] =  SCons.Builder.Builder(
                  action = [SCons.Defaults.SharedCheck, 
                            SCons.Action.Action("$" + shlinkcom_name, "$SHLINKCOMSTR") ],
                  emitter = "$SHLIBEMITTER",
                  prefix = '$SHLIBPREFIX',
                  suffix = '$SHLIBSUFFIX',
                  target_scanner = SCons.Scanner.Prog.ProgramScanner(),
                  src_suffix = '$SHOBJSUFFIX',
                  src_builder = 'SharedObject')

            if not config.shared_library_2nd in env['BUILDERS']:
               shlinkflags_name = config.shared_library_2nd + "FLAGS"
               env[shlinkflags_name] = \
                  "-Qoption ld -Bsymbolic,-Bdirect,-zlazyload,-znodefs".split()
               shlinkcom_name = config.shared_library_2nd + "COM"
               env[shlinkcom_name] = \
                  "CC -mt $" + shlinkflags_name + " -G -h${TARGET.file} " + \
                  "-Qoption ld -zmuldefs -norunpath -R /usr/lib:/opt/SUNWspro/lib " + \
                  "$SOURCES -o $TARGET $_LIBDIRFLAGS $_LIBFLAGS"
               env["BUILDERS"][config.shared_library_2nd] =  SCons.Builder.Builder(
                  action = [SCons.Defaults.SharedCheck, 
                            SCons.Action.Action("$" + shlinkcom_name, "$SHLINKCOMSTR") ],
                  emitter = "$SHLIBEMITTER",
                  prefix = '$SHLIBPREFIX',
                  suffix = '$SHLIBSUFFIX',
                  target_scanner = SCons.Scanner.Prog.ProgramScanner(),
                  src_suffix = '$SHOBJSUFFIX',
                  src_builder = 'SharedObject')
            # Use -znodefs to prevent link errors to when linking with
            # libraries, which have implicit dependencies.
            env.Append(LINKFLAGS=(
               "-Qoption ld -ztext,-znodefs,-Bsymbolic,-Bdirect,-zlazyload,-zcombreloc,-zignore "
               "-norunpath").split())
         else:
            env.Replace(LINKFLAGS=(
               "-Qoption ld -ztext,-zdefs,-Bsymbolic,-Bdirect,-zlazyload,-zcombreloc,-zignore"
               " -norunpath -R /usr/lib:/opt/SUNWspro/lib").split())
         # Use env["CXX"] as linker, due to current setting of LINKFLAGS
         env["LINK"] = env["CXX"]
      else:
         env.Replace(LINKFLAGS=["-Bdynamic"])
