import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class Scene(BaseValidator):
	'''
	* Checks for presence excess scenes in the file.
	'''

	scene_name_regex = re.compile( r"[0-9]{3}\.[0-9]{4}\.t[0-9]+" )

	def __init__(self):
		super(Scene, self).__init__()

	def process_hook( self ):
		self.master_scene = None

		self.scenes = []

		for scene in bpy.data.scenes:
			match = self.scene_name_regex.match( scene.name )
			if match:
				if self.master_scene:
					self.error(
						ob=scene.name,
						type='SCENE:EXTRAS',
						message=( 'Scene "{}" is an extra that may need removal.'
								.format(scene.name) )
					)
				else:
					self.master_scene = scene.name
			else:
				self.error(
					ob=scene.name,
					type='SCENE:INVALID NAME',
					message=( 'Scene "{}" has an invalid name and may be an extra needing removal.'
							.format(scene.name) )
				)


