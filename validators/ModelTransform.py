import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class ModelTransform(BaseValidator):
	'''
	Checks shape keys on mesh objects against
	show naming convention.
	'''

	def __init__(self):
		super(ModelTransform, self).__init__()

	def process_hook( self ):
		for item in self.get_objects( type='MESH' ):
			if not sum( item.location ) == 0.0:
				self.error(
					type='MODEL:TRANSFORM LOCATION',
					message=("Mesh {}: object location should be (0,0,0).")
							.format( item.name )
				)

			if not sum( item.rotation_euler ) == 0.0:
				self.error(
					type='MODEL:TRANSFORM ROTATION',
					message=("Mesh {}: object rotation should be (0,0,0).")
							.format( item.name )
				)

