import bpy

from scene_check.validators.base_validator import BaseValidator

class RigShapeLocking(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigShapeLocking, self).__init__()

	def process_hook( self ):
		self.processed = True

	def automatic_fix_hook( self ):
		meshes = [ x for x in self.get_objects( type='MESH' ) if x.name.startswith('shape') ]
		for mesh in meshes:
			mesh.hide = mesh.hide_select = mesh.hide_render = True
			mesh.layers = ( [False] * 19 + [True] )
		print( "+ Automatic Shape Hiding: hid and layered {} rig shapes.".format(len(meshes)) )
