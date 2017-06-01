import os
import bpy

## ----------------------------------------------------------------------
class BVException(Exception): pass
class BVInvalidSubclass(BVException): pass
class BVNotProcessed(BVException): pass


## ----------------------------------------------------------------------
class ValidationMessage( object ):
	def __init__( self, ob, subob, message, parent=None, type=None, data=None, error=True ):
		self.ob = ob
		self.subob = subob
		self.message = message
		self.parent = parent if parent else Error
		self._type = type
		self.data = data
		self.is_error = error

	def __repr__(self):
		msg = "<< {}".format( "Error " if self.is_error else "Warning " )
		if self.type:
			msg += "Type: %s" % str( self.type )
		if self.ob:
			msg += "\n\tObject: %s" % self.ob.name
		if self.subob:
			msg += " Subob: %s" % str( self.subob )

		msg += "\n\t{}: {}".format( self.parent, self.message )
		msg += " >>"
		return msg

	@property
	def type( self ):
		return '' if self._type is None else self._type


## ----------------------------------------------------------------------
class BaseValidator( object ):
	enabled = True
	automatic_fix = False
	log_name = 'check_result_log.csv'

	def __init__( self ):
		self.processed = False
		self.warnings = []
		self.errors = []
		self.file_full_path = bpy.path.abspath( bpy.data.filepath )
		self.dir_name = os.path.dirname( self.file_full_path )
		self.file_name = os.path.basename( self.file_full_path )
		self.root_name = self.file_name.partition('.')[0]

		try:
			self.asset_type = self.root_name[:3]
		except:
			self.asset_type = 'unk'

	def __del__( self ):
		if not self.log_name in bpy.data.texts:
			log = bpy.data.texts.new( self.log_name )
		else:
			log = bpy.data.texts[self.log_name]

		if len( self.errors ):
			for error in self.errors:
				log.write( repr(error) + "\n" )
		else:
			log.write( '<< {}: Passed >>\n'.format(self.id()) )

	def process( self, scene=None ):
		if not self.enabled:
			self.processed = True
			return

		if scene is None:
			scene = bpy.context.scene
		self.scene = scene
		self.process_hook()
		self.processed = True

		if self.automatic_fix:
			self.automatic_fix_hook()
			self.scene.update()

	def error(self, ob=None, subob=None, message=None, type=None, data=None ):
		error = ValidationMessage( ob, subob, message, parent=self.id(), type=type, data=data )
		self.errors.append( error )

	def warning(self, ob=None, subob=None, message=None, type=None, data=None ):
		warning = ValidationMessage( ob, subob, message, parent=self.id(), 
									type=type, data=data, error=False )
		self.warnings.append( warning )

	def get_objects( self, type=None ):
		if self.scene and len(self.scene.objects):
			if type:
				return [ x for x in self.scene.objects if x.type == type ]
			return [ x for x in self.scene.objects ]
		return []

	def is_valid( self ):
		if not self.processed:
			raise BVNotProcessed
		return len( self.errors ) == 0

	def has_warnings( self ):
		if not self.processed:
			raise BVNotProcessed
		return len( self.warnings ) == 0

	def id( self ):
		return self.__class__.__name__

	def process_hook( self ):
		raise BVInvalidSubclass( "BaseValidator::process_hook not overridden." )

	def automatic_fix_hook( self ):
		print( "-- {}::automatic_fix_hook not properly overridden.".format(self.id()) )
