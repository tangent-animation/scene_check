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
			if not lib.filepath or not os.path.exists( os.path.abspath(bpy.path.abspath(lib.filepath)) ):
				self.error(
					ob=lib.name,
					type='GENERAL:INVALID FILE PATH',
					message=('Path is either not set or broken on Library "{}" ("{}").')
							 .format( lib.name, lib.filepath )
				)

			elif not lib.filepath.startswith( '//' ):
				self.error(
					ob=lib.name,
					type='GENERAL:FILE PATHING RELATIVE',
					message=('Path is absolute. MUST be relative (library "{}").')
							 .format( lib.filepath )
				)

				## the fix here is very specific to the show
				## need to change this path if it's a different show.

				base_path     = 'T:/Projects/0053_7723/'
			
				path      = lib.filepath
				abspath   = os.path.abspath( bpy.path.abspath(path) )
				file_root = os.path.dirname( bpy.path.abspath(bpy.data.filepath) )
				
				print( "Abspath: {}".format(abspath) )
				print( "FileRoot: {}".format(file_root) )

				try:
					relative_path = os.path.relpath( abspath, file_root ).replace('\\','/')

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

			if lib.filepath.count('sandbox'):
				self.error(
					ob=lib.name,
					type='GENERAL:SANDBOX PATH',
					message=('Path for library "{}" points to a sandbox file ("{}").')
							 .format( lib.name, lib.filepath )
				)

