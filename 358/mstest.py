"""
This builder is for running mstest with VS 2008, 
If env['MSTEST_REMOVE_TMP_DIR'] is True, it will also delets all previous temporary mstest directories 
which matche reg. expression: 'username_hostname\s\d{4}-\d{2}-\d{2}\s\d{2}_\d{2}_\d{2}' where username and hostname are real values;
directory like that will be matched and deleted "username_hostname 2000-01-01 10_10_25" 

"""

import os.path
import SCons.Defaults
import SCons.Platform.win32
import SCons.Util
import re
import shutil
import getpass 
import socket
def _detect(env):
    mstest=None
    HLM = SCons.Util.HKEY_LOCAL_MACHINE
    Key = r'Software\Microsoft\VisualStudio\%s\Setup\VS'%env['MSVS_VERSION']
    k=SCons.Util.RegOpenKeyEx(HLM, Key)
    path = SCons.Util.RegQueryValueEx(k, 'EnvironmentDirectory' )
    if path and path[0]:
       path=str(path[0])
       fullpath=os.path.join(path,'mstest.exe')
       if os.path.exists(fullpath):
          mstest=fullpath
    return mstest

def DevDeleteTmpDirMessage(target, source, env):
    return ""
def DevDeleteTmpDir(target, source, env):
   if env['MSTEST_REMOVE_TMP_DIR']:
      username=getpass.getuser()
      hostname=socket.gethostname().upper()
      reTempDir=re.compile('%s_%s\s\d{4}-\d{2}-\d{2}\s\d{2}_\d{2}_\d{2}'%(username,hostname))
      pathdir=os.path.dirname(target[0].abspath)
      if os.path.exists(pathdir):
         for dir in os.listdir(pathdir):
            removeDir=os.path.join(pathdir,dir)
            if os.path.isdir(removeDir):
               match=reTempDir.match(dir)
               if match:
                  print "Removing temporary directory:", removeDir
                  shutil.rmtree(removeDir)
   return 0
  
def generate(env):
   DeletTempDirAction=SCons.Action.Action(DevDeleteTmpDir,strfunction=DevDeleteTmpDirMessage)
   MsTestBuilder=SCons.Builder.Builder(action=[DeletTempDirAction,"\"$MSTEST\" /nologo /testmetadata:$SOURCE /resultsfile:$TARGET"], suffix="$MSTEST_RES_SUFFIX")
   env['MSTEST']=_detect(env)
   env['MSTEST_RES_SUFFIX']=".trx"
   env['MSTEST_REMOVE_TMP_DIR']=False
   env['BUILDERS']['MsTest'] = MsTestBuilder

def exists(env):
   return _detect(env)
