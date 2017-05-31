import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

class MeshModifiers(BaseValidator):
	'''
	Checks all modifiers on mesh objects:
	* Are they enabled in view and render?
	* Are target objects in the rig group?
	* Are subdiv render levels higher than display,
	  and are display levels 1?
	* Live modifiers checks for wireframe, mirror, and bevel
	'''

	def __init__(self):
		super(MeshModifiers, self).__init__()

	def process_hook( self ):
		target_deformer_types = { 'MESH_DEFORM','HOOK','CAST','LATTICE','CURVE' }
		target_subdiv_types   = { 'SUBSURFACE', 'MULTIRES' }

		for item in self.get_objects( type='MESH' ):
			for modifier in item.modifiers:
				if modifier.show_render == False and modifier.show_viewport == False:
					self.error(
						ob=item,
						subob=modifier.name,
						type='MODEL:MODIFIER',
						message=('Mesh "{}" Modifier "{}": disabled in VIEW and RENDER. Should it be removed?')
								.format( item.name, modifier.name )
					)
				elif modifier.show_render == False:
					self.error(
						ob=item,
						subob=modifier.name,
						type='MODEL:MODIFIER',
						message=('Mesh "{}" Modifier "{}": disabled in RENDER. Should it be removed?')
								.format( item.name, modifier.name )
					)

				elif modifier.show_viewport == False:
					self.error(
						ob=item,
						subob=modifier.name,
						type='MODEL:MODIFIER',
						message=('Mesh "{}" Modifier "{}": disabled in VIEW. Should it be removed?')
								.format( item.name, modifier.name )
					)

				if modifier.type in target_deformer_types:
					target = modifier.object
					if target:
						for thisgroup in item.users_group:
							if not( target.name in thisgroup.objects ):
								self.error(
									ob=target,
									subob=modifier.name,
									type='GENERAL:DEFORMERS',
									message=('Mesh "{}" Modifier "{}": Target {} not in rig group for linking.')
											.format( item.name, modifier.name, target.name )
								)
					else:
						self.error(
							ob=item,
							subob=modifier.name,
							type='GENERAL:DEFORMERS',
							message=('Mesh "{}" Modifier "{}": Target is empty.')
									.format( item.name, modifier.name )
						)

				elif modifier.type in target_subdiv_types:
					if modifier.levels > modifier.render_levels:
						self.error(
							ob=item,
							subob=modifier.name,
							type='MODEL:SUBSURF',
							message=('Mesh "{}" Modifier "{}": View subdiv levels higher in render than view.')
									.format( item.name, modifier.name )
						)

					if modifier.levels:
						self.error(
							ob=item,
							subob=modifier.name,
							type='MODEL:SUBSURF',
							message=('Mesh "{}" Modifier "{}": subdiv levels should be zero at file save (currently {}).')
									.format( item.name, modifier.name, modifier.levels )
						)

				elif modifier.type == 'WIREFRAME':
						self.error(
							ob=item,
							subob=modifier.name,
							type='MODEL:WIREFRAME',
							message=('Mesh "{}" Modifier "{}": Wireframe modifier found; should probably be removed.')
									.format( item.name, modifier.name )
						)

				elif modifier.type == 'MIRROR':
						self.error(
							ob=item,
							subob=modifier.name,
							type='MODEL:MIRROR',
							message=('Mesh "{}" Modifier "{}": Mirror modifier found; should probably be applied.')
									.format( item.name, modifier.name )
						)

				elif modifier.type == 'BEVEL':
					if len( [x for x in item.modifiers if x.type in target_subdiv_types] ):
						self.error(
							ob=item,
							subob=modifier.name,
							type='MODEL:BEVEL',
							message=( 'Mesh "{}" Modifier "{}": Bevel modifier found; Check if Bevel '
									'edge weights are set to work correctly with Subdivision Surface '
									'or Multires modifier.')
									.format( item.name, modifier.name )
						)
