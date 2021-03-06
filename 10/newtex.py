"""SCons.Tool.tex

Tool-specific initialization for TeX.

There normally shouldn't be any need to import this module directly.
It will usually be imported through the generic SCons.Tool.Tool()
selection method.

"""

#
# Copyright (c) 2001, 2002, 2003 Steven Knight
# Copyright (c) 2003 Kevin Quick
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

__revision__ = "/home/scons/scons/branch.0/baseline/src/engine/SCons/Tool/tex.py 0.94.D001 2003/11/07 06:02:01 knight"

import os.path
import re
import string

import SCons.Action
import SCons.Defaults
import SCons.Node
import SCons.Node.FS
import SCons.Util

# Define an action to build a generic tex file.  This is sufficient for all 
# tex files.
TeXAction = SCons.Action.CommandAction("$TEXCOM")
PDFTeXAction = SCons.Action.CommandAction("$PDFTEXCOM")

# Define an action to build a latex file.  This action might be needed more
# than once if we are dealing with labels and bibtex
LaTeXAction = SCons.Action.CommandAction("$LATEXCOM")
PDFLaTeXAction = SCons.Action.Action("$PDFLATEXCOM")

# Define an action to run BibTeX on a file.
BibTeXAction = SCons.Action.CommandAction("$BIBTEXCOM")

MoveAction = SCons.Action.Action('[ "${TARGET.file}" == "${TARGET}" ] || mv ${TARGET.file} $TARGET')

def LaTeXAuxAction(target = None, source= None, env=None):
    """A builder for LaTeX files that checks the output in the aux file
    and decides how many times to use LaTeXAction, and BibTeXAction."""
    # Get the base name of the target
    basename, ext = os.path.splitext(str(target[0]))
    # Run LaTeX once to generate a new aux file.
    if ext == '.pdf':
        PDFLaTeXAction(target,source,env)
    else:
        LaTeXAction(target,source,env)
    # Now if bibtex will need to be run.
    content = open(os.path.basename(basename) + ".aux","rb").read()
    if string.find(content, "bibdata") != -1:
        bibfile = env.fs.File(basename)
        BibTeXAction(None,bibfile,env)
    # Now check if latex needs to be run yet again.
    for trial in range(3):
        content = open(os.path.basename(basename) + ".log","rb").read()
        if not re.search("^LaTeX Warning:.*Rerun",content,re.MULTILINE):
            break
        LaTeXAction(target,source,env)
    return 0

def TeXLaTeXAction(target = None, source= None, env=None):
    """A builder for TeX and LaTeX that scans the source file to
    decide the "flavor" of the source and then executes the appropriate
    program."""
    LaTeXFile = None
    for src in source:
	content = src.get_contents()
        if re.search("\\\\document(style|class)",content):
	   LaTeXFile = 1
           break
    if LaTeXFile:
	LaTeXAuxAction(target,source,env)
    else:
        if os.path.splitext(str(target[0]))[1] == '.pdf':
            PDFTexAction(target,source,env)
        else:
            TeXAction(target,source,env)
    return 0

def generate(env):
    """Add Builders and construction variables for TeX to an Environment."""
    try:
        bld = env['BUILDERS']['DVI']
    except KeyError:
        bld = SCons.Defaults.DVI()
        env['BUILDERS']['DVI'] = bld
        
    bld.add_action('.tex', [TeXLaTeXAction, MoveAction])
    bld.add_action('.latex', [LaTeXAuxAction, MoveAction])
    bld.add_action('.ltx', [LaTeXAuxAction, MoveAction])

    try:
        bld2 = env['BUILDERS']['PDF']
    except KeyError:
        bld2 = SCons.Defaults.PDF()
        env['BUILDERS']['PDF'] = bld2

    bld2.add_action('.tex', [SetInputsAction, TeXLaTeXAction, MoveAction])
    bld2.add_action('.latex', [LaTeXAuxAction, MoveAction])
    bld2.add_action('.ltx', [LaTeXAuxAction, MoveAction])

    env['LCLTEXINPUTS'] = ''

    inpspec = 'TEXINPUTS=%s:${TARGET.dir}:$LCLTEXINPUTS:'%os.environ['TEXINPUTS']
    
    env['TEX']      = 'tex'
    env['TEXFLAGS'] = ''
    env['TEXCOM']   = '%s $TEX $TEXFLAGS $SOURCES'%inpspec

    env['PDFTEX']      = 'pdftex'
    env['PDFTEXFLAGS'] = ''
    env['PDFTEXCOM']   = '%s $PDFTEX $PDFTEXFLAGS $SOURCES'%inpspec

    # Duplicate from latex.py.  If latex.py goes away, then this is still OK.
    env['LATEX']      = 'latex'
    env['LATEXFLAGS'] = ''
    env['LATEXCOM']   = '%s $LATEX $LATEXFLAGS $SOURCES'%inpspec

    env['PDFLATEX']      = 'pdflatex'
    env['PDFLATEXFLAGS'] = ''
    env['PDFLATEXCOM']   = "%s $PDFLATEX $PDFLATEXFLAGS $SOURCES"%inpspec

    env['BIBTEX']      = 'bibtex'
    env['BIBTEXFLAGS'] = ''
    env['BIBTEXCOM']   = '%s $BIBTEX $BIBTEXFLAGS $SOURCES'%inpspec


def exists(env):
    return (env.Detect('tex') |
            env.Detect('latex') |
            env.Detect('pdftex') |
            env.Detect('pdflatex'))
