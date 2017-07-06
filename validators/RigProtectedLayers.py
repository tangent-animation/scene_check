import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigProtectedLayers( BaseValidator ):
	automatic_fix = True

	def __init__(self):
		super( RigProtectedLayers, self ).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		if not len(armatures):
			return

		for arm in armatures:
			total = sum( x for x in arm.data.layers_protected )
			if not total == 32:
				self.error(
					ob=arm.name,
					select_func='object',
					type='ARMATURE:PROTECTED LAYERS',
					message='Armature "{}" does not have all its protected layers set.'
							.format(arm.name)
				)

				fix_code = (
					'bpy.data.objects["{}"].data.layers_protected = ( [True] * 32 )'
					.format( arm.name )
				)

				self.auto_fix_last_error(
					fix_code,
					message=(
						'Set protected layers on armature "{}".'
						.format( arm.name )
					)
				)

		self.processed = True

	# def automatic_fix_hook(self):
	# 	armatures = self.get_objects( type='ARMATURE' )
	# 	if not len(armatures):
	# 		return

	# 	for arm in armatures:
	# 		arm.data.layers_protected = ([False] * 32)

	# 	print( "+ Automatically hid protected layers ({} armatures).".format(len(armatures)) )
