##
# Add a   target to generate  text  files by  substituting environment
# variables into its input.
#
# Example:
#
# =================== BEGIN config.h.in ===================
# /* Package name */
# #define PACKAGE "%(PACKAGE)s"
#
# /* Define if stdint.h is present. */
# %(HAVE_STDINT_H)s
# ==================== END config.h.in ====================
#
# ================ BEGIN SConscript snippet ===============
# import sconstools.subst
# sconstools.subst.register (env)
#
# env["PACKAGE"] = "foo"
# if haveStdintH:
#     env.Defined ("HAVE_STDINT_H")
# else:
#     env.Undefined ("HAVE_STDINT_H")
#
# env.Subst ("config.h", "config.h.in")
# ================= END SConscript snippet ================
import re
import sconstools as tools

## Builder function
def __build (env, target, source):
    input = file (str (source[0]), "r")
    output = file (str (target[0]), "w")
    dict = env.Dictionary()
    for l in input.readlines():
        output.write (l % dict)
    input.close()
    output.close()

## Emitter function (will register the dependencies)
def __emit (target, source, env):
    for src in source:
        values = set()
        for match in re.findall (r"%\((\w+)\)", src.get_contents()):
            for tgt in target:
                env.Depends (tgt, env.Value (env[match]))
    return (target, source)

## Wrapper class for "Defined" values
def __Defined (env, name, value = None):
    class Defined:
        def __init__ (self, name, value):
            self.name  = name
            self.value = value

        def __str__ (self):
            if self.value is None:
                return "#define %s" % self.name
            else:
                return "#define %s %s" % (self.name, self.value)
    env[name] = Defined (name, value)

## Wrapper class for "Undefined" values
def __Undefined (env, name):
    class Undefined:
        def __init__ (self, name):
            self.name = name

        def __str__ (self):
            return "/* #undef %s */" % self.name
    env[name] = Undefined (name)

##
# Adds the following items to a SCons environment:
# - A "Subst" builder  which will take  a "foo.in" file and convert it
#   into a  "foo" file while  performing  variable substitution on  it
#   (using the environment values for substitution variables);
# - A "Defined" function that will create an environment variable with
#   the proper substitution for a C/C++ #define statement;
# - An "Undefined" function that  will create an environment  variable
#   that might  have  been  "Defined"  under  other circumstances  but
#   isn't.
def register (env):
    # Add the Subst builder
    a = env.Action (__build, "$$SUBSTR")
    b = env.Builder (action = a,
                     src_suffix = ".in",
                     emitter = __emit,
                     single_source = True)
    env.Append (BUILDERS = { "Subst": b })
    if env["verbose"]:
        env["SUBSTR"] = tools.makeVerboseCommandString ("Setting variables in ${SOURCE.srcpath} with:",
                                                        "Subst (${TARGET}, ${SOURCE})")
    else:
        env["SUBSTR"] = tools.makeStandardCommandString ("Setting variables in ${TARGET.file}...")

    # Add the Defined and Undefined methods
    class Wrapper:
        def __init__ (self, obj, method):
            self.obj = obj
            self.method = method

        def __call__ (self, *args, **kwargs):
            self.method (self.obj, *args, **kwargs)
    env.Defined   = Wrapper (env, __Defined)
    env.Undefined = Wrapper (env, __Undefined)
