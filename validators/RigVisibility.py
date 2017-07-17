import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigVisibility(BaseValidator):
	"""
	* Checks for non-control bones that 
	should be hidden.
	"""

	automatic_fix = True

	def __init__(self):
		super(RigVisibility, self).__init__()

	def process_hook( self ):

		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		regex = re.compile( r"^(ctl)\.([A-Za-z\_]+)(_tweak|_secondary)\.([CLR])\.([0-9]{3})$" )

		for arm in armatures:
			for bone in arm.pose.bones:
				## process all non-control bones
				match = regex.match( bone.name )
				if match and not bone.bone.hide:
					self.error(
						ob=arm.name,
						subob=bone.name,
						select_func='armature_bone',
						type='RIG:BONE VISIBILITY',
						message='Bone "{}::{}" should be hidden.'
								.format( arm.name, bone.name )
					)

					fix_code = (
						'bone = bpy.data.objects["{}"].data.bones["{}"]\n'
						'bone.hide = True'
					).format( arm.name, bone.name )

					self.auto_fix_last_error(
						fix_code,
						message=(
							'Hide bone "{}::{}".'
							.format( arm.name, bone.name )
						)
					)

		self.processed = True
