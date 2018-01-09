#!/usr/bin/env python
#
# __COPYRIGHT__
#
# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the
# "Software"), to deal in the Software without restriction, including
# without limitation the rights to use, copy, modify, merge, publish,
# distribute, sublicense, and/or sell copies of the Software, and to
# permit persons to whom the Software is furnished to do so, subject to
# the following conditions:
#
# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY
# KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE
# WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
#

__revision__ = "__FILE__ __REVISION__ __DATE__ __DEVELOPER__"

"""
Real world test for compiling dependent classes from different directories.
"""

import os

import TestSCons

test = TestSCons.TestSCons()

where_javac, java_version = test.java_where_javac()
where_javah = test.java_where_javah()
where_java_include=test.java_where_includes()


test.subdir(['src'],
            ['src', 'Source'],
            ['src', 'Source', 'Interface'],
            ['src', 'gen'],
            ['src', 'gen', 'mymod'],
            ['src', 'gen', 'mymod', 'java'],
            ['src', 'build'],
            ['src', 'build', 'classes'])

test.write(['SConstruct'], """\
import os,sys
env=Environment(tools = ['default', 'javac'],
                JAVAC = r'%(where_javac)s')
Export('env')
env.PrependENVPath('PATH',os.environ.get('PATH',[]))

Java('build/classes', [env.Dir('src/gen/mymod/java'), env.Dir('src/Source/Interface')])

""" % locals())

test.write(['src', 'gen', 'mymod', 'java', 'LibraryFlags.java'], """\
package com.mycompany.PROD;

public enum LibraryFlags {
  @com.mycompany.metadata.ConstantName("IgnoreDefaultDirectories")   IGNORE_DEFAULT_DIRECTORIES(1),
  @com.mycompany.metadata.ConstantName("CheckSubFonts")   CHECK_SUB_FONTS(4),
  @com.mycompany.metadata.ConstantName("InitEdit")   INIT_EDIT(32);

  final int someValue() {
    return someValue;
  }

  static LibraryFlags someToEnum(int someValue) {
    LibraryFlags[] someValues = LibraryFlags.class.getEnumConstants();
    if (someValue < someValues.length && someValue >= 0 && someValues[someValue].someValue == someValue)
      return someValues[someValue];
    for (LibraryFlags someEnum : someValues)
      if (someEnum.someValue == someValue)
        return someEnum;
    throw new IllegalArgumentException("No enum " + LibraryFlags.class + " with value " + someValue);
  }

  private LibraryFlags() {
      this.someValue = 75;
  }

  private LibraryFlags(int someValue) {
    this.someValue = someValue;
  }

  private LibraryFlags(LibraryFlags someEnum) {
    this.someValue = someEnum.someValue;
  }

  private final int someValue;

}
""")

test.write(['src', 'Source', 'Interface', 'ConstantName.java'], """\
package com.mycompany.metadata;

import java.lang.annotation.*;

/**
 * Indicates the canonical name of a constant or enum value
 */
@Retention(RetentionPolicy.RUNTIME)
@Target(ElementType.FIELD)
public @interface ConstantName {
    String value();
}
""")

test.run(arguments = '.')

test.must_exist(['src', 'build', 'classes', 'com', 'mycompany', 'metadata', 'ConstantName.class'])
test.must_exist(['src', 'build', 'classes', 'com', 'mycompany', 'PROD', 'LibraryFlags.class'])

test.must_exist(['src', 'gen', 'mymod', 'java', 'LibraryFlags.java'])
test.must_exist(['src', 'Source', 'Interface', 'ConstantName.java'])

test.up_to_date(arguments = '.')

test.pass_test()

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
