import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigBoneBendy(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigBoneBendy, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		regex = re.compile( r"^([a-z]{3})\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		for arm in armatures:
			changed = 0
			for bone in arm.pose.bones:
				match = regex.match( bone.name )
				modified = False
				## process all non-control bones
				if match:
					if bone.bone.bbone_segments > 1:
						if bone.name.startswith('ctl.'):
							self.error(
								ob=arm.name,
								subob=bone.name,
								select_func='armature_bone',
								type='control',
								message="{}::{}: Control Bone has bendy segments."
								.format(arm.name, bone.name)
								)
						else:
							if not bone.name.startswith('def.'):
								self.error(
									ob=arm.name,
									subob=bone.name,
									select_func='armature_bone',
									message="{}::{}: Non-deform bone has bendy segments."
									.format(arm.name, bone.name)
									)

	def automatic_fix_hook( self ):
		'''
		for error in self.errors:
			if error.type == 'control':
				error.ob.pose.bones[error.subob].bone.bbone_segments = 1
				print( "+ Automatically fixed bendy for control bone {}::{}.".format(error.ob.name, error.subob) )
		'''
		pass
