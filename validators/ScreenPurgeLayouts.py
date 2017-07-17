import re
import bpy

from scene_check.validators.base_validator import BaseValidator

class ScreenPurgeLayouts(BaseValidator):
	"""
	* Checks for excess layouts in the Blender file.
	"""

	automatic_fix = True

	def __init__(self):
		super(ScreenPurgeLayouts, self).__init__()

	def process_hook( self ):

		regex = re.compile( r".*([A-Za-z0-9]+)\.([0-9]+)" )

		for screen in bpy.data.screens:
			if regex.match( screen.name ) and screen.users:
				self.error(
					ob=screen.name,
					type='SCREEN:EXCESS',
					message="Excess Screen found: {}.".format( screen.name )
				)

				fix_code = (
					'screen = bpy.data.screens["{}"]\n'
					'screen.user_clear()\n'
				).format( screen.name )

				self.auto_fix_last_error(
					fix_code,
					message='Mark screen layout "{}" for deletion on save.'.format( screen.name )
				)
