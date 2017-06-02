import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

# whitespace_regex = re.compile('(\t|\n|\r| )')

class ObjectNames(BaseValidator):
	'''
	* Checks for whitespace in names
	* Checks Curves and Curve data for 'crv' prefix.
	* Checks Empty objects for 'nul' prefix
	* Checks Lattice objects for 'def' prefix
	'''

	def __init__(self):
		super(ObjectNames, self).__init__()

	def process_hook( self ):
		for item in self.get_objects():
			##!FIXME: Regex works online but not here; punting
			if ' ' in item.name or '\t' in item.name or '\r' in item.name:
				self.error(
					ob=item.name,
					select_func='object',
					type="GENERAL:OBJECT NAME",
					message=( 'Object "{}" has whitespace in its name.' )
						.format( item.name )
				)

			if item.type == 'CURVE':
				if not item.name.startswith( 'crv' ):
					self.error(
						ob=item.name,
						select_func='object',
						type="GENERAL:OBJECT NAME",
						message=( 'Object "{}" is missing the "crv" prefix.' )
							.format( item.name )
					)

				if not item.data.name.startswith( 'crv' ):
					self.error(
						ob=item.name,
						select_func='curve_data',
						type="GENERAL:DATA NAME",
						message=( 'Curve data for object "{}" is missing the "crv" prefix.' )
							.format( item.data.name )
					)

			elif item.type == 'EMPTY':
				if not item.name.startswith( 'nul' ):
					self.error(
						ob=item.name,
						select_func='object',
						type="GENERAL:OBJECT NAME",
						message=( 'Empty object "{}" is missing the "nul" prefix.' )
							.format( item.name )
					)

			elif item.type == 'LATTICE':
				if not item.name.startswith( 'def' ):
					self.error(
						ob=item.name,
						select_func='object',
						type="GENERAL:OBJECT NAME",
						message=( 'Lattice object "{}" is missing the "def" prefix.' )
							.format( item.name )
					)
