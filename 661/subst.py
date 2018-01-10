# File:         subst.py
# Author:       Brian A. Vanderburg II
# Purpose:      SCons file substitution mechanism
# Copyright:    This file is placed in the public domain.
##############################################################################


# Requirements
##############################################################################
import re

from SCons.Script import *
import SCons.Errors


# For any part that matches a pattern, a replace function will be
# called passing the environment and the match object, and it will
# return the correct replacement.  The pattern must have a parameter
# named "key" to be used for tracking which environment keys a target
# is dependent on
##############################################################################

def _subst_file(target, source, env, pattern, replace):
    # Read file
    f = open(source, "rU")
    try:
        contents = f.read()
    finally:
        f.close()

    # Substitute, make sure the result is a string, not integer or float
    def subfn(mo):
        return str(replace(env, mo))

    contents = re.sub(pattern, subfn, contents)

    # Write file
    f = open(target, "wt")
    try:
        f.write(contents)
    finally:
        f.close()

def _subst_keys(source, pattern):
    # Read file
    f = open(source, "rU")
    try:
        contents = f.read()
    finally:
        f.close()

    # Determine keys
    keys = []
    def subfn(mo):
        key = mo.group("key")
        if key:
            keys.append(key)
        return ''

    re.sub(pattern, subfn, contents)

    return keys


# Builder related functions
##############################################################################

def _subst_in_file(target, source, env):
    # Substitute in the files
    pattern = env["SUBST_PATTERN"]
    replace = env["SUBST_REPLACE"]

    for (t, s) in zip(target, source):
        _subst_file(str(t), str(s), env, pattern, replace)

    return 0

def _subst_string(target, source, env):
    items = ["Substituting vars from %s to %s" % (str(s), str(t))
             for (t, s) in zip(target, source)]

    return "\n".join(items)

def _subst_emitter(target, source, env):
    pattern = env["SUBST_PATTERN"]
    for (t, s) in zip(target, source):
        # Get keys used
        keys = _subst_keys(str(s), pattern)

        d = dict()
        for key in keys:
            # Why can't we do "if key in env" without getting "KeyError: 0:"
            try:
                env[key]
            except KeyError:
                continue

            d[key] = env.subst("${%s}" % key)

        # Only the current target depends on this dictionary
        Depends(t, SCons.Node.Python.Value(d))

    return target, source


# Replace @key@ with the value of that key, and @@ with a single @
##############################################################################

_SubstFile_pattern = "@(?P<key>\w*?)@"
def _SubstFile_replace(env, mo):
    key = mo.group("key")
    if not key:
        return "@"
    return env.subst("${%s}" % key)
    
def SubstFile(env, target, source):
    return env.SubstGeneric(target,
                            source,
                            SUBST_PATTERN=_SubstFile_pattern,
                            SUBST_REPLACE=_SubstFile_replace)


# A substitutor similar to config.h header substitution
# Supported patterns are:
#
# Pattern: #define @key@
# Found:   #define key value
# Missing: /* #define key */
#
# Pattern: #define @key@ default
# Found:   #define key value
# Missing: #define key default
#
# Pattern: #undef @key@
# Found:   #define key value
# Missing: #undef key
#
# The "@" is used to that these defines can be used in addition to
# other defines that you do not desire to be replaced.
##############################################################################

_SubstHeader_pattern = "(?m)^(?P<space>\\s*?)(?P<type>#define|#undef)\\s+@(?P<key>\w+?)@(?P<ending>.*?)$"
def _SubstHeader_replace(env, mo):
    space = mo.group("space")
    type = mo.group("type")
    key = mo.group("key")
    ending = mo.group("ending")

    try:
        # why doesn't "if key in env" work?
        env[key]
    except KeyError:
        # Not found
        if type == "#define":
            if ending.strip():
                # There is a default value
                if ending[0] != " " and ending[0] != "\t":
                    ending = " %s" % ending
                return "%s#define %s%s" % (space, key, ending)
            else:
                # There is no default value
                return "%s/* #define %s */" % (space, key)

        # It was #undef
        return "%s#undef %s" % (space, key)
        
    # If found it is always #define key value
    value = env.subst("${%s}" % key)
    return "%s#define %s %s" % (space, key, value)

def SubstHeader(env, target, source):
    return env.SubstGeneric(target,
                            source,
                            SUBST_PATTERN=_SubstHeader_pattern,
                            SUBST_REPLACE=_SubstHeader_replace)


# Create builders
##############################################################################
def TOOL_SUBST(env):
    # The generic builder
    subst_in_file_action = SCons.Action.Action(_subst_in_file, _subst_string)
    env['BUILDERS']['SubstGeneric'] = Builder(action=subst_in_file_action,
                                              emitter=_subst_emitter)

    # Additional ones
    env.AddMethod(SubstFile)
    env.AddMethod(SubstHeader)


