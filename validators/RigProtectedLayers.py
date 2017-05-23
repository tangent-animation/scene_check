import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigProtectedLayers(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigProtectedLayers, self).__init__()

	def process_hook( self ):
		pass

	def automatic_fix_hook(self):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		for arm in armatures:
			arm.data.layers_protected = ([False] * 32)
		print( "+ Automatically hid protected layers ({} armatures).".format(len(armatures)) )
