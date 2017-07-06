import re
import os
from functools import partial

import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class ObjectTempGeometry(BaseValidator):
	'''
	* Checks for temporary geometry in animated scenes.
	'''

	automatic_fix = True

	def __init__(self):
		super(ObjectTempGeometry, self).__init__()
		self.temp_objects = []

	def process_hook( self ):
		self.temp_objects = [ x for x in bpy.context.scene.objects if 
						 not x.library and x.type in {'MESH','CURVE'} and
						 not (x.parent and x.parent.type == 'ARMATURE') ]

		scene_temp_name = self.scene.name + "__TEMP"

		for item in self.temp_objects:
			parent = item.parent
			if ( (not parent or not parent.name == scene_temp_name) and 
				not ('shape.' in item.name or 'shp.' in item.name) ):
				self.error(
					ob=item.name,
					select_func='object',
					type="GENERAL:OBJECT TEMPORARY",
					message=( 'Temporary Object "{}" found in scene.' )
						.format( item.name )
				)

				fix_code = (
					'ob = bpy.data.objects[ "{}" ]\n'
					'bpy.context.scene.objects.unlink( ob )'
				).format( item.name )

				self.auto_fix_last_error(
					fix_code,
					message='Remove temporary object {}'.format( item.name )
				)

	# def automatic_fix_hook(self):
	# 	scene = bpy.context.scene

	# 	for error in self.errors:
	# 		ob = bpy.data.objects[ error.ob ]
	# 		bpy.context.scene.objects.unlink( ob )
