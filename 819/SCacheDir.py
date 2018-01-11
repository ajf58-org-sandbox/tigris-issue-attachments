#
# Copyright (c) 2001, 2002, 2003, 2004, 2005, 2006, 2007, 2008, 2009, 2010 The SCons Foundation
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
# This CacheDir has changes for better group access of cache files
# TODO: smart cache size, like in ccache

__revision__ = "src/engine/SCons/CacheDir.py 5064 2010/06/27 18:05:07 bdeegan"

__doc__ = """
CacheDir support
"""

import os.path
import stat
import sys

import SCons.Action

cache_enabled = True
cache_debug = False
cache_force = False
cache_show = False

def CacheRetrieveFunc(target, source, env):
    t = target[0]
    fs = t.fs
    cd = env.get_CacheDir()
    cachedir, cachefile = cd.LocalCachePath(t)
    if cachefile is None:
        cd.CacheDebug('CacheRetrieve(%s): %s not in local\n', t)
        cachedir, cachefile = cd.GlobalCachePath(t)
        if cachefile is None:
            cd.CacheDebug('CacheRetrieve(%s): %s not in global\n', t)
            return 1
        else:
            cd.CacheDebug('CacheRetrieve(%s): retrieving from global %s\n', t)
    else:
        cd.CacheDebug('CacheRetrieve(%s): retrieving from local %s\n', t)
    if SCons.Action.execute_actions:
        if fs.islink(cachefile):
            fs.symlink(fs.readlink(cachefile), t.path)
        else:
            try:
                fs.link(cachefile, t.path)
            except OSError:
                tempfile = t.path+'.tmp'+str(os.getpid())
                env.copy_from_cache(cachefile, tempfile)
                #st = fs.stat(cachefile)
                #fs.chmod(tempfile, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWRITE)
                fs.rename(tempfile, t.path)
    return 0

def CacheRetrieveString(target, source, env):
    t = target[0]
    cd = env.get_CacheDir()
    cachedir, cachefile = cd.LocalCachePath(t)
    if cachefile is None:
        cachedir, cachefile = cd.GlobalCachePath(t)
    if cachefile is None:
        return None
    else:
        return "Retrieved `%s' from cache" % t.path

CacheRetrieve = SCons.Action.Action(CacheRetrieveFunc, CacheRetrieveString)

CacheRetrieveSilent = SCons.Action.Action(CacheRetrieveFunc, None)

def CachePushFunc(target, source, env):
    t = target[0]
    if t.nocache:
        return
    fs = t.fs
    cd = env.get_CacheDir()

    if not cd.HasLocalCache():
        cd.CacheDebug('CachePush(%s): no local cache for %s\n', t)
        return

    cachedir, cachefile = cd.LocalCachePath(t, False)
    if fs.exists(cachefile):
        # Don't bother copying it if it's already there.  Note that
        # usually this "shouldn't happen" because if the file already
        # existed in cache, we'd have retrieved the file from there,
        # not built it.  This can happen, though, in a race, if some
        # other person running the same build pushes their copy to
        # the cache after we decide we need to build it but before our
        # build completes.
        cd.CacheDebug('CachePush(%s): %s already exists in local cache\n', t)
        return

    cd.CacheDebug('CachePush(%s): pushing to local %s\n', t)

    tempfile = cachefile+'.tmp'+str(os.getpid())
    errfmt = "Unable to copy %s to cache. Cache file is %s"

    if not fs.isdir(cachedir):
        try:
            fs.makedirs(cachedir)
            # make directory user and group writable for sharing cache
            st = fs.stat(cachedir)
            fs.chmod(cachedir, stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IWUSR | stat.S_IRWXG)
        except EnvironmentError:
            # We may have received an exception because another process
            # has beaten us creating the directory.
            if not fs.isdir(cachedir):
                msg = errfmt % (str(target), cachefile)
                raise SCons.Errors.EnvironmentError(msg)

    try:
        if fs.islink(t.path):
            fs.symlink(fs.readlink(t.path), tempfile)
        else:
            try:
                fs.link(t.path, tempfile)
            except OSError:
                fs.copy2(t.path, tempfile)
        # open file for read by group and close it for write
        # we don't allow writes to cached files, because they are hard-linked
        # into user directories
        st = fs.stat(tempfile)
        new_mod = stat.S_IMODE(st[stat.ST_MODE]) | stat.S_IRGRP
        new_mod &= ~(stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH)
        fs.chmod(tempfile, new_mod)
        fs.rename(tempfile, cachefile)
    except EnvironmentError:
        # It's possible someone else tried writing the file at the
        # same time we did, or else that there was some problem like
        # the CacheDir being on a separate file system that's full.
        # In any case, inability to push a file to cache doesn't affect
        # the correctness of the build, so just print a warning.
        msg = errfmt % (str(target), cachefile)
        SCons.Warnings.warn(SCons.Warnings.CacheWriteErrorWarning, msg)

CachePush = SCons.Action.Action(CachePushFunc, None)

def CachePath(path, node):
    """
    Return tuple of directory and file path into specified cache path.
    """
    sig = node.get_cachedir_bsig()
    subdir = sig[0].lower()
    dir = os.path.join(path, subdir)
    return dir, os.path.join(dir, sig)

class CacheDir(object):

    def __init__(self, path):
        try:
            import hashlib
        except ImportError:
            msg = "No hashlib or MD5 module available, CacheDir() not supported"
            SCons.Warnings.warn(SCons.Warnings.NoMD5ModuleWarning, msg)
            path = None
        if path is None:
            self.path = None
            self.global_paths = []
            self.enabled = False
        else:
            self.path, self.global_paths = path
            self.enabled = True
        self.current_cache_debug = None
        self.debugFP = None

    def CacheDebug(self, fmt, target):
        if cache_debug != self.current_cache_debug:
            if cache_debug == '-':
                self.debugFP = sys.stdout
            elif cache_debug:
                self.debugFP = open(cache_debug, 'w')
            else:
                self.debugFP = None
            self.current_cache_debug = cache_debug
        if self.debugFP:
            sig = target.get_cachedir_bsig()
            self.debugFP.write(fmt % (target, sig))

    def is_enabled(self):
        return (cache_enabled and self.enabled)

    def cachepath(self, node):
        """
        """
        if not self.is_enabled():
            return None, None
        cachedir, cachefile = self.LocalCachePath(node)
        if cachefile is None:
            cachedir, cachefile = self.GlobalCachePath(node)
        return cachedir, cachefile

    def HasLocalCache(self):
        return self.path is not None
    def HasGlobalCache(self):
        return bool(self.global_paths)

    def LocalCachePath(self, node, check_exists = True):
        """
        Return tuple of directory and file path into local cache, if such a file exists.
        """
        if self.HasLocalCache():
            dir, file = CachePath(self.path, node)
            fs = node.fs
            if not check_exists or fs.exists(file):
                return dir, file
        return None, None

    def GlobalCachePath(self, node):
        """
        Return tuple of directory and file path into global cache, if such a file exists.
        """
        fs = node.fs
        for path in self.global_paths:
            dir, file = CachePath(path, node)
            if fs.exists(file):
                return dir, file
        return None, None

    def retrieve(self, node):
        """
        This method is called from multiple threads in a parallel build,
        so only do thread safe stuff here. Do thread unsafe stuff in
        built().

        Note that there's a special trick here with the execute flag
        (one that's not normally done for other actions).  Basically
        if the user requested a no_exec (-n) build, then
        SCons.Action.execute_actions is set to 0 and when any action
        is called, it does its showing but then just returns zero
        instead of actually calling the action execution operation.
        The problem for caching is that if the file does NOT exist in
        cache then the CacheRetrieveString won't return anything to
        show for the task, but the Action.__call__ won't call
        CacheRetrieveFunc; instead it just returns zero, which makes
        the code below think that the file *was* successfully
        retrieved from the cache, therefore it doesn't do any
        subsequent building.  However, the CacheRetrieveString didn't
        print anything because it didn't actually exist in the cache,
        and no more build actions will be performed, so the user just
        sees nothing.  The fix is to tell Action.__call__ to always
        execute the CacheRetrieveFunc and then have the latter
        explicitly check SCons.Action.execute_actions itself.
        """
        if not self.is_enabled():
            return False

        env = node.get_build_env()
        if cache_show:
            if CacheRetrieveSilent(node, [], env, execute=1) == 0:
                node.build(presub=0, execute=0)
                return True
        else:
            if CacheRetrieve(node, [], env, execute=1) == 0:
                return True

        return False

    def push(self, node):
        if not self.is_enabled():
            return
        return CachePush(node, [], node.get_build_env())

    def push_if_forced(self, node):
        if cache_force:
            return self.push(node)

# Local Variables:
# tab-width:4
# indent-tabs-mode:nil
# End:
# vim: set expandtab tabstop=4 shiftwidth=4:
