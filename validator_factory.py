import json, os, sys
from imp import reload
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
		self.module_path = os.sep.join( [__file__.rpartition( os.sep )[0], 'validators'] )
		self.modules = [ x.partition('.')[0] for x in os.listdir(self.module_path) if x.endswith('.py') 
					and not x.count('__init') 
					and not x.count('base_validator') ]

		self.scheme_path = os.sep.join( [__file__.rpartition( os.sep )[0], 'schemes'] )
		self.schemes = [ x.partition('.')[0].lower() for x in os.listdir(self.scheme_path) if x.endswith('.scheme') ]

		# print("Valid Schemes:")
		# for scheme in self.schemes:
		# 	print( "\t+ {}".format(scheme) )

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
	def run_scheme( self, scheme:str, task_filter:Optional[str]=None, as_json:Optional[bool]=False ):
		"""
		Tries to run the list of Validators provided by the named Scheme.
		Schemes are JSON files in the schemes/ folder, specified as lists
		of strings:

		[
			'ThisValidator',
			'SomeOtherValidator'
		]

		where the string names match file names of Validators in the validators/
		folder.

		:param scheme: Name of Scheme to load.
		:param task_filter: If specified, filters out the Validators in the Scheme
							using this string. Default: None
		:param as_json: If True, returns the results dict in a JSON-compatible format.
						Default: False
		:returns: 	The results dict of ValidationMessage classes for the errors, warnings,
					and auto-fixes. If as_json is True, the dict will be in a JSON-compatible
					format. Returns None on error.
		"""

		assert( isinstance(scheme, str) )
		scheme = scheme.lower()

		if not scheme in self.schemes:
			raise ValueError( 'Chosen Scheme "{}" does not exist.'.format(scheme) )

		scheme_file_path = os.sep.join([self.scheme_path, scheme+'.scheme'])

		with open( scheme_file_path, 'r' ) as fp:
			data = json.load( fp )

		## validate the file
		if not isinstance(data, list) or not all( [isinstance(x, str) for x in data]):
			raise ValueError( 'Chosen Scheme "{}" is an improperly formatted file ({}).'.format(scheme, scheme_file_path) )

		return self.run_all( *data, task_filter=task_filter, as_json=as_json )


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

			print( "Classes modifed to {}".format(str(classes)) )

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
				'warnings':   [ x.to_dict() for x in result['warnings'] ],
				'errors':     [ x.to_dict() for x in result['errors'] ],
				'auto_fixes': [ x.to_dict() for x in result['auto_fixes'] ],
			}

			return data

		return result


## ----------------------------------------------------------------------
