import re
import bpy

from scene_check.validators.base_validator import BaseValidator

class ScreenPurgeLayouts(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(ScreenPurgeLayouts, self).__init__()

	def process_hook( self ):

		regex = re.compile( r".*([A-Za-z0-9]+)\.([0-9]+)" )

		for screen in bpy.data.screens:
			if regex.match( screen.name ) and screen.users:
				self.error(
					ob=screen,
					message="Excess Screen found: {}.".format( screen.name )
				)

	def automatic_fix_hook(self):
		for error in self.errors:
			error.ob.user_clear()
			print( "\+ Marked excess scene {} for removal on save.".format(error.ob.name) )

