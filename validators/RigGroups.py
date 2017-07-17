import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigGroups(BaseValidator):
	"""
	* Makes sure objects in a rig are properly
	grouped for linking.
	"""

	def __init__(self):
		super(RigGroups, self).__init__()

	def process_hook( self ):
		base_name = os.path.basename( bpy.data.filepath ).replace('.blend','')
		char_name = base_name.rpartition('_')[2]

		base_group_name = 'grp.{}.000'.format( base_name )
		if not base_group_name in bpy.data.groups:
			self.error( message="Base Group is missing ({})."
							.format(base_group_name) )

		base_group_low_name = 'grp.{}_low.000'.format( base_name )
		if not base_group_low_name in bpy.data.groups:
			self.error( message="Base Low Group is missing ({})."
							.format(base_group_low_name) )

		base_group_names = { base_group_name, base_group_low_name }

		regex_low = re.compile( r"(grp)\.([A-Za-z0-9_]+)_low\.([0-9]{3})" )
		regex = re.compile( r"(grp)\.([A-Za-z0-9_]+)\.([0-9]{3})" )

		for group in bpy.data.groups:
			if group.name in base_group_names:
				continue

			low_match = regex_low.match( group.name )
			match = regex.match( group.name )

			if low_match is None and match is None:
				self.error( message="Group {} does not match naming convention."
							.format(group.name) )

			elif match and not low_match:
				low_name = '.'.join( ['grp', match.group(2) + '_low', match.group(3)] )
				if not low_name in bpy.data.groups:
					self.error( message="Group {} has no matching low group '{}'."
								.format(group.name, low_name) )




