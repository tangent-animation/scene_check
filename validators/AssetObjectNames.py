import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

# whitespace_regex = re.compile('(\t|\n|\r| )')

class AssetObjectNames(BaseValidator):
	def __init__(self):
		super(AssetObjectNames, self).__init__()

	def process_hook( self ):
		for item in self.get_objects():
			##!FIXME: Regex works online but not here; punting
			if ' ' in item.name or '\t' in item.name or '\r' in item.name:
				self.error(
					type="GENERAL:OBJECT NAME",
					message=( 'Object "{}" has whitespace in its name.' )
						.format( item.name )
				)
