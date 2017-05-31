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
		for item in self.get_objects( type='MESH' ):
			edges = 0
			verts = 0

			bm = bmesh.new()
			bm.from_mesh( item.data )

			for edge in bm.edges:
				if not( edge.is_manifold ):
					edges += 1
	
			for vert in bm.verts:
				if not( vert.is_manifold ):
					verts += 1
 
			if verts:
				self.error(
					type='MODEL:NONMANIFOLD VERTS',
					message=('Mesh "{}" contains {} non-manifold vert{}. Please use MeshLint.')
							.format( item.name, verts, '' if verts == 1 else 's' )
				)

			if edges:
				self.error(
					type='MODEL:NONMANIFOLD EDGES',
					message=('Mesh "{}" contains {} non-manifold edge{}. Please use MeshLint.')
							.format( item.name, edges, '' if edges == 1 else 's' )
				)
