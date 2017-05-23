import imp
from imp import reload
import os, sys

from validators import base_validator as bv
reload( bv )

import bpy

## ----------------------------------------------------------------------
class ValidatorFactoryException(Exception):
	pass


## ----------------------------------------------------------------------
class ValidatorFactory(object):
	def __init__(self):
		self.modulePath = os.sep.join( [__file__.rpartition( os.sep )[0], 'validators'] )
		self.modules = [ x.partition('.')[0] for x in os.listdir(self.modulePath) if x.endswith('.py') 
					and not x.count('__init') 
					and not x.count('base_validator') ]

	## ----------------------------------------------------------------------

	def __getitem__(self, key):
		return(self.getClass(key))

	def __setitem__(self, key, value):
		raise ValueError("ValidatorFactory does not allow the setting of values through brackets.")

	## ----------------------------------------------------------------------
	def get_class( self, name ):
		for item in self.modules:
			modName = item.split('.')[0]
			if modName == name:
				impmod = __import__('validators.'+modName, {}, {}, [modName])
				reload(impmod)
				theClass = impmod.__getattribute__( modName )
				return(theClass)

		## class not found!
		raise ValidatorFactoryException('Class not found or unloadable: %s.' % name)


	## ----------------------------------------------------------------------
	def get_class_names( self ):
		return self.modules[:]


## ----------------------------------------------------------------------
