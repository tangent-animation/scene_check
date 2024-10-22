import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class ModelVertexGroups(BaseValidator):
	'''
	Ensures vertex group names on mesh objects
	conform to the show standard.
	'''

	def __init__(self):
		super(ModelVertexGroups, self).__init__()

	def process_hook( self ):
		valid_names = { 'vtx','def','shp','deform_mesh','hair','surfacing' }

		for item in self.get_objects(type='MESH'):
			for group in item.vertex_groups:
				valid = False
				for name in valid_names:
					if group.name.startswith( name ):
						valid = True

				if not valid:
					self.error(
						ob=item.name,
						subob=group.name,
						select_func='mesh_vertex_group',
						type='MODEL:VERTEX GROUP NAME',
						message=('Mesh "{}" Vertex Group "{}": Name does not conform to show standards.')
								.format( item.name, group.name )
					)
