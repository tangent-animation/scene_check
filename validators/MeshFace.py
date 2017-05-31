import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class MeshFace(BaseValidator):
	'''
	Reports counts on ngons and triangles,
	zero area polygons, and loose edges
	for every mesh.	
	'''

	def __init__(self):
		super(MeshFace, self).__init__()

	def process_hook( self ):
		for item in self.get_objects( type='MESH' ):
			triangles   = 0
			ngons       = 0
			zero_area   = 0
			loose_edges = 0

			for face in item.data.polygons:
				vert_count = len( face.vertices )
				if vert_count == 3:
					triangles += 1
				elif vert_count > 4:
					ngons += 1

				# if face.area < 0.0001:
				if face.area == 0.0:
					zero_area += 1

			for edge in item.data.edges:
				if edge.is_loose:
					loose_edges += 1

			if triangles:
				self.error(
					type='MODEL:TRIS',
					message=('Mesh "{}" contains {} triangle{}. Please use MeshLint.')
							.format( item.name, triangles, '' if triangles == 1 else 's' )
				)

			if ngons:
				self.error(
					type='MODEL:NGONS',
					message=('Mesh "{}" contains {} ngon{}. Please use MeshLint.')
							.format( item.name, ngons, '' if ngons == 1 else 's' )
				)

			if zero_area:
				self.error(
					type='MODEL:ZERO AREA FACES',
					message=('Mesh "{}" contains {} zero area face{}. Please use MeshLint.')
							.format( item.name, zero_area, '' if zero_area == 1 else 's' )
				)

			if loose_edges and not item.name.startswith('shape'):
				self.error(
					type='MODEL:LOOSE EDGES',
					message=('Mesh "{}" contains {} loose edge{}.')
							.format( item.name, loose_edges, '' if loose_edges == 1 else 's' )
				)

