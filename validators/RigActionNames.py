import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigActionNames(BaseValidator):
	def __init__(self):
		super(RigActionNames, self).__init__()

	def process_hook( self ):
		for action in bpy.data.actions:
			if not action.name.startswith('DO_NOT_TOUCH'):
				self.error( 
					ob=action, 
					message='Action named "{}" should start with "DO_NOT_TOUCH"'.format(action.name)
				)
