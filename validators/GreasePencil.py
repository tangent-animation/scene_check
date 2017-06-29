import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class GreasePencil(BaseValidator):
	'''
	* Checks for and removes excess grease pencil objects and data from the scene
	'''

	automatic_fix = True

	def __init__(self):
		super(GreasePencil, self).__init__()
		self.temp_objects = []

	def process_hook( self ):
		self.pencil_objects = set()

		for item in [ x for x in bpy.context.scene.objects if x.grease_pencil ]:
			self.error(
				ob=item.name,
				subob=item.grease_pencil.name,
				select_func='object',
				type='OBJECT:GREASE PENCIL',
				message=( 'Object {} has grease pencil data {}.'
						.format(item.name, item.grease_pencil.name) )
			)

			self.pencil_objects.add( item.grease_pencil.name )

		if self.scene.grease_pencil:
			self.error(
				ob=self.scene.name,
				subob=self.scene.grease_pencil.name,
				type='SCENE:GREASE PENCIL',
				message=( 'Scene {} has grease pencil data "{}".'
							.format(self.scene.name, self.scene.grease_pencil.name) )
			)

			self.pencil_objects.add( self.scene.grease_pencil.name )

		for item in bpy.data.grease_pencil:
			if not item.name in self.pencil_objects:
				## putting it into ob and subob here to make
				## the auto-fix loop simpler
				self.error(
					ob=item.name,
					subob=item.name,
					type='GREASE PENCIL',
					message=( 'Loose grease pencil data "{}".'
								.format(item.name) )
				)

			self.pencil_objects.add( item.name )

	def automatic_fix_hook(self):
		for error in self.errors:
			gp = bpy.data.grease_pencil[error.subob]
			bpy.data.grease_pencil.remove( gp )