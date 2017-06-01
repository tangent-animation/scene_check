import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class ModelTransform(BaseValidator):
	'''
	Checks that the transform values on all mesh
	objects are zero'd, and that the rotate order
	is properly set
	'''
	def __init__(self):
		super(ModelTransform, self).__init__()

	def process_hook( self ):
		rejected_orders = {
				'QUATERNION',
				'AXIS_ANGLE'
				# 'XYZ', 'XZY', 'YXZ',
				# 'YZX', 'ZXY', 'ZYX'
			}

		for item in self.get_objects( type='MESH' ):
			if not sum( item.location ) == 0.0:
				self.error(
					ob=item,
					type='MODEL:TRANSFORM LOCATION',
					message=("Mesh {}: object location should be (0,0,0).")
							.format( item.name )
				)

			if not sum( item.rotation_euler ) == 0.0:
				self.error(
					ob=item,
					type='MODEL:TRANSFORM ROTATION',
					message=("Mesh {}: object rotation should be (0,0,0).")
							.format( item.name )
				)

			if not sum( item.scale ) == 0.0:
				self.error(
					ob=item,
					type='MODEL:TRANSFORM SCALE',
					message=("Mesh {}: object scale should be (1.0,1.0,1.0).")
							.format( item.name )
				)

			if item.rotation_mode in rejected_orders:
				self.error(
					ob=item,
					type='MODEL:TRANSFORM ROTATION MODE',
					message=("Mesh {}: object rotation_mode should not be {}.")
							.format( item.name, item.rotation_mode )
				)
