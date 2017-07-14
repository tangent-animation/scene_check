import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class AssetLibraries(BaseValidator):
	'''
	Validate asset libraries:
	* Make sure no paths are absolute.
	'''

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

				## the fix here is very specific to the show
				## need to change this path if it's a different show.

				base_path     = 'T:/Projects/0053_7723/'
			
				path      = lib.filepath
				abspath   = os.path.abspath( bpy.path.abspath(path) )
				file_root = os.path.dirname( bpy.path.abspath(bpy.data.filepath) )
				
				try:
					relative_path = os.path.relpath( abspath, file_root )

					fix_code = (
						'import os\n'
						'lib  = bpy.data.libraries["{}"]\n'
						'path = "{}"\n'
						'lib.filepath = "//" + path\n'
						.format( lib.name, relative_path )
					)

					self.auto_fix_last_error(
						fix=fix_code,
						message=(
							'Change library "{}" to use a relative path.'
							.format(lib.name)
						)	
					)
				except:
					print( '-- File "{}" could not be made relative-- different drives.'.format(lib.filepath) )

