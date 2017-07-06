import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigBoneLocking( BaseValidator ):
	'''
	Checks for and bone locks on non-control bones in all armatures,
	providing automatic fixes for improperly locked bones.
	'''

	automatic_fix = True
	regex = re.compile( r"^(ctl)\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

	def __init__(self):
		super(RigBoneLocking, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		for arm in armatures:
			for bone in arm.pose.bones:
				## process all non-control bones
				match = self.regex.match( bone.name )
				if not match:
					total = []
					for index in range(3):
						for attr in bone.lock_location, bone.lock_rotation, bone.lock_scale:
							total.append( attr[index] )

					if not sum(total) == 9:
						self.warning( ob=arm.name, subob=bone.name,
							type='RIG: BONE LOCK',
							select_func='armature_bone',
							message="{}::'{}' non-control bone not properly locked."
								.format(arm.name, bone.name) )

						fix_code = (
							'bone = bpy.data.objects["{}"].pose.bones["{}"]\n'
							'try:\n'
							'\tbone.lock_location = [True] * 3\n'
							'\tbone.lock_rotation = [True] * 3\n'
							'\tbone.lock_scale    = [True] * 3\n'
							'except AttributeError:\n'
							'\tpass'
						).format( arm.name, bone.name )

						self.auto_fix_last_warning(
							fix_code,
							message='Lock non-control bone "{}".'.format( bone.name )
						)

		self.processed = True
