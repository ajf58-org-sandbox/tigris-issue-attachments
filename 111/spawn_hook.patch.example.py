
"""
====================================================
class GccColorizer, knows how to colorize gcc output.
it uses the ansicolor module, available from www.koders.com.
it doesnt use scons at all, and can be freely used. it is based on the colorgcc.pl script
====================================================
"""


import ansicolor
import re

class GccColorizer:
   def __init__(self):
       self.__color_names = {
           'reset' : 'default',
                     'srcColor'  : 'bold;purple',
           'introColor': 'bold;cyan',
                     'warningFileNameColor': 'light;green',
           'warningNumberColor'    : 'light;green',
           'warningMessageColor'    : 'bold;yellow',
                     'errorFileNameColor': 'light;green',
           'errorNumberColor'    : 'light;green',
           'errorMessageColor'    : 'bold;red',
       }
             # convert the name to ansi-color representations
       self.__colors = {}
       for color in self.__color_names.keys():
           self.__colors [color] = ansicolor.esc_ansicolor (self.__color_names [color])
             flags = re.DOTALL | re.MULTILINE
                 # compile a regular expression that captures the
       # source qouting of gcc
       self.__src_regex = re.compile (r"\`(.*?)\'", flags)
             # compile a regular expression that captures
       # filename:lineno:message format
       self.__file_line_msg_regex = re.compile (r"^([^:]*?)\s*:([0-9:]+):( .*)$", flags)
             # filename:message:
       self.__file_msg_regex= re.compile (r"^(.*?):(.+)[:,]$", flags)
             # compile a regular expression that captures warnings
       self.__warning_regex = re.compile (r"\s+warning:.*", flags)
             # comile a regex for wrapped message lines
       # wrap lines start with 3 spaces
       self.__wrap_regex = re.compile (r"^[ ]{3}[^ ]", flags)
             #buffer where we store lines until they become full message
       self.__buffer = ""
             # lists of error and warnings
       self.__errors = []
       self.__warnings = []
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
           filename= match.group (1)
           lineno = match.group (2)
           msg = match.group (3)
                                                         if self.__warning_regex.match (msg):
               # Warning
               print self.__colors["warningFileNameColor"], filename, ':', self.__colors["reset"],
               print self.__colors["warningNumberColor"], \
                           'line', lineno, ':', self.__colors["reset"],
               self.__srcscan__(msg, self.__colors["warningMessageColor"])
                             # add this message to the list of warnings
               self.__warnings.append (message)
           else:
               # Error
               print self.__colors["errorFileNameColor"], filename, ':', self.__colors["reset"],
               print self.__colors["errorNumberColor"], \
                           'line', lineno, ':', self.__colors["reset"],
               self.__srcscan__(msg, self.__colors["errorMessageColor"])
                             # add this message to the list of errors
               self.__errors.append (message)
                     elif self.__file_msg_regex.match (message):
           # No line number, treat as an "introductory" line of text.
           self.__srcscan__(message, self.__colors["introColor"])
       else: # Anything else.                  # Doesn't seem to be a warning or an error. Print normally.
           print self.__colors["reset"], message,
             #print

         def __srcscan__ (self, text, normalColor):
       #
       color_on  = ansicolor.AnsiReset + self.__colors['srcColor']
       color_off = ansicolor.AnsiReset + normalColor
                 # This substitute replaces `foo' with `AfooB' where A is the escape
       # sequence that turns on the the desired source color, and B is the
       # escape sequence that returns to $normalColor.
       result = self.__src_regex.subn ("`" + color_on+ r'\1' + color_off + "'", text)
             print normalColor, result[0], ansicolor.AnsiReset,


# unit test
if __name__ == "__main__":
   real_gcc_output = """common/ArgesCan.cpp:1:27: canFileMedium.h: No such file or directory
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

   colorizer=ColorGcc ()
   colorizer.colorize (real_gcc_output.splitlines ())





"""
===================================
actual usage of the spawn hooks, a class that makes g++ output
for c++ files colorful
===================================
"""

class ColouredCxxAction(SCons.Action.CommandAction):
   def __init__(self, cmd, cmdstr=None, *args, **kw):
       SCons.Action.CommandAction.__init__(self, cmd, cmdstr, *args, **kw)
             self.__colorizer = GccColorizer.GccColorizer ()
       pass
         def __spawn__ (self, shell, escape, cmd, args, scons_env, user_env):
       """executes the cmd using the piped spawning function defined in the environment."""
       try:
           get_env_command = scons_env['SPAWN_CMDLINE']
       except KeyError:
           raise SCons.Errors.UserError('Missing SPAWN_CMDLINE construction variable.')

       cmdline= get_env_command (shell, escape, cmd, args, user_env)
       return self.__colorize__ (cmdline)
               def __colorize__ (self, cmdline):
       process = popen2.Popen3 (cmdline, capturestderr=True)
             # reset the warnings and errors in the colorizer
       self.__colorizer.reset()
             max_number_of_errors = 10
       max_errors_shown = False
             # close the stdin of the process
       process.tochild.close ()
       line = process.childerr.readline ()
       while line:
           self.__colorizer.colorize_line (line)
                     # do not show more than 10 errors
           if (len (self.__colorizer.errors ()) > max_number_of_errors):
               max_errors_shown = True
               break;
                     line = process.childerr.readline ()
             if max_errors_shown:
           print
           print 'Source has additional errors, which are not shown.'
           print
       else:
           # finish processing the last line
           self.__colorizer.finish ()
         # return the exit status of the process
       process.fromchild.close ()
       process.childerr.close ()
       status = process.wait ()
       if status & 0xff:
           status = status | 0x80
                 status = status >> 8
       return status




"""
=================================
usage:
just change the action of the StaticObject builder to this action, and you get colorful output immediately!!!
=================================
"""

# unit test:
env.StaticObject.builder.action = ColouredCxxAction (cmd='$CXXCOM', cmdstr='$CXXCOMSTR')






