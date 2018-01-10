"""
1. step: Create a shared library with unresolved externals
   Store the result at dedicated place
2. step: Create the shared library. "Special versions" of cyclic dependents
   must be used for link step.
   
Additional Variable "DEFAULTPATHES" is used when linking executables too
(Added to LINKFLAGS).
"""

def setup_link(self, env):
   """
   Define the shared library creation
   
   """
   # Enable automatic loading of referenced shared libraries:
   # Do not record any link time paths.
   env.Append(LINKFLAGS=["-Wl,+nodefaultrpath"])
   # Set default library search pathes /usr/lib
   env.Replace(DEFAULTPATHES="/usr/lib")
   env.Append(LINKFLAGS=["-Wl,+b$DEFAULTPATHES"])
   if self._cycle_dependencies:
      if not config.shared_library_1st in env['BUILDERS']:
         # First builder creates shared libraries without cyclic dependents.
         # The builder is created like default "SharedLibrary" builder
         # but has an additional linkflag "-Wl,-ashared" peventing an error code
         # on unresolved externals.
         # The results of first builder are stored in subdirectory "code".
         self._install_1st_lib_path = "code"
         shlinkcom_name = config.shared_library_1st + "COM"
         # insert the link flag.
         env[shlinkcom_name] = env["SHLINKCOM"].replace("$SHLINKFLAGS",
                                                        "$SHLINKFLAGS -Wl,-ashared")
         env["BUILDERS"][config.shared_library_1st] = SCons.Builder.Builder(
            action = [ SCons.Defaults.SharedCheck,
                       SCons.Action.Action("$"+shlinkcom_name, "$SHLINKCOMSTR")],
            emitter = "$SHLIBEMITTER",
            prefix = '$SHLIBPREFIX',
            suffix = '$SHLIBSUFFIX',
            target_scanner = SCons.Scanner.Prog.ProgramScanner(),
            src_suffix = '$SHOBJSUFFIX',
            src_builder = 'SharedObject')
      if not config.shared_library_2nd in env['BUILDERS']:
         # all dependents are created in first step, now we can use 2. builder
         env["BUILDERS"][config.shared_library_2nd] = env["BUILDERS"]["SharedLibrary"]

