import os, re
from copy import deepcopy
import bpy
import bmesh
from bpy import ops

## ----------------------------------------------------------------------
class BVException(Exception): pass
class BVInvalidSubclass(BVException): pass
class BVNotProcessed(BVException): pass
class BVObjectNotFound(BVException): pass


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
def get_spaces( type=None ):
	spaces = []
	for area in bpy.context.screen.areas:
		for space in area.spaces:
			if space.type == type or type is None:
				spaces.append( space )

	return( spaces )

## ----------------------------------------------------------------------
def get_properties_spaces():
	return get_spaces( 'PROPERTIES' )

## ----------------------------------------------------------------------
def get_view3d_editors():
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
	except Exception as e:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		raise e

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

	return ob


## ----------------------------------------------------------------------
def sf_action(self):
	pass


## ----------------------------------------------------------------------
def sf_armature_bone(self):
	ob = sf_object(self)

	if not ob.type == 'ARMATURE':
		raise ValueError( 'sf_armature_bone: attempted to run on non-armature object {}.'.format(self.ob) )

	ops.object.mode_set( mode='OBJECT' )
	ops.object.mode_set( mode='POSE' )
	ops.pose.select_all( action='DESELECT' )

	try:
		bone = ob.pose.bones[self.subob]
	except Exception as e:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		raise e

	bone.bone.select = True
	bone.bone.select_head = True
	bone.bone.select_tail = True

	ob.data.bones.active = bone.bone

	## sometimes the bone won't be visible because of bone layers
	## so flip the layer on
	layers = list(ob.data.layers)
	for index in range(len(layers)):
		layers[index] = layers[index] or bone.bone.layers[index]

	ob.data.layers = layers

	update_view()

	return ob, bone

## ----------------------------------------------------------------------
def sf_armature_constraint(self):
	ob, bone = sf_armature_bone(self)

	try:
		cnst = bone.constraints[self.data]
	except Exception as e:
		print( '-- {}: Attempted to select non-existent constraint {} on bone {}, armature {}.'
				.format(self.parent, self.data, bone.name, ob.name) )
		raise e

	properties = get_properties_spaces()
	for space in properties:
		try:
			space.context = 'BONE_CONSTRAINT'
		except:
			pass

	for constraint in bone.constraints:
		constraint.show_expanded = False

	cnst.show_expanded = True

	update_view()


## ----------------------------------------------------------------------
def sf_image(self):
	images = bpy.data.images

	try:
		image = images[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent image {}.'.format(self.parent, self.ob) )
		return

	## SHOTGUN BLAST
	for ed in get_image_editors():
		ed.spaces.active.image = image

	print( "Selected image " + image.name )

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

	## bugfix: make sure the damned thing is visible
	ob.hide = False

	ops.object.mode_set( mode='OBJECT' )
	ops.object.mode_set( mode='EDIT' )

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
	
	## bugfix: make sure the damned thing is visible
	scene.objects.active = ob
	update_view()

	ob.hide        = False
	ob.hide_select = False

	print('+ Selected {} face{} on object "{}".'
			.format( len(self.data), '' if len(self.data) == 1 else 's', ob.name )
		)
	try:
		ops.object.mode_set( mode='EDIT' )
	except:
		print("-- Unable to set edit mode (probably due to driven visibility or selection)")


## ----------------------------------------------------------------------
def sf_modifiers(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return

	if not ob.type == 'MESH':
		raise ValueError( 'sf_modifiers: attempted to run on non-mesh object {}.'.format(self.ob) )

	try:
		mod = ob.modifiers[self.subob]
	except:
		print( '-- {}: Attempted to select non-existent modifier {} on object {}.'
				.format(self.parent, self.subob, self.ob) )
		return

	## select object first
	sf_object( self )

	if self.data:
		if self.data in scene.objects:
			scene.objects[self.data].select = True

	properties = get_properties_spaces()
	for space in properties:
		try:
			space.context = 'MODIFIER'
		except:
			pass

	## Thought here is there's no way to actually "select" a modifier
	## so instead I'll minimize the others
	for item in ob.modifiers:
		item.show_expanded = False

	mod.show_expanded = True

	update_view()


## ----------------------------------------------------------------------
def sf_materials( self ):
	scene = bpy.context.scene

	## select object first
	ob = sf_object( self )

	if not ob.type == 'MESH':
		raise ValueError( 'sf_modifiers: attempted to run on non-mesh object {}.'.format(self.ob) )

	try:
		mat = ob.data.materials[self.subob]
	except Exception as e:
		print( '-- {}: Attempted to select non-existent material {} on object {}.'
				.format(self.parent, self.subob, self.ob) )
		raise e

	ob.active_material = mat

	properties = get_properties_spaces()
	for space in properties:
		try:
			space.context = 'MATERIAL'
		except:
			pass

	update_view()
	return(ob, mat)


## ----------------------------------------------------------------------
def sf_material_nodes(self):

	ob, mat = sf_materials( self )
	node_trees = get_spaces( type='NODE_TREE' )
	for space in node_trees:
		try:
			space.context = 'MATERIAL'
		except:
			pass

	nodes = mat.node_tree.nodes
	try:
		node = nodes[self.data]
	except Exception as e:
		print( '-- {}: Attempted to select non-existent node {} (object {}, material {}).'
				.format(self.parent, self.data, self.ob, self.subob) )
		raise e

	for item in nodes:
		item.select = False

	node.select = True
	print( "Selected {}".format(node.name) )
	update_view()


## ----------------------------------------------------------------------
def sf_data(self):
	scene = bpy.context.scene

	try:
		ob = scene.objects[self.ob]
	except:
		print( '-- {}: Attempted to select non-existent object {}.'.format(self.parent, self.ob) )
		return

	## select object first
	sf_object( self )

	properties = get_properties_spaces()
	for space in properties:
		try:
			space.context = 'DATA'
		except:
			pass

	update_view()
	return ob

## ----------------------------------------------------------------------
def sf_mesh_data(self):
	ob = sf_data(self)
	if not ob.type == 'MESH':
		raise ValueError( 'sf_mesh_data: attempted to run on non-mesh object {}.'.format(self.ob) )

	return ob


## ----------------------------------------------------------------------
def sf_mesh_uvs(self):
	ob = sf_mesh_data(self )

	uv_textures = ob.data.uv_textures if len(ob.data.uv_textures) else []
	if not self.subob in uv_textures:
		raise ValueError( ('sf_mesh_uvs: attempted to select non-existent '
						   'UV layer "{}" on mesh object {}.')
						   .format(self.subob, self.ob)
						)

	for index in range(len(uv_textures)):
		layer = uv_textures[index]
		print('layer "{}" >> subob "{}"'.format(layer.name, self.subob))
		if layer.name == self.subob:
			uv_textures.active_index = index
			uv_textures.active = layer
			break

	update_view()


## ----------------------------------------------------------------------
def sf_curve_data(self):
	ob = sf_data(self)
	if not ob.type == 'CURVE':
		raise ValueError( 'sf_curve_data: attempted to run on non-curve object {}.'.format(self.ob) )

	return ob

## ----------------------------------------------------------------------
def sf_shape_keys(self):
	scene = bpy.context.scene

	ob = sf_mesh_data(self)

	if not ob.data.shape_keys:
		print( '-- {}: Attempted to select shape key "{}" on object with no shape keys {}.'
				.format(self.parent, self.subob, self.ob) )
		return

	## key_blocks isn't iterable??
	keys = ob.data.shape_keys.key_blocks
	for index in range(len(keys)):
		if keys[index].name == self.subob:
			ob.active_shape_key_index = index
			break

	update_view()


## ----------------------------------------------------------------------
def sf_mesh_vertex_group(self):
	scene = bpy.context.scene

	ob = sf_mesh_data(self)

	## not iterable in script
	for index in range(len(ob.vertex_groups)):
		if ob.vertex_groups[index].name == self.subob:
			ob.vertex_groups.active_index = index
			break

	print( 'Selected "{}" on "{}" (index {})'.format(self.subob, self.ob, index) )
	update_view()


## ----------------------------------------------------------------------
select_functions =  {
	'null'                : sf_null,
	'object'              : sf_object,
	'image'               : sf_image,
	'verts'               : sf_verts,
	'edges'               : sf_edges,
	'faces'               : sf_faces,
	'non_manifold'        : sf_non_manifold,
	'modifiers'           : sf_modifiers,
	'data'         		  : sf_data,
	'mesh_data'           : sf_mesh_data,
	'curve_data'          : sf_curve_data,
	'shape_keys'          : sf_shape_keys,
	'mesh_vertex_group'   : sf_mesh_vertex_group,
	'materials'           : sf_materials,
	'material_nodes'      : sf_material_nodes,
	'mesh_uvs'            : sf_mesh_uvs,
	'armature_bone'       : sf_armature_bone,
	'armature_constraint' : sf_armature_constraint,
}

def get_select_func( name ):
	if not name in select_functions:
		raise ValueError( 'select_func "{}" does not exist.'.format(name) )
	return select_functions[name]


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

	def __init__( self, ob=None, subob=None, message=None, parent=None, 
					type=None, data=None, error=True, auto_fix=None, select_func=None ):
		self.ob          = ob
		self.subob       = subob
		self.message     = message
		self.parent      = parent
		self._type       = type
		self.data        = data
		self.is_error    = error
		self.select_func = 'null' if select_func is None else select_func
		self.auto_fix    = auto_fix

	def __repr__(self):
		msg = "<< {}".format( 'Auto Fix' if self.auto_fix else ("Error " if self.is_error else "Warning ") )
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

	def to_dict( self ):
		##TODO: error checking on None
		result = {
			'ob'          : self.ob,
			'subob'       : self.subob,
			'message'     : self.message,
			'parent'      : self.parent,
			'type'        : self.type,
			'data'        : self.data,
			'is_error'    : self.is_error,
			'select_func' : self.select_func,
		}

		return result

	def from_dict( self, value ):
		##TODO: error checking on None
		assert( isinstance(value, dict) )
		self.ob          = value['ob']
		self.subob       = value['subob']
		self.message     = value['message']
		self.parent      = value['parent']
		self._type       = value['type']
		self.data        = value['data']
		self.is_error    = value['is_error']
		self.select_func = value['select_func']

		## trick for comprehensions
		return self

	def copy( self ):
		return deepcopy( self )


## ----------------------------------------------------------------------
class BaseValidator( object ):
	enabled = True
	automatic_fix = False
	log_name = 'check_result_log.json'

	rig_regex   = re.compile( r"(con|rig|ncr)\.([A-Za-z0-9_]+)\.([0-9]{3})" )
	proxy_regex = re.compile( r"(grp)\.([A-Za-z0-9_]+)\.([0-9]{3})_proxy" )

	def __init__( self ):
		self.processed      = False
		self.auto_fixes     = []
		self.warnings       = []
		self.errors         = []
		self.file_full_path = bpy.path.abspath( bpy.data.filepath )
		self.dir_name       = os.path.dirname( self.file_full_path )
		self.file_name      = os.path.basename( self.file_full_path )
		self.root_name      = self.file_name.partition('.')[0]

		try:
			self.asset_type = self.root_name[:3]
		except:
			self.asset_type = 'unk'

	def __del__( self ):
		if not self.log_name in bpy.data.texts:
			log = bpy.data.texts.new( self.log_name )
		else:
			log = bpy.data.texts[ self.log_name ]

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

	def auto_fix_errors( self ):
		raise DeprecationWarning( 'This function is not meant to be called directly any more.' )
		if self.automatic_fix:
			self.automatic_fix_hook()
			self.scene.update()

	def error( self, ob=None, subob=None, message=None, type=None, data=None, select_func=None ):
		error = ValidationMessage( ob, subob, message, parent=self.id(),
								   type=type, data=data, select_func=select_func )
		self.errors.append( error )

	def warning( self, ob=None, subob=None, message=None, type=None, data=None, select_func=None ):
		warning = ValidationMessage( ob, subob, message, parent=self.id(), 
									 type=type, data=data, error=False, select_func=select_func )
		self.warnings.append( warning )

	def auto_fix( self, fix, ob=None, subob=None, message=None, type=None, data=None, select_func=None ):
		raise DeprecationWarning( "Don't use this." )

		if fix is None:
			raise ValueError('"fix" code must assigned.')

		auto_fix = ValidationMessage( ob, subob, message, parent=self.id(), 
								 type=type, data=data, error=False, 
								 auto_fix=fix, select_func=select_func )
		self.auto_fixes.append( auto_fix )

	def auto_fix_last_error( self, fix, message=None ):
		if fix is None:
			raise ValueError('"fix" code must assigned.')

		# print( "Converting error into auto-fix:\n{}\n\n".format(repr(self.errors[-1])) )

		auto_fix = self.errors[-1].copy()
		auto_fix.auto_fix = fix
		if message:
			auto_fix.message = message
		self.auto_fixes.append( auto_fix )

	def auto_fix_last_warning( self, fix, message=None ):
		if fix is None:
			raise ValueError('"fix" code must assigned.')

		# print( "Converting warning into auto-fix:\n{}\n\n".format(repr(self.warnings[-1])) )

		auto_fix = self.warnings[-1].copy()
		auto_fix.auto_fix = fix
		if message:
			auto_fix.message = message
		self.auto_fixes.append( auto_fix )

	def get_objects( self, type=None ):
		if self.scene and len(self.scene.objects):
			if type:
				return [ x for x in self.scene.objects if x.type == type ]
			return [ x for x in self.scene.objects ]
		return []

	def get_render_meshes( self ):
		return [ 
			x for x in self.get_objects(type='MESH')
				if not x.name.startswith('shape')
				and not x.name.count('_proxy')
				and not x.name.count('mesh_deform')
		]

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

