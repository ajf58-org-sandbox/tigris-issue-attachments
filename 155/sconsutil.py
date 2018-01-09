
def myInstaller(dest, source, env):
     """Installer Function that Supports Symlinks"""

     construction_vars=env.Dictionary();
     
     usesymlink= (construction_vars.has_key('INSTALL_SYMLINKS')
        and construction_vars['INSTALL_SYMLINKS'])
     
     print 'dest=',dest
     print 'source=',source

     destDir = os.path.dirname(dest)
     print 'destDir=',destDir
     
     if not os.path.exists(destDir):
         os.makedirs(destDir)
     if os.path.isdir(source):
         shutil.copytree(source, dest, symlinks = usesymlink)
     elif os.path.islink(source) and usesymlink:
         linkto = os.readlink(source)
         os.symlink(linkto, dest)     
     else:
         shutil.copy2(source, dest)
