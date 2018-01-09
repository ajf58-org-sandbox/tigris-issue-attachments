--- C:\work\sparrow\configs\devscons\v1.0\JavaCommon.py	2007-01-07 15:57:12.000000000 -0500
+++ C:\work\sparrow\configs\devscons\v1.0\DevJavaCommon.py	2007-01-25 10:37:49.000000000 -0500
@@ -145,14 +145,16 @@
         """A state that looks for anonymous inner classes."""
         def __init__(self, outer_state):
             # outer_state is always an instance of OuterState
             self.outer_state = outer_state
             self.tokens_to_find = 2
         def parseToken(self, token):
-            # This is an anonymous class if and only if the next token
-            # is a bracket
+            # This is an anonymous class if and only if the next  
+            #non-whitespace token is a bracket            
+            if token == '\n':
+                return self
             if token == '{':
                 self.outer_state.addAnonClass()
             elif token in ['"', "'"]:
                 return IgnoreState(token, self)
             return self.outer_state
 
