import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class ModelShapeKeys(BaseValidator):
	'''
	Checks shape keys on mesh objects against
	show naming convention.
	'''

	def __init__(self):
		super(ModelShapeKeys, self).__init__()

	def process_hook( self ):
		for item in self.get_objects(type='MESH'):
			if not item.data.shape_keys:
				continue

			for key in item.data.shape_keys.key_blocks:
				if not key.name.startswith('shp') and not key.name == 'Basis':
					self.error(
						ob=item.name,
						subob=key.name,
						select_func='shape_keys',
						type='MODEL:SHAPE KEY NAME',
						message=("Mesh {} Shape {}: Name missing the 'shp' prefix.")
								.format( item.name, key.name )
					)
