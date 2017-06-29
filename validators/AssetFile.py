import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

file_regex = re.compile( "(chr|prp|set)([0-9]{3})(\_)([a-z0-9\_]+)(\.)?(v[0-9]+)?(\.blend)" )

class AssetFile(BaseValidator):
	'''
	Basic checks that work at the file level:
	* "Auto execute scripts" should be enabled.
	* "Use relative paths" should be disabled.
	* "Use Autopack" should be disabled.
	* render.use_simplify should be disabled.
	* File name should conform to show style and be in the right place
	* Checks for excess text data blocks
	* Make sure the system units isn't imperial.
	'''

	def __init__(self):
		super(AssetFile, self).__init__()

	def process_hook( self ):
		if ( bp.system.use_scripts_auto_execute == False ):
			self.error(	type='GENERAL:PREFS AUTORUN',
				message=("Ensure Autorun Scripts is turned ON "
						 "in User Preferences.")
			)

		if ( bp.filepaths.use_relative_paths == False ):
			self.error(	type='GENERAL:PREFS RELATIVE',
				message=("Relative Paths is turned OFF. Relative "
						"Paths must be turned ON in User Preferences")
			)

		if ( bd.use_autopack ):
			self.error(	type='GENERAL:PREFS AUTOPACK',
				message=("Autopack should be turned OFF.  You may "
						"need to unpack any packed data if this "
						"file has been saved with Autopack enabled.")
			)

		if bc.scene.render.use_simplify:
			self.error(	type='GENERAL:SIMPLIFY',
				message=("Simplify is turned ON.  It must be "
						"turned OFF for asset publishing.")
			)
	
		render_layer_count = len( bc.scene.render.layers )
		if render_layer_count > 1:
			self.error(	type='GENERAL:RENDER LAYERS',
				message=("Please clean up render layers. "
						"There must be only one at the "
						"asset level ({} found).").format( render_layer_count )
			)
	
		match = file_regex.match( self.file_name )
		if not match:
			self.error(	type='GENERAL:FILE NAME',
				message=('File name "{}" does not conform to '
						'show format: [typ][000]_[token].blend')
						.format( self.file_name )
			)

		if not 'T:/Projects/0053_7723/asset' in self.dir_name:
			self.error(	type='GENERAL:FILE DIR',
				message=('File appears to be saved in an '
						'invalid location: "{}".')
						.format( self.dir_name )
			)
		else:
			split = self.dir_name.split('/')

			if not self.root_name in split:
				self.error(	type='GENERAL:FILE DIR',
					message=('Asset / Folder name mismatch. '
							'Please check that asset name matches '
							'folder name {}/{}.blend')
							.format( dir_name, self.root_name )
				)

		bad_text_blocks = 0
		accepted_text_names = { self.log_name, ".snapshot" }
		for text in bpy.data.texts:
			if not text.name in accepted_text_names:
				bad_text_blocks += 1

		if bad_text_blocks:
			self.error( type='GENERAL:FILE TEXT DATA',
				message=('All text files should be removed '
						 'from the Text Editor (found {:d} extra).')
						 .format(bad_text_blocks)
			)

		system_units = bc.scene.unit_settings.system
		if system_units not in { 'NONE', 'METRIC' }:
			self.error( type='GENERAL:FILE SYSTEM UNIT SCALE',
				message=('Should be None or Metric, found "{}".')
						 .format(system_units)
			)

