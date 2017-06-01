import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigArmatureProxy(BaseValidator):
	def __init__(self):
		super(RigArmatureProxy, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		for arm in armatures:
			if '_proxy' in arm.name:
				self.error(
					ob=arm,
					type='RIGGING:PROXY',
					message='Proxy Armature found: {} (should not exist in file).'.format( arm.name )
				)

