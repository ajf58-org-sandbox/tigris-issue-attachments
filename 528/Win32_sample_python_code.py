def _shared_library_in_2steps(env):
   """
   Setup of creation of shared libraries in 2 Steps.

   env:
      The scons Environment

   builder config.shared_library_1st: Builds an import library and export file.
      Construction Variables:
      config.shared_library_1st + "COM"
         The lib command line.
      config.shared_library_1st + "EMITTER"
         The SCons "emitter" of this builder.

   builder config.shared_library_2nd: Links a MS shared library (DLL).
      Construction Variables:
      config.shared_library_2nd + "EMITTER"
         The emitter of this builder.
   """

   if not config.shared_library_1st in env['BUILDERS']:
      # The 1st builder
      shlinkcom_name = config.shared_library_1st + "COM"
      env[shlinkcom_name] = "${TEMPFILE('$AR /DEF $ARFLAGS /OUT:$TARGET $SOURCES')}"
      ar_action = SCons.Action.Action("$" + shlinkcom_name, "building '$TARGET' from '$SOURCE'")
      emitter_name = config.shared_library_1st + "EMITTER"
      env[emitter_name] = [__lib_export_emitter]
      env["BUILDERS"][config.shared_library_1st] = SCons.Builder.Builder(
         action=ar_action,
         emitter="$" + emitter_name,
         prefix="$LIBPREFIX",
         suffix="$LIBSUFFIX",
         src_suffix="$SHOBJSUFFIX",
         src_builder="SharedObject")

   if not config.shared_library_2nd in env['BUILDERS']:
      # The 2nd builder
      emitter_name = config.shared_library_2nd + "EMITTER"
      env[emitter_name] = [__win32_lib_emitter]
      env["BUILDERS"][config.shared_library_2nd] = SCons.Builder.Builder(
         action=[SCons.Defaults.SharedCheck,
                 SCons.Action.Action("$SHLINKCOM", "building '$TARGET' from '$SOURCE'")],
         emitter="$" + emitter_name,
         prefix="$SHLIBPREFIX",
         suffix="$SHLIBSUFFIX",
         target_scanner=SCons.Scanner.Prog.ProgramScanner(),
         src_suffix="$SHOBJSUFFIX",
         src_builder="SharedObject")
