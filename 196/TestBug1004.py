import TestSCons

# This is a test for fix of Issue 1004.

test = TestSCons.TestSCons()

test.write('SConstruct', """\
env = Environment()

mylib = env.StaticLibrary('mytest', 'test_lib.c')

myprog = env.Program('test1.c',
                     LIBPATH = ['.'],
                     LIBS = ['mytest'])
if ARGUMENTS['case']=='2':
  AddPostAction(myprog, Action('strip ' + myprog[0].abspath))
""")

test.write('test1.c', """\
extern void test_lib_fn();
int main(int argc, char **argv) {
  test_lib_fn();
  return 0;
}
""")

test.write('test_lib.c', r"""\
#include <stdio.h>

void test_lib_fn() {
  printf("Hello world\n");
}
""")

test.run(arguments="-Q case=1")
test.run(arguments="-Q -c case=1")
test.must_not_exist('test1.o')
test.run(arguments="-Q case=2")

test.pass_test()
