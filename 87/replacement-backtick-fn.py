    def backtick(self, command):
        try:
            import subprocess
            p = subprocess.Popen(
                command
                , stdout=subprocess.PIPE
                , stderr=subprocess.PIPE
            )
            out = p.stdout.read()
            p.stdout.close()
            print "OUTPUT FROM %s:\n" % command[0],out
            err = p.stderr.read()
            p.stderr.close()
            status = p.returncode
            if status:
                raise OSError("'%s' exited %d (%s)" %(" ".join(command),status,err.strip()))

        except ImportError: 
            try:
                popen2.Popen3
            except AttributeError:
                (tochild, fromchild, childerr) = os.popen3(self.subst(command))
                tochild.close()
                err = childerr.read()
                out = fromchild.read()
                fromchild.close()
                status = childerr.close()
            else:
                p = popen2.Popen3(self.subst(command), 1)
                p.tochild.close()
                out = p.fromchild.read()
                err = p.childerr.read()
                status = p.wait()

            if status:
                try:
                    if os.WIFEXITED(status):
                        status = os.WEXITSTATUS(status)
                except AttributeError:
                    pass
                raise OSError("'%s' exited %s" % (command, status))
            if err:
                print "ERROR OUTPUT",err
                import sys
                sys.stderr.write(err)

        return out