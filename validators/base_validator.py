import os
import bpy
import bmesh
from bpy import ops

## ----------------------------------------------------------------------
class BVException(Exception): pass
class BVInvalidSubclass(BVException): pass
class BVNotProcessed(BVException): pass


## ----------------------------------------------------------------------
def update_view():
	bpy.context.scene.objects.active = bpy.context.scene.objects.active

## ----------------------------------------------------------------------
def get_editors( type ):
	editors = []

	for area in bpy.context.screen.areas:
		if area.type == type:
			editors.append(area)
	
	return editors

## ----------------------------------------------------------------------
def get_view3ds():
	return get_editors( 'VIEW_3D' )

## ----------------------------------------------------------------------
def get_image_editors():
	return get_editors( 'IMAGE_EDITOR' )

## ----------------------------------------------------------------------
def sf_null(self):
	pass

## ----------------------------------------------------------------------
def sf_object(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return

	for item in scene.objects:
		vis = item.hide
		item.hide = False
		item.select = False
		item.hide = vis

	ob.hide        = False
	ob.hide_select = False
	ob.select      = True

	scene.objects.active = ob
	scene.update()
	update_view()


## ----------------------------------------------------------------------
def sf_image(self):
	images = bpy.context.images

	try:
		image = images[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent image {}.'.format(self.parent, self.ob) )
		return

	## SHOTGUN BLAST
	for ed in get_image_editors:
		ed.image = image

## ----------------------------------------------------------------------
def sf_non_manifold(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return	

	if not ob.type == 'MESH':
		raise ValueError( 'sf_verts: attempted to run on non-mesh object {}.'.format(self.ob) )

	if not self.data or not len(self.data):
		raise ValueError( 'sf_verts({}): Attempted to select verts with no data (object {}).'
						  .format(self.parent, self.ob) )

	## select object first
	sf_object( self )

	ops.object.mode_set( mode='OBJECT' )
	ops.object.mode_set( mode='EDIT' )
	ops.mesh.select_mode( use_extend=False, use_expand=False, type='VERT')
	ops.mesh.select_all( action='DESELECT' )

	ops.mesh.select_non_manifold( extend=False, use_boundary=False )

	update_view()


## ----------------------------------------------------------------------
def sf_verts(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return	

	if not ob.type == 'MESH':
		raise ValueError( 'sf_verts: attempted to run on non-mesh object {}.'.format(self.ob) )

	## select object first
	sf_object( self )

	ops.object.mode_set( mode='OBJECT' )
	ops.object.mode_set( mode='EDIT' )
	ops.mesh.select_mode( use_extend=False, use_expand=False, type='VERT')
	ops.mesh.select_all( action='DESELECT' )

	bm = bmesh.new()
	bm.from_mesh( ob.data )
	bm.vertices.ensure_lookup_table()

	for index in self.data:
		bm.vertices[index].select = True

	update_view()


## ----------------------------------------------------------------------
def sf_edges(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return	

	if not ob.type == 'MESH':
		raise ValueError( 'sf_edges: attempted to run on non-mesh object {}.'.format(self.ob) )

	## select object first
	sf_object( self )

	ops.object.mode_set( mode='OBJECT' )
	ops.object.mode_set( mode='EDIT' )
	ops.mesh.select_mode( use_extend=False, use_expand=False, type='EDGE')
	ops.mesh.select_all( action='DESELECT' )

	bm = bmesh.new()
	bm.from_mesh( ob.data )
	bm.edges.ensure_lookup_table()

	for index in self.data:
		bm.edges[index].select = True

	update_view()

## ----------------------------------------------------------------------
def sf_faces(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return	

	if not ob.type == 'MESH':
		raise ValueError( 'sf_faces: attempted to run on non-mesh object {}.'.format(self.ob) )

	## select object first
	sf_object( self )

	ops.object.mode_set( mode='OBJECT' )
	ops.object.mode_set( mode='EDIT' )

	update_view()

	ops.mesh.select_mode( use_extend=False, use_expand=False, type='FACE')

	bm = bmesh.new()
	bm.from_mesh( ob.data )
	bm.faces.ensure_lookup_table()

	for index, face in enumerate(bm.faces):
		if index in self.data:
			face.select = True
		else:
			face.select = False

	ops.object.mode_set( mode='OBJECT' )
	bm.to_mesh( ob.data )
	ops.object.mode_set( mode='EDIT' )
	update_view()


## ----------------------------------------------------------------------
select_functions =  {
	'null'         : sf_null,
	'object'       : sf_object,
	'image'        : sf_image,
	'verts'        : sf_verts,
	'edges'        : sf_edges,
	'faces'        : sf_faces,
	'non_manifold' : sf_non_manifold,
}

## ----------------------------------------------------------------------
class ValidationMessage( object ):
	'''
	When a Validator generates an error or a warning,
	this class holds the information on the error like
	which object it occurred on, any sub-objects or
	components, an optional function to select the
	offending object, and a human-readable message.

	Should not be instantiated outside of 
	'''

	def __init__( self, ob, subob, message, parent=None, 
					type=None, data=None, error=True, select_func=None ):
		self.ob = ob
		self.subob = subob
		self.message = message
		self.parent = parent if parent else Error
		self._type = type
		self.data = data
		self.is_error = error
		self.select_func = sf_null

	def __repr__(self):
		msg = "<< {}".format( "Error " if self.is_error else "Warning " )
		if self.type:
			msg += "Type: %s" % str( self.type )
		if self.ob:
			msg += "\n\tObject: %s" % self.ob
		if self.subob:
			msg += " Subob: %s" % str( self.subob )

		msg += "\n\t{}: {}".format( self.parent, self.message )
		msg += " >>"
		return msg

	@property
	def type( self ):
		return '' if self._type is None else self._type

	def set_select_func(self, func_name):
		if func_name is None:
			self.select_func = sf_null

		elif not func_name in select_functions.keys():
			raise ValueError( ('ValidationMessage.select_func: can only be set to '
							  'functions, None, and strings. Found {}.  Valid strings: {}.')
							  .format( func_name, ', '.join(select_functions.keys()))
							)
		else:
			self.select_func = select_functions[func_name]

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

	def error(self, ob=None, subob=None, message=None, type=None, data=None, select_func=None ):
		error = ValidationMessage( ob, subob, message, parent=self.id(),
								   type=type, data=data )
		error.set_select_func( select_func )
		self.errors.append( error )

	def warning(self, ob=None, subob=None, message=None, type=None, data=None, select_func=None ):
		warning = ValidationMessage( ob, subob, message, parent=self.id(), 
									 type=type, data=data, error=False, select_func=select_func )
		warning.set_select_func( select_func )
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
