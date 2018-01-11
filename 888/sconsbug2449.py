#!python
# Author: Thomas Berg <merlin66b@gmail.com>
# License: BSD

import os
import shutil

# For this script to run, scons must be installed (http://www.scons.org),
# and Microsoft VS2008.
# Purpose of this program: Generate all files needed for a C++ build, compile
# it with scons, and demonstrate a crash in python.exe on Windows.
# For a description of the problem, see:
# http://old.nabble.com/SCons-Python-crashing-on-Windows---dereferencing-NULL-td22576049.html
#
# The crash happens more or less frequently, depending on which machine
# you run it on, so it may need to run a few times before you get a crash
# (or you may not get it at all).

#==========================================================================
# Template for the SConscript file
sconscript = """
#!python

import os
import glob

tools = ['mslink', 'msvc', 'mslib', 'msvs', 'install']
# We use VS2008 (9.0), but other versions might work too
env = Environment(tools = tools, MSVC_VERSION = '9.0')

# Enable tempfile munging for CXXCOM:
env['CXXCOM'] = '${TEMPFILE("$CXX $_MSVC_OUTPUT_FLAG /c $CHANGED_SOURCES $CXXFLAGS $CCFLAGS $_CCCOMCOM")}'
# Lower the threshold for when the tempfile munging is triggered:
env['MAXLINELENGTH'] = 5

# Some random C++ compiler flags
env.AppendUnique(CCFLAGS = ['/EHsc'])
env.AppendUnique(CCFLAGS = ['/Zc:forScope'])
env.AppendUnique(CCFLAGS = ['/GR'])
env.AppendUnique(CCFLAGS = ['/GF'])
env.AppendUnique(CCFLAGS = ['/FC'])
env.AppendUnique(CCFLAGS = ['/fp:precise'])
env.AppendUnique(CCFLAGS = ['/Oxityb2'])
env.AppendUnique(CCFLAGS = ['/MD'])
env.AppendUnique(LINKFLAGS = ['/SUBSYSTEM:CONSOLE'])

no_programs = %(no_programs)s
programs = ['program_%%s_' %% i for i in range(0, no_programs)]

abspath = env.Dir('.').srcnode().abspath

for p in programs:
    src = glob.glob(os.path.join(abspath, '%%s*.cpp' %% p))
    name = p[:-1]
    program = env.Program(name, src)
    env.Default(program)
"""
#==========================================================================

def main():
    no_programs = 1000
    files_per_program = 15
    jobs = 24 # Note from author: I have 6 cores with hyperthreading, so 12 virtual cores. -j24 triggered the crash at least.

    programs = ['program_%s_' % i for i in range(0, no_programs)]

    runs = 10
    for i in range(0, runs):
        # Clear generated stuff from previous runs
        if os.path.exists('sconstestcase'):
            shutil.rmtree('sconstestcase')
        os.makedirs('sconstestcase')

        # Generate a SConstruct file
        with open('sconstestcase/SConstruct', 'w') as f:
            f.write(sconscript % dict(no_programs = no_programs))

        # Generate a bunch of files to be grouped into programs
        for program in programs:
            # A few numbered files specific for each program
            for i in range(0, files_per_program):
                with open('sconstestcase/%s%s.cpp' % (program, i), 'w') as f:
                    # Include some C++ headers to slow down the compilation a bit
                    f.write('#include <iostream>\n')
                    f.write('#include <string>\n')
                    f.write('#include <vector>\n')
                    f.write('#include <algorithm>\n')
                    f.write('int test%s() { int a = 0; a += %s; return a;}\n' % (i, i))
            # Create the main file for the program
            with open('sconstestcase/%smain.cpp' % program, 'w') as f:
                for i in range(0, files_per_program):
                    f.write('int test%s();\n' % i);
                f.write('int main(int argc, char* argv[]){\n    int sum = 0;')
                for i in range(0, files_per_program):
                    f.write('    sum += test%s();\n' % i)
                f.write('    return sum;\n}\n')

        os.system('cd sconstestcase && scons.bat -j%s' % jobs)

if __name__ == '__main__':
    main()
