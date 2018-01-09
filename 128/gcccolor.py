
"""
====================================================
class GccColorizer, knows how to colorize gcc output.
it uses the ansicolor module, available from www.koders.com.
can be freely used. it is based on the colorgcc.pl script
====================================================
"""


import ansicolor
import re
import string
import sys

class GccColorizer:

   flags = re.DOTALL | re.MULTILINE
   # compile a regular expression that captures the
   # source qouting of gcc
   __src_regex = re.compile (r"\`(.*?)\'", flags)
   # compile a regular expression that captures
   # filename:lineno:message format
   __file_line_msg_regex = re.compile (r"^([^:]*?)\s*:([0-9:]+):( .*)$", flags)
   # filename:message:
   __file_msg_regex= re.compile (r"^(.*?):(.+)[:,]$", flags)
   # compile a regular expression that captures warnings
   __warning_regex = re.compile (r"\s+warning:.*", flags)
   # comile a regex for wrapped message lines
   # wrap lines start with 3 spaces
   __wrap_regex = re.compile (r"^[ ]{3}[^ ]", flags)

   __default_color_names = {
       'reset' : 'default',
       'srcColor'  : 'bold;purple',
       'introColor': 'bold;cyan',
       'warningFileNameColor': 'light;green',
       'warningNumberColor'    : 'light;green',
       'warningMessageColor'    : 'yellow',
       'errorFileNameColor': 'light;green',
       'errorNumberColor'    : 'light;green',
       'errorMessageColor'    : 'red',
   }

   def __init__(self, outfp=sys.stdout):

       self.outfp = outfp

       # buffer where we store lines until they become full message
       self.__buffer = ""
       self.__errors = []
       self.__warnings = []

       # convert the name to ansi-color representations
       self.__colors = {}
       for key, color in self.__default_color_names.items():
           self.__colors[key] = ansicolor.esc_ansicolor(color)

   def colorize_line (self, line):
       """colorize a single gcc message.
       if the message spans more than one line (has wraps) then
       the message is not printed until the complete message has been retrieved."""
       if self.__wrap_regex.match (line):
           #self.__buffer += '\n'
           self.__buffer += line
       else:
           self.colorize_message (self.__buffer)
           self.__buffer = line
   def warnings (self):
       """returns a list of the warnings encountered."""
       return self.__warnings
   def errors (self):
       """returns a list of the errors encountered."""
       return self.__errors
   def reset (self):
       """resets the errors and warnings counters. removes any leftovers in the buffer."""
       self.__buffer = ""
       self.__errors = self.__warnings = []

   def colorize (self, lines):
      """ Colorize the output from the compiler.
      'lines' is an array of the lines of output from the compiler."""
      if isinstance (lines, str):
         # convenience:
         # lines is a string, so we convert it to a list
         # by splitting the lines
         lines = lines.splitlines ()
      for line in lines:
         self.colorize_line (line)
         self.finish ()
   def finish (self):
      """call this method after all lines, in order to print the last buffer."""
      self.colorize_line ("")
   def colorize_message(self, message):
      """Colorizes and prints a full gcc message"""
      if (message == None or len(message)==0):
          return
      match = self.__file_line_msg_regex.match (message)
      if match:
          # Pull the color variable names into the local namespace so
          # we can interpolate them into the format string with one %
          # operation.
          locals().update(self.__colors)

          filename = match.group (1)
          lineno = match.group (2)
          msg = match.group (3)

          if self.__warning_regex.match (msg):
              # Warning
              fmt = '%(warningFileNameColor)s%(filename)s:%(reset)s' + \
                    '%(warningNumberColor)s%(lineno)s:%(reset)s'
              self.outfp.write(fmt % locals())
              self.__srcscan__(msg, locals()['warningMessageColor'])
              self.__warnings.append (message)
          else:
              # Error
              fmt = '%(errorFileNameColor)s%(filename)s:%(reset)s' + \
                    '%(errorNumberColor)s%(lineno)s:%(reset)s'
              self.outfp.write(fmt % locals())
              self.__srcscan__(msg, locals()["errorMessageColor"])
              self.__errors.append (message)

      elif self.__file_msg_regex.match (message):
          # No line number, treat as an "introductory" line of text.
          self.__srcscan__(message, self.__colors["introColor"])

      else:
          # Doesn't seem to be a warning or an error. Print normally.
          self.outfp.write(self.__colors["reset"] + message + '\n')

   def __srcscan__ (self, text, normalColor):
       #
       color_on  = ansicolor.AnsiReset + self.__colors['srcColor']
       color_off = ansicolor.AnsiReset + normalColor
       # This substitute replaces `foo' with `AfooB' where A is the escape
       # sequence that turns on the the desired source color, and B is the
       # escape sequence that returns to $normalColor.
       result = self.__src_regex.subn ("`" + color_on+ r'\1' + color_off + "'", text)
       self.outfp.write(normalColor + result[0] + ansicolor.AnsiReset + '\n')

def spawn_gcc_colorized(sh, escape, cmd, args, env):
    import subprocess
    p = subprocess.Popen(string.join(args), shell=True, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    stdout, stderr = p.communicate()
    colorizer = GccColorizer(sys.stdout)
    colorizer.colorize(stdout)
    return p.returncode

def generate(env):
    env['SPAWN'] = spawn_gcc_colorized

def exists(env):
    return 1


# unit test
if __name__ == "__main__":
   real_gcc_output = """\
common/ArgesCan.cpp:1:27: canFileMedium.h: No such file or directory
common/ArgesCan.cpp:2:26: canBusMedium.h: No such file or directory
In file included from common/ArgesCan.cpp:3:
common/ArgesCan.h:4:23: canMedium.h: No such file or directory
In file included from common/ArgesCan.h:5,
                from common/ArgesCan.cpp:3:
common/brain/appData.h:5:33: MEXimage/coordinate.h: No such file or directory
common/brain/appData.h:6:26: MEXmisc/defs.h: No such file or directory
common/brain/appData.h:7:32: warningsParameters.h: No such file or directory
In file included from common/brain/appData.h:8,
                from common/ArgesCan.h:5,
                from common/ArgesCan.cpp:3:
common/brain/FCWProcess.h:4:25: FCW/process.h: No such file or directory
In file included from common/brain/appData.h:8,
                from common/ArgesCan.h:5,
                from common/ArgesCan.cpp:3:
common/brain/FCWProcess.h:18: error: 'realx' is used as a type, but is not
  defined as a type.
common/ArgesCan.cpp:12: warning: argument to non-pointer type `int' from NULL
common/ArgesCan.cpp:14: error: parse error before `}' token
common/ArgesCan.cpp:17: error: syntax error before `::' token
common/ArgesCan.cpp:20: error: ISO C++ forbids declaration of `_medium' with no
   type
common/ArgesCan.cpp:20: warning: initialization to non-pointer type `int' from
   NULL
common/ArgesCan.cpp:20: warning: argument to non-pointer type `int' from NULL
common/ArgesCan.cpp:21: error: parse error before `if'
common/ArgesCan.cpp:30: error: `MAX_CAN_MSGS_PER_FRAME' was not declared in
   this scope
common/ArgesCan.cpp:30: error: parse error before `;' token
"""

   colorizer=GccColorizer ()
   colorizer.colorize (real_gcc_output.splitlines ())
