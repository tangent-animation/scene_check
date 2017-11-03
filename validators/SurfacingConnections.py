import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class SurfacingConnections( BaseValidator ):
	"""
	* Checks that Shader-type outputs are 
	connected to Shader-type inputs.
	"""

	def __init__(self):
		super(SurfacingConnections, self).__init__()

	def process_hook( self ):
		all_meshes = filter( lambda x: len(x.data.materials) > 0, self.get_render_meshes() )

		for item in all_meshes:
			materials = [ x for x in item.data.materials if x ]

			link_set = [ (item, mat) for mat in materials ]

			for ob, mat in link_set:
				if not mat.node_tree:
					self.error(
						ob=item.name,
						select_func='materials',
						subob=mat.name,
						type='SURFACE:MATERIAL - NODE TREE',
						message=('Material "{}" on object "{}" has no connected node tree.')
								.format( item.name, mat.name )
					)

					continue

				for link in mat.node_tree.links:
					if link.from_socket.type == 'SHADER' and not link.to_socket.type == 'SHADER':
						self.error(
							ob=item.name,
							select_func='material_nodes',
							subob=mat.name,
							data=link.from_node.name,
							type='SURFACE:MATERIAL - SHADER LINKS',
							message=('Shader output "{}.{}" connected to non-shader input "{}.{}" (type {}).')
									.format( link.from_node.name, link.from_socket.name,
											 link.to_node.name, link.to_socket.name,
											 link.to_socket.type
										)
						)