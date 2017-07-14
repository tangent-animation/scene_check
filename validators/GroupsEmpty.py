import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

file_regex = re.compile( "(chr|prp|set)([0-9]{3})(\_)([a-z0-9\_]+)(\.)?(v[0-9]+)?(\.blend)" )

class GroupsEmpty( BaseValidator ):
	"""
	Checks for and removes groups that live in the Blender file
	but are not connected to anything in the current scene.
	"""

	def __init__(self):
		super(GroupsEmpty, self).__init__()

	def process_hook( self ):
		scene = bpy.context.scene

		for group in bpy.data.groups:
			result = 0
			for ob in group.objects:
				if ob in scene.objects:
					result += 1

			if result == 0:
				self.error(
					ob=group.name,
					type='GROUP:EMPTY',
					message=('Group "{}" is in Blender file but '
							'not attached to a scene object.'
							.format(group.name))
				)

				fix_code = (
					'bpy.data.groups.remove( bpy.data.groups["{}"] )\n'
					.format(group.name)
				)

				self.auto_fix_last_error(
					fix=fix_code,
					message=('Remove empty group "{}"'.format(group.name))
				)
