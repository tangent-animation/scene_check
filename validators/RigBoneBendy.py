import re
import os
import bpy

from validators.base_validator import BaseValidator

class RigBoneBendy(BaseValidator):
	def __init__(self):
		super(RigBoneBendy, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		regex = re.compile( r"^(def)\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		for arm in armatures:
			changed = 0
			for bone in arm.pose.bones:
				match = regex.match( bone.name )
				modified = False
				## process all non-control bones
				if not match:
					if bone.bone.bbone_segments > 1:
						self.error( ob=arm, subob=bone.name,
							message="{}::{}: Bone has bendy segments."
							.format(arm.name, bone.name)
							)
