import re
import os
from functools import partial

import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class ObjectPasses(BaseValidator):
	'''
	* Checks for object pass_index values greater than zero.
	'''

	automatic_fix = True

	def __init__(self):
		super(ObjectPasses, self).__init__()
		self.temp_objects = []

	def process_hook( self ):
		for item in bc.scene.objects:
			if item.pass_index == 0:
				self.error(
					ob=item.name,
					select_func='object',
					type="OBJECT: PASS INDEX",
					message=( 'Object "{}" has a pass index of 0.' )
						.format( item.name )
				)
