import re
import os
import bpy, bmesh

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class MeshNonManifold(BaseValidator):
	'''
	Reports counts on non-manifold
	verts and edges for every mesh.	
	'''

	def __init__(self):
		super(MeshNonManifold, self).__init__()
		print("--== MeshNonManifold is in Beta! ==--")

	def process_hook( self ):
		context = bpy.context
		scene   = context.scene

		for item in [ x for x in self.get_objects( type='MESH' ) 
					 if not x.name.startswith('shape')
					 and not x.name.count('_proxy')
					 and not x.name.count('mesh_deform')]:
			verts = 0
			verts_data = []
			# edges = 0
			# edges_data = []

			item.hide = False
			scene.objects.active = item
			bpy.ops.object.mode_set( mode='OBJECT' )

			bm = bmesh.new()
			bm.from_mesh( item.data )

			for vert in item.data.vertices:
				vert.select = False

			# for edge in item.data.edges:
			# 	edge.select = False

			# for edge in bm.edges:
			# 	edge.select = False
			# 	if not edge.is_manifold:
			# 		## bugfix: if it's linked to one face only it's a border
			# 		## edge and not non-manifold
			# 		if len(edge.link_faces) > 1:
			# 			edge.select = True
			# 			edges += 1
			# 			edges_data.append( edge.index )
			
			for vert in bm.verts:
				vert.select = False
				if not vert.is_manifold:
					vert.select = True
					verts += 1
					verts_data.append( vert.index )

			# if verts or edges:
			# 	bm.to_mesh( item.data )
 
			if verts:
				self.error(
					ob=item.name,
					select_func='non_manifold',
					data=verts_data,
					type='MODEL:NONMANIFOLD VERTS',
					message=('Mesh "{}" contains {} non-manifold vert{}. Please use MeshLint.')
							.format( item.name, verts, '' if verts == 1 else 's' )
				)

			# if edges:
			# 	self.error(
			# 		ob=item,
			# 		data=edges_data,
			# 		type='MODEL:NONMANIFOLD EDGES',
			# 		message=('Mesh "{}" contains {} non-manifold edge{}. Please use MeshLint.')
			# 				.format( item.name, edges, '' if edges == 1 else 's' )
			# 	)
