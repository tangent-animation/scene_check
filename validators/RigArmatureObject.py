import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigArmatureObject(BaseValidator):
	'''
	Makes sure that the armature's rotation mode is 
	properly set.
	'''

	def __init__(self):
		super(RigArmatureObject, self).__init__()

	def process_hook( self ):
		rejected_orders = {
				'QUATERNION',
				'AXIS_ANGLE'
				# 'XYZ', 'XZY', 'YXZ',
				# 'YZX', 'ZXY', 'ZYX'
			}

		armatures = self.get_objects( type='ARMATURE' )
		for item in armatures:
			if item.rotation_mode in rejected_orders:
				self.error(
					ob=item,
					type='RIGGING:TRANSFORM ROTATION MODE',
					message=("Armature {}: object rotation_mode should not be {}.")
							.format( item.name, item.rotation_mode )
				)
