"""
1. step: Create an "Import File" for AIX command: makeC++SharedLib_r
1.a Use AIX command: CreateExportList
1.b Convert Export list to an "Import File"
2. step: Create the shared library. Using "Import File" from 1.step and
   using all "Import Files" of cyclic dependent libraries. (i.e. The libraries
   which are created in the same environment)
   We do this using the function __append_library which defines all "cyclic dependents"
   as "IMPORTFILES".
"""



def _setup_link(env, bitsflag, cycle_dependencies):
   """
   Define the setting of the shared library creation.

   env:                 SCons construction environment
   bitsflag:            String containing bits model.
   cycle_dependencies:  Boolean, indication cylic dependencies.
                        True:  Shared libraries are created in 2 steps.
                        False: Shared library is created in 1 step.
   """
   return_path = False
   # common link flags
   env.Replace(LINKFLAGS="-qtwolink -bbigtoc".split())
   env.Append(LINKFLAGS=bitsflag.split())

   if env["shared"]:
      # enable run time loading of shared libraries
      env.Append(LINKFLAGS=["-brtl"])
      # define bits model
      env.AppendUnique(SHLINKFLAGS=bitsflag.split())
      if cycle_dependencies:
         # shared library is created in 2 steps:
         # 1. Step: Creation of an import list file of this library
         # 2. Step: Creation of shared library using
         #          libraries of externals.
         #          import files of this product.
         
         # results of first builder are stored in "build" folder
         return_path = True
         # Extension of import file
         env[__sh_expsuffix_name__] = ".exp"
         # Define 1. Builder:
         if not config.shared_library_1st in env['BUILDERS']:
            # Define Action: Creation of an export list file from object files.
            shlinkcom_name = config.shared_library_1st + "COM"
            env[shlinkcom_name] = "CreateExportList -e $TARGET $SOURCES -X$mode"
            create_export_action = SCons.Action.Action("$" + shlinkcom_name)
            # Define Action: Change export list file to an Import files.
            create_import_action = SCons.Action.Action(
               __create_import_from_export,
               "Change $TARGET to import file.")
            # Define the builder and add to "BUILDERS".
            env["BUILDERS"][config.shared_library_1st] = SCons.Builder.Builder(
               action=[create_export_action,
                       create_import_action],
               prefix="$LIBPREFIX",
               suffix="$" + __sh_expsuffix_name__,
               #Scan for dependency of libraries
               target_scanner = SCons.Scanner.Prog.ProgramScanner(),
               src_suffix="$SHOBJSUFFIX",
               src_builder="SharedObject")

         # Define 2. Builder:
         if not config.shared_library_2nd in env['BUILDERS']:
            # Create shared library using "makeC++SharedLib_r".
            shlinkcom_name = config.shared_library_2nd + "COM"
            shlinkcom_flags = config.shared_library_2nd + "FLAGS"
            env[shlinkcom_flags] = [flag for flag in env.subst("$SHLINKFLAGS").split()
                                    if flag.startswith("-b") and flag != "-brtl"] + \
                                   ["-blibpath:/lib:/usr/lib"]
            env[shlinkcom_name] = "makeC++SharedLib_r -p10" \
                                  " -E${TARGET.base}$" + __sh_expsuffix_name__ +\
                                  " $_LIBDIRFLAGS $_LIBFLAGS" \
                                  " $" + shlinkcom_flags + \
                                  " ${_concat('-I', IMPORTFILES, '', __env__)}" \
                                  " -X $mode" \
                                  " -o $TARGET $SOURCES"
            env["BUILDERS"][config.shared_library_2nd] = SCons.Builder.Builder(
               emitter=__lib_source_exp_emitter,
               action=[SCons.Action.Action("$" + shlinkcom_name)],
               prefix="$LIBPREFIX",
               suffix="$SHLIBSUFFIX",
               #Scan for dependency of libraries
               target_scanner=SCons.Scanner.Prog.ProgramScanner(),
               src_prefix="$LIBPREFIX",
               src_suffix=__sh_expsuffix_name__)
            # Let library.library use __append_library to add libraries to env.
            env[config.shared_library_import] = __append_library


def __lib_source_exp_emitter(target, source, env):
   """
   SCons "emitter", adding import list files to emitted objects.

   target:        list of SCons nodes of buld targets.
   source:        list of Scons nodes of source files.
   env:           Scons construction environment
   """

   found_extensions = env.FindIxes(target, "LIBPREFIX", "SHLIBSUFFIX")

   if found_extensions:
      source.append(env.ReplaceIxes(found_extensions, 
                                    "SHLIBPREFIX", "SHLIBSUFFIX",
                                    "LIBPREFIX", __sh_expsuffix_name__))

   # Let target depend on "IMPORTFILES"
   for importfile in env.Dictionary().get("IMPORTFILES", []):
      env.Depends(target[0], importfile)

   return (target, source)


def __create_import_from_export(target = None, source = None, env = None):
   """
   SCons "action", creating an import file from an export file.

   target:        list of SCons nodes of buld targets.
   source:        list of Scons nodes of source files.
   env:           Scons construction environment
   """
   # The parameters are requested by SCons.Action.Action
   # but env is not used. =>
   # pylint: disable-msg=I0011,W0613

   file_p = open(str(target[0]), "r")
   in_lines = file_p.readlines()
   file_p.close()

   first_line = "#!" + os.path.splitext(
      os.path.basename(str(target[0])))[0] + env.subst("$SHLIBSUFFIX") + os.linesep
   file_p = open(str(target[0]), "w")
   file_p.write(first_line)
   for line in in_lines:
      # Do not export fortran's symbol "block data"
      if not line.startswith("(block"):
         file_p.write(line)
   file_p.close()

   return 0


def __append_library(library_path, library_name, env):
   """
   Append a library to "LIBS" or as "importfile" to "IMPORTFILES".

   library_path:  path of library.
   library_name:  name of library.
   env:           Scons construction environment
   """
   if library_path == env["install_lib_path"]: # Here we recognize libraries which are created in this environment
      # support of "#" in "install_lib_path"
      env.AppendUnique(IMPORTFILES=[str(env.File(os.path.join(
         library_path, env.subst("$LIBPREFIX") + library_name + env[__sh_expsuffix_name__])))])
   else:
      env.AppendUnique(LIBS=[library_name])
