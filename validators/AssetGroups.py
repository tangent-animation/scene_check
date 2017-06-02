import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class AssetGroups(BaseValidator):
	def __init__(self):
		super(AssetGroups, self).__init__()

	def process_hook( self ):
		if not len(bpy.data.groups):
			self.error(
				type="GENERAL:MISSING:NO GROUPS",
				message=("No asset group found. Should be: {}.")
					.format( 'grp.{}.000'.format(self.root_name) )
			)

		light_rig_names = { 'grp.colour_chart', 'grp.lights', 'grp.rig_cam', 'grp.spheres', 'grp.turntable' }

		for group in bpy.data.groups:
			if group.name in light_rig_names:
				self.error(
					ob=group.name,
					type="GENERAL:REVIEW RIG",
					message=("Light Rig found (group {}). Please remove.")
						.format( group.name )
				)

			if group.library:
				self.error(
					ob=group.name,
					type="GENERAL:LINKED",
					message=("A clean asset file should contain NO linked groups "
							"(Linked group {} found.)")
						.format( group.name )
				)
