import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class SurfacingMaterials(BaseValidator):
	'''
	Checks to make sure that each mesh
	has at least one Material.
	'''

	def __init__(self):
		super(SurfacingMaterials, self).__init__()

	def process_hook( self ):
		mesh_materials = {}

		for item in self.get_objects(type='MESH'):
			if not len(item.data.materials):
				self.error(
					ob=item,
					type='SURFACE:MATERIAL - NONE',
					message=('Mesh "{}" has no materials.')
							.format( item.name )
				)

			## bugfix: some materials return as None?
			for material in [ x for x in item.data.materials if x ]:
				if not material.name in mesh_materials:
					mesh_materials[material.name] = material

					if not material.name.startswith('mtl.'):
						self.error(
							ob=item,
							subob=material.name,
							type='SURFACE:MATERIAL - NAME',
							message=('Material "{}" on Mesh "{}" "mtl." prefix in its name.')
									.format( material.name, item.name )
						)

				nodes = material.node_tree.nodes if material.use_nodes else []
				node_count = len(nodes)
				links = material.node_tree.links if material.use_nodes else []

				##!FIXME: This seems strange and arbitrary
				if node_count > 15:
					self.warning(
						ob=item,
						subob=material.name,
						type='SURFACE:MATERIAL - COMPLEX',
						message=('Material "{}" on Mesh "{}" has {} nodes-- possibly needs cleaning.')
								.format( material.name, item.name, node_count )
					)

				cloth      = 0
				dielectric = 0
				glass      = 0
				metal      = 0
				skin       = 0

				for node in nodes:
					if node.type == 'TEX_IMAGE':
						if not node.inputs[0].is_linked:
							self.warning(
								ob=item,
								subob=material.name,
								type='SURFACE:NODE - CONNECTION',
								message=('Material "{}" on Mesh "{}" appears to have a disconnected UV input.')
										.format( material.name, item.name )
							)
						else:
							for link in node.inputs[0].links:
								subob = '{}.node_tree.nodes[{}]'.format(material.name, node.name)
								
								## bugfix: uvmap_node.uv_map returns an empty string if nothing is picked
								##         also, you can assume link.from_node is filled or it won't
								##         be in the above tuple
								if link.from_node.type == 'UVMAP' and len(link.from_node.uv_map):
									self.error(
										ob=item,
										subob=subob,
										type='SURFACE:NODE - NO UVS',
										message=('UV Map Node "{}" on Mesh "{}" has no UVs assigned.')
												.format( subob, item.name )
									)

								elif link.from_node.type == 'TEX_COORD':
									if not link.from_node.object:
										self.error(
											ob=item,
											subob=subob,
											type='SURFACE:NODE - NO UVS',
											message=('Texture Coordinates Node "{}" on '
													 'Mesh "{}" has no source object.')
													.format( subob, item.name )
										)
									elif not len(link.from_node.object.data.uv_layers):
										self.error(
											ob=item,
											subob=subob,
											type='SURFACE:NODE - NO UVS',
											message=('Texture Coordinates Node "{}" on '
													 'Mesh "{}" has a source object '
													 'with no UVs ("{}")')
													.format( subob, item.name, link.from_node.object.name )
										)

					elif node.type == 'GROUP':
						if ( ('shd.pbr_cloth' in node.node_tree.name 
								or 'pbr.cloth' in node.node_tree.name) and
								len( node.node_tree.nodes ) == 13 ):
							cloth += 1
						if ( ('shd.pbr_dielectric' in node.node_tree.name 
								or 'pbr.dielectric' in node.node_tree.name) and
								len( node.node_tree.nodes ) == 5 ):
							dielectric += 1
						if ( ('shd.pbr_glass' in node.node_tree.name 
								or 'pbr.glass' in node.node_tree.name) and
								len( node.node_tree.nodes ) == 15 ):
							glass += 1
						if ( ('shd.pbr_metal' in node.node_tree.name 
								or 'pbr.metal' in node.node_tree.name) and
								len( node.node_tree.nodes ) == 7 ):
							metal += 1
						if ( ('shd.pbr_sss_skin' in node.node_tree.name 
								or 'pbr.sss_skin' in node.node_tree.name) and
								len( node.node_tree.nodes ) == 39 ):
							skin += 1

				if cloth > 1:
					self.error(
						ob=item,
						subob=material.name,
						type='SURFACE:NODE - PBR',
						message=('Material "{}" on Mesh "{}" has too many pbr_cloth groups (found {}).')
								.format( material.name, item.name, cloth )
					)

				if dielectric > 1:
					self.error(
						ob=item,
						subob=material.name,
						type='SURFACE:NODE - PBR',
						message=('Material "{}" on Mesh "{}" has too many pbr_dielectric groups (found {}).')
								.format( material.name, item.name, dielectric )
					)

				if glass > 1:
					self.error(
						ob=item,
						subob=material.name,
						type='SURFACE:NODE - PBR',
						message=('Material "{}" on Mesh "{}" has too many pbr_glass groups (found {}).')
								.format( material.name, item.name, glass )
					)

				if metal > 1:
					self.error(
						ob=item,
						subob=material.name,
						type='SURFACE:NODE - PBR',
						message=('Material "{}" on Mesh "{}" has too many pbr_metal groups (found {}).')
								.format( material.name, item.name, metal )
					)

				if skin > 1:
					self.error(
						ob=item,
						subob=material.name,
						type='SURFACE:NODE - PBR',
						message=('Material "{}" on Mesh "{}" has too many pbr_skin groups (found {}).')
								.format( material.name, item.name, skin )
					)

