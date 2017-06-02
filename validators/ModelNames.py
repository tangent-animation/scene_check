import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

whitespace_regex = re.compile('(\t|\n|\r| )')

class ModelNames(BaseValidator):
	'''
	Checks scene mesh objects against show naming conventions.
	'''

	def __init__(self):
		super(ModelNames, self).__init__()

	def process_hook( self ):
		for item in self.get_objects(type='MESH'):
			##!FIXME: should this check the presence of a skin?
			if self.asset_type == 'chr' and item.users > 1 and not item.name.startswith('shape'):
				self.error(
					ob=item.name,
					select_func='object',
					type='MODEL:USERS',
					message=("Multi-user object {} ({:d} users). On characters anything needing skin can't be instanced.")
							.format( item.name, item.users )
				)

			##!FIXME: purpose of this?
			if not self.asset_type == 'chr' and item.users > 1 and not item.name.startswith('shape'):
				self.warning(
					ob=item.name,
					select_func='object',
					type='MODEL:USERS',
					message=("Multi-user object {} ({:d} users). Can any of these instanced objects be combined?")
							.format( item.name, item.users )
				)

			if item.data.users > 1:
				self.warning(
					ob=item.name,
					select_func='object',
					type='MODEL:INSTANCE',
					message=( "{}: Can any of the {:d} users be combined?" )
							.format( item.name, item.data.users )
				)

			if not item.name.startswith( 'shape' ) and not item.name.startswith( 'geo' ):
				##!FIXME: Use a regex to really nail down the name format
				self.error(
					ob=item.name,
					select_func='object',
					type='MODEL:OBJECT NAME',
					message=( "{}: name does not begin with geo" )
							.format( item.name )
				)

				if not item.data.name.startswith( 'msh' ):
					self.error(
						ob=item.name,
						select_func='mesh_data',
						type='MODEL:DATA NAME',
						message=( "{}: data does not begin with 'msh' (currently {})" )
								.format( item.name, item.data.name )
					)

