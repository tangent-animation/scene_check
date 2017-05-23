import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigXray(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigXray, self).__init__()

	def process_hook( self ):
		for arm in self.get_objects( type='ARMATURE' ):
			if arm.show_x_ray:
				self.error( ob=arm, message="%s has XRay enabled." % arm.name )

	def automatic_fix_hook(self):
		for error in self.errors:
			error.ob.show_x_ray = False
			print( "\+ Disabled xray on %s." % error.ob.name )

