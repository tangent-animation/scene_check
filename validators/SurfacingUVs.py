import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class SurfacingUVs(BaseValidator):
	'''
	Checks to make sure that each mesh
	has UVs, and that it 	
	'''

	def __init__(self):
		super(SurfacingUVs, self).__init__()

	def process_hook( self ):
		valid_names = { 'vtx','def','shp','deform_mesh','hair','surfacing' }

		for item in self.get_objects(type='MESH'):
			if len( item.data.uv_layers ):
				for layer in item.data.uv_layers:
					if not layer.name.startswith('uvs'):
						self.error(
							type='SURFACE:UVS NAME',
							message=('Mesh "{}" UV Set "{}": Name does not conform to show standards.')
									.format( item.name, layer.name )
						)
			else:
				self.error(
					type='SURFACE:UVS NONE',
					message=('Mesh "{}" Vertex Group "{}": Name does not conform to show standards.')
							.format( item.name, group.name )
				)


