    def MergeFlags(self, args, unique=1):
        """
        Merge the dict in args into the construction variables.  If args
        is not a dict, it is converted into a dict using ParseFlags.
        If unique is not set, the flags are appended rather than merged.
        """

	print "MERGEFLAGS on ",args
	
        if not SCons.Util.is_Dict(args):
            args = self.ParseFlags(args)
            print "PARSEFLAGS RESULT WAS",args
        if not unique:
            apply(self.Append, (), args)
            return self
        for key, value in args.items():
            print "MERGEFLAGS, key = %s, value = %s" % (key,value)
            if value == '':
                continue
            try:
                orig = self[key]
            except KeyError:
                orig = value
            else:
                if orig == None or len(orig) == 0:
                	orig = []
                elif not SCons.Util.is_List(orig): 
                	orig = [orig]
                
                orig = orig + value
            t = []
            if key[-4:] == 'PATH':
                ### keep left-most occurence
                for v in orig:
                    if v not in t:
                        t.append(v)
            else:
                ### keep right-most occurence
                orig.reverse()
                for v in orig:
                    if v not in t:
                        t.insert(0, v)
            self[key] = t
        return self