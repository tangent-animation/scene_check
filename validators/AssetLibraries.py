import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class AssetLibraries(BaseValidator):
	def __init__(self):
		super(AssetLibraries, self).__init__()

	def process_hook( self ):
		for lib in bpy.data.libraries:
			if not (lib.filepath and lib.filepath.startswith('//')):
				self.error(
					ob=lib.name,
					type='GENERAL:FILE PATHING',
					message=('Path is absolute. MUST be relative (library "{}").')
							 .format( lib.filepath )
				)

