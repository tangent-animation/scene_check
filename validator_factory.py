import imp
from imp import reload
import os, sys

from scene_check.validators import base_validator
reload( base_validator )
from scene_check.validators.base_validator import BaseValidator as bv

import bpy

## ----------------------------------------------------------------------
class ValidatorFactoryException(Exception):
	pass


## ----------------------------------------------------------------------
class ValidatorFactory(object):
	def __init__(self, clear=True):
		self.modulePath = os.sep.join( [__file__.rpartition( os.sep )[0], 'validators'] )
		self.modules = [ x.partition('.')[0] for x in os.listdir(self.modulePath) if x.endswith('.py') 
					and not x.count('__init') 
					and not x.count('base_validator') ]

		if clear:
			self.clear_log()

	## ----------------------------------------------------------------------

	def __getitem__(self, key):
		return(self.getClass(key))

	def __setitem__(self, key, value):
		raise ValueError("ValidatorFactory does not allow the setting of values through brackets.")

	## ----------------------------------------------------------------------
	def clear_log(self):
		if not bv.log_name in bpy.data.texts:
			log = bpy.data.texts.new( bv.log_name )
		else:
			log = bpy.data.texts[bv.log_name]
			log.clear()

	## ----------------------------------------------------------------------
	def get_class( self, name ):
		for item in self.modules:
			modName = item.split('.')[0]
			if modName == name:
				impmod = __import__('scene_check.validators.'+modName, {}, {}, [modName])
				reload(impmod)
				theClass = impmod.__getattribute__( modName )
				return(theClass)

		## class not found!
		raise ValidatorFactoryException('Class not found or unloadable: %s.' % name)


	## ----------------------------------------------------------------------
	def get_class_names( self, filter=None ):
		if isinstance( filter, str ):
			filter = filter.lower()
			result = [ x for x in self.modules if filter in x.lower() ]
		else:
			result = self.modules[:]
		return result


## ----------------------------------------------------------------------
