import SCons.Builder
import SCons.Util

CPreProcessorBuilder = SCons.Builder.Builder(
	action = '$CPPCOM',
	prefix = '$CPPPREFIX',
	suffix = '$CPPSUFFIX')

def generate(env):
	env['CPP'] = '$CC -E'
	env['CPPCOM'] = '$CPP $CCFLAGS $CPPFLAGS $_CPPDEFFLAGS $_CPPINCFLAGS $SOURCES > $TARGET'
	env['CPPPREFIX'] = ''
	env['CPPSUFFIX'] = '.i'
	env['BUILDERS']['CPreProcessor'] = CPreProcessorBuilder

def exists(env):
	return env.Detect('$CC')
