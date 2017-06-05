import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigBoneLocking(BaseValidator):
	'''
	Checks for and automatically fixes bone locks on
	non-control bones in all armatures.
	'''

	automatic_fix = True

	def __init__(self):
		super(RigBoneLocking, self).__init__()

	def process_hook( self ):
		self.processed = True

	def automatic_fix_hook(self):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		regex = re.compile( r"^(ctl)\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		for arm in armatures:
			changed = 0
			for bone in arm.pose.bones:
				match = regex.match( bone.name )
				modified = False
				## process all non-control bones
				if not match:
					for attr in bone.lock_location, bone.lock_rotation, bone.lock_scale:
						for index in range(3):
							if not attr[index]:
								attr[index] = True
								modified = True
				if modified:
					changed += 1
			if changed:
				print( "+ Automatically processed bone locks on {} ({} / {} bones changed).".format(arm.name, changed, len(arm.pose.bones)) )
