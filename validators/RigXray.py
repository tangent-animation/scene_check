import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigXray( BaseValidator ):
	"""
	* Checks that the Armature is not in XRay mode.
	"""

	automatic_fix = True

	def __init__(self):
		super(RigXray, self).__init__()

	def process_hook( self ):
		for arm in self.get_objects( type='ARMATURE' ):
			if arm.show_x_ray:
				self.error( 
					ob=arm.name,
					select_func='object',
					type='RIG:XRAY',
					message='Armature "{}" has XRay enabled.'.format( arm.name )
				)

				fix_code = (
					'arm = bpy.data.objects["{}"]\n'
					'arm.show_x_ray = False'
				).format( arm.name )

				self.auto_fix_last_error(
					fix_code,
					message='Disable XRay on Armature "{}".'.format( arm.name )
				)
