class newCLVar(list):
	# dirt dumb for testing
	def __init__(self, v): self.v = v.split()
	def set(self, Vars_object, value):
		#print(self)
		#print(Vars_object)
		#print(value)
		self.v = value.split()
	def get(self, Vars_object):
		#print(self)
		#print(Vars_object)
		return self.v

class Env:	# very simple stand-in
	# Base class for environment variables
	# Holds common objects with special semantics
	class Vars(object):
		# don't yet know if anything's needed here
		pass

	def __init__(self):
		# use a dynamically-created intermediate class
		# to hold per-Env objects with special semantics
		class Intermediate(self.Vars):
			# don't yet know if anything's needed here
			pass
		self.vars = Intermediate()

	def __setitem__(self, key, value):
		try:	self.vars.__getattribute__(key) # faster than hasattr?
		except AttributeError:
			if not _is_valid_var.match(key):
				raise SCons.Errors.UserError, "Illegal construction variable `%s'" % key
		self.vars.__setattr__(key, value)

	def __getitem__(self, key):
		try:
			return self.vars.__getattribute__(key)
		except AttributeError, e:
			raise KeyError(e)

	def __delitem__(self, key):
		try:
			self.vars.__delattr__(key)
		except AttributeError, e:
			raise KeyError(e)

	# set up variable with list-like special semantics
	def ListLike(self, key):
		try:	v = self.vars.__getattribute__(key)
		except AttributeError: v = ''
		print('newCLVar initial <' + v + '>')
		ll = newCLVar(v)
		setattr(self.vars.__class__, key,
			property(ll.get, ll.set, _nodel))

########    INITIALIZE

import re
_is_valid_var = re.compile(r'[_a-zA-Z]\w*$')

reserved_construction_var_names = [
    'CHANGED_SOURCES',
    'CHANGED_TARGETS',
    'SOURCE',
    'SOURCES',
    'TARGET',
    'TARGETS',
    'UNCHANGED_SOURCES',
    'UNCHANGED_TARGETS',
]

future_reserved_construction_var_names = []

def _noget(key): raise KeyError(key)
def _nodel(key): raise KeyError(key)

def _set_reserved(key, value): raise KeyError('Trying to set reserved value')
def _set_future_reserved(env, key, value): pass
def _set_SCANNERS(env, key, value): raise KeyError('Trying to set reserved value')
def _set_BUILDERS(env, key, value): raise KeyError('Trying to set reserved value')

for key in reserved_construction_var_names:
    setattr(Env.Vars, key, property(_noget, _set_reserved, _nodel))
for key in future_reserved_construction_var_names:
    setattr(Env.Vars, key, property(_noget, _set_future_reserved, _nodel))
setattr(Env.Vars, 'BUILDERS', property(_noget, _set_BUILDERS, _nodel))
setattr(Env.Vars, 'SCANNERS', property(_noget, _set_SCANNERS, _nodel))

########    TEST

e = Env()

for key in reserved_construction_var_names + ['BUILDERS', 'SCANNERS']:
	# setting a special variable should throw KeyError
	try:	e[key] = 'nope'
	except KeyError: pass
	else:	print('oops, should have thrown KeyError setting ' + key)
	# fetching a special variable should throw KeyError
	try:	e[key]
	except KeyError: pass
	else:	print('oops, should have thrown KeyError fetching ' + key)
	# deleting a special variable should throw KeyError
	try:	del e[key]
	except KeyError: pass
	else:	print('oops, should have thrown KeyError deleting ' + key)

for v in	['simple sting',
		['a', 'list'],
		('a', 'tuple'),
		{'a' : 'dict'},
		]:
	e['test'] = v
	if e['test'] != v:
		print('oops')

key = 'CFLAGS'
e.ListLike(key)
# should be same
print(e.vars.CFLAGS)
print(e[key])
e[key] = 'a test value'
# should be same
print(e.vars.CFLAGS)
print(e[key])

e = Env()	# repeat with new env
key = 'CFLAGS'
e[key] = 'an initial test value'
e.ListLike(key)
# should be same
print(e.vars.CFLAGS)
print(e[key])
e[key] = 'a new test value'
# should be same
print(e.vars.CFLAGS)
print(e[key])
