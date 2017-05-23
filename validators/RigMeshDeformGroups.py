import re
import os
import bpy

from validators.base_validator import BaseValidator

class RigMeshDeformGroups(BaseValidator):
	def __init__(self):
		super(RigMeshDeformGroups, self).__init__()

	def process_hook( self ):
		regex = re.compile( r"^([a-z]{3})\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		## deform bones only in mesh vertex groups
		for mesh in self.get_objects( type='MESH' ):
			if mesh.name.startswith('shape.'):
				continue

			## pull out all groups that look like they could be bones
			groups    = [ x.name for x in mesh.vertex_groups ]
			modifiers = [ x for x in mesh.modifiers if x.type == 'ARMATURE' ]
			armatures = [ x.object for x in modifiers if x.object ]
			for arm in armatures:
				for group in groups:
					if group in arm.data.bones:
						bone = arm.data.bones[group]
						if not ( group.startswith('def.') and bone.use_deform ):
							self.error( ob=mesh,
										message="Mesh {} has vertex group {} for non-deforming bone."
												.format(mesh.name, group) )
