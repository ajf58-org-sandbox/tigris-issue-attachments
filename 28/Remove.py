
class Base:
    def mRemove(self, **kw):
        """Remove values from existing construction variables
        in an Environment.
        """
        kw = copy_non_reserved_keywords(kw)
        for key, val in kw.items():
            # It would be easier on the eyes to write this using
            # "continue" statements whenever we finish processing an item,
            # but Python 1.5.2 apparently doesn't let you use "continue"
            # within try:-except: blocks, so we have to nest our code.
            try:
                orig = self._dict[key]
            except KeyError:
                # No existing variable in the environment, so just skip it
                pass
            else:
                try:
                    # Most straightforward:  just try to substract it.
                    # But this will not work in most cases :-(
                    self._dict[key] = orig - val
                except TypeError:
                    try:
                        # It orig and val is dictionaties:
                        for k in val.keys():
                                del orig[k]
                        # May be some recursion ?
                    except AttributeError:
                        try:
                            # Check if the original is a list.
                            remove_from_orig = orig.remove
                        except AttributeError:
                            # Can't do nothing more
                            pass
                        else:
                            # The original is a list, so remove
                            # value from it.
                            try:
                                i = val[0]
                            except TypeError:
                                val = [ val ]
                            for i in val:
                                try:
                                    remove_from_orig(i)
                                except ValueError:
                                    pass
        self.scanner_map_delete(kw)

