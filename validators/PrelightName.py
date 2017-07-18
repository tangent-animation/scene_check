import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class PrelightName(BaseValidator):
	'''
	* Makes sure that a properly-named Prelight group exists in the file
	'''

	prelight_regex = re.compile( r"grp\.([0-9]{3})\.(prelight_[A-Za-z0-9\_]+)\.([0-9]{3})" )

	def __init__(self):
		super(PrelightName, self).__init__()

	def process_hook( self ):
		prelight_groups = []

		for group in bpy.data.groups:
			match = self.prelight_regex.match( group.name )
			if match:
				prelight_groups.append( group.name )

		if not len( prelight_groups ):
			self.error(
				type='PRELIGHT:GROUP',
				message='File is missing a Prelight group.'
			)
