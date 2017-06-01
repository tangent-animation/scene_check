import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigCharacterMeshLocks(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigCharacterMeshLocks, self).__init__()

	def collect_children_recursive( self, ob, type=None, result=None ):
		if result is None:
			result = []
		if not ob in result:
			result.append(ob)
		for child in ob.children:
			result = self.collect_children_recursive( child, result=result )
		return(result)

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		for arm in armatures:
			if arm.name.startswith('rig.'):
				for child in self.collect_children_recursive(arm, type='MESH'):
					if not child.hide_select:
						self.error(
							ob=child,
							type='rig_mesh_hide',
							message='Child object {} under rig {} is not properly locked.'
							.format( child.name, arm.name )
						)

	def automatic_fix_hook( self ):
		for error in self.errors:
			if error.type == 'rig_mesh_hide':
				error.ob.hide_select = True
				print( "+ Automatically fixed mesh locking for rig mesh {}.".format(error.ob.name) )
