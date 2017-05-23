import re
import os
import bpy

from validators.base_validator import BaseValidator

class RigVisibility(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigVisibility, self).__init__()

	def process_hook( self ):
		self.processed = True

	def automatic_fix_hook(self):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		regex = re.compile( r"^(ctl)\.([A-Za-z\_]+)(_tweak|_secondary)\.([CLR])\.([0-9]{3})$" )

		for arm in armatures:
			changed = 0
			for bone in arm.pose.bones:
				match = regex.match( bone.name )
				modified = False
				## process all non-control bones
				if match:
					if not bone.bone.hide:
						bone.bone.hide = True
						modified = True
				if modified:
					changed += 1
			if changed:
				print( "+ Automatically hid secondary / tweaker bones on {} ({} bones hidden).".format(arm.name, changed) )
