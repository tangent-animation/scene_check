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
		for item in [ x for x in self.get_objects(type='MESH') 
						if not x.name.startswith('shape')
						and not x.name.count('_proxy')
						and not x.name.count('mesh_deform') ]:
			if len( item.data.uv_layers ):
				for layer in item.data.uv_layers:
					if not layer.name.startswith('uvs'):
						ob=item,
						self.error(
							type='SURFACE:UVS NAME',
							message=('Mesh "{}" UV Set "{}": Name does not conform to show standards.')
									.format( item.name, layer.name )
						)
			else:
				self.error(
					ob=item,
					type='SURFACE:UVS NONE',
					message=('Mesh "{}" has no UVs.')
							.format( item.name )
				)


