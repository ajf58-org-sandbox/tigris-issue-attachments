import os

cmd='ls'
print 'Trying to execute: ', cmd
tochild, fromchild, childerror = os.popen3(cmd)
line=fromchild.readline()
tochild.close()
fromchild.close()
childerror.close()

#Exception exceptions.TypeError:
# TypeError("'NoneType' object is not callable",) 
#in <bound method Popen3.__del__ of <popen2.Popen3 instance at 0xa55a28>> ignored
