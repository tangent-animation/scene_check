import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigArmatureNCR(BaseValidator):
	'''
	Check for visibility on non-control armatures (they should be hidden).
	'''

	automatic_fix = True

	def __init__(self):
		super(RigArmatureNCR, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		for arm in armatures:
			if arm.name.startswith('ncr.'):
				if not arm.hide or not arm.hide_select or not arm.hide_render:
					self.error(
						ob=arm,
						type='ncr_hide',
						message='NCR Armature {} is not properly hidden.'.format( arm.name )
					)


	def automatic_fix_hook( self ):
		for error in self.errors:
			if error.type == 'ncr_hide':
				error.ob.hide        = True
				error.ob.hide_select = True
				error.ob.hide_render = True
				print( "+ Automatically fixed bendy for control bone {}::{}.".format(error.ob.name, error.subob) )

