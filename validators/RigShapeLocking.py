import bpy

from scene_check.validators.base_validator import BaseValidator

class RigShapeLocking(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigShapeLocking, self).__init__()

	def process_hook( self ):
		meshes = [ x for x in self.get_objects( type='MESH' ) if x.name.startswith('shape') ]
		for mesh in meshes:
			if not mesh.hide or not mesh.hide_select or not mesh.hide_render:
				self.error(
					ob=mesh.name,
					select_func='object',
					type='RIG:SHAPE LOCKING',
					message='Shape object "{}" is not properly locked.'
							.format( mesh.name )
				)

				fix_code = (
					'ob = bpy.data.objects["{}"]\n'
					'ob.hide = ob.hide_select = ob.hide_render = True'
					
				).format( mesh.name )

				self.auto_fix_last_error(
					fix_code,
					message=(
						'Lock shape object "{}".'
						.format( mesh.name )
					)
				)

			layers = [ x for x in mesh.layers ]
			layer_sum = sum( layers )
			if not (layers[19] and layer_sum == 1) or not layer_sum == 1:
				self.error(
					ob=mesh.name,
					select_func='object',
					type='RIG:SHAPE LAYERS',
					message='Shape object "{}" does not have proper layers.'
							.format( mesh.name )
				)

				fix_code = (
					'ob = bpy.data.objects["{}"]\n'
					'ob.layers = ( [False] * 19 + [True] )'
				).format( mesh.name )

				self.auto_fix_last_error(
					fix_code,
					message=(
						'Set proper layers on shape object "{}".'
						.format( mesh.name )
					)
				)

		self.processed = True

	# def automatic_fix_hook( self ):
	# 	meshes = [ x for x in self.get_objects( type='MESH' ) if x.name.startswith('shape') ]
	# 	for mesh in meshes:
	# 		mesh.hide = mesh.hide_select = mesh.hide_render = True
	# 		mesh.layers = ( [False] * 19 + [True] )
	# 	print( "+ Automatic Shape Hiding: hid and layered {} rig shapes.".format(len(meshes)) )
