import imp
from imp import reload
import os, sys
from typing import List, Optional, Union

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
		name = name.lower()

		for item in self.modules:
			modName = item.split('.')[0]
			if modName.lower() == name:
				impmod = __import__('scene_check.validators.'+modName, {}, {}, [modName])
				reload(impmod)
				theClass = impmod.__getattribute__( modName )
				return(theClass)

		## class not found!
		raise ValidatorFactoryException('Class not found or unloadable: %s.' % name)

	## ----------------------------------------------------------------------
	def get_class_names( self, task_filter:Optional[str]=None ):
		result = []
		
		modules_lower = [ x.lower() for x in self.modules ]

		if isinstance( task_filter, str ):
			task_filter = task_filter.lower()
			result += [ x for x in modules_lower if task_filter in x ]
		elif isinstance( task_filter, (list, tuple, dict, set)):
			task_filter = [ str(x).lower() for x in task_filter ]
			for item in task_filter:
				result += [ x for x in modules_lower if item in x ]
		elif task_filter is None:
			result += self.modules[:]
		else:
			raise ValueError( "get_class_names: task_filter must be a string, a list of strings, or None." )
		return result

	## ----------------------------------------------------------------------
	def run_all( self, *args, task_filter=None, as_json=False ):
		result = {
			'errors':     [],
			'warnings':   [],
			'auto_fixes': [],
			'valid':      []
		}

		classes = self.get_class_names( task_filter=task_filter )
		if len(args):
			classes = [ x for x in classes if x in args ]

		for name in classes:
			inst = self.get_class(name)()
			inst.process()
			result['errors'] += inst.errors
			result['warnings'] += inst.warnings
			result['auto_fixes'] += inst.auto_fixes
		else:
			result['valid'].append( name )

		if as_json:
			data = {
				'warnings': [ x.to_dict() for x in result['warnings'] ],
				'errors':   [ x.to_dict() for x in result['errors'] ],
				'auto_fixes':   [ x.to_dict() for x in result['auto_fixes'] ],
			}

			return data

		return result


## ----------------------------------------------------------------------
