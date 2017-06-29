import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class SceneConstraints(BaseValidator):
	'''
	* Checks for presence of scene-level constraints empty
	* Makes sure all constraint armatures are living under a scene-level empty
	'''

	automatic_fix = True

	def __init__(self):
		super(SceneConstraints, self).__init__()
		self.temp_objects = []

	def process_hook( self ):
		self.constraint_objects = [
				x for x in bpy.context.scene.objects if 
				not x.library            and 
				x.type in { 'ARMATURE' } and
				x.name.startswith( 'con.' )
		]

		self.constraints_group_name = 'grp.constraints_' + self.scene.name

		if not self.constraints_group_name in self.scene.objects:
			self.error(
				ob=self.scene.name,
				type="SCENE:CONSTRAINTS GROUP",
				message=( 'Constraints group object "{}" is missing.'
					.format( self.constraints_group_name ) )
			)

		for item in self.constraint_objects:
			##!TODO: Separate error for linked constraint armatures?

			parent = item.parent
			if not parent or not parent.name == self.constraints_group_name:
				self.error(
					ob=item.name,
					select_func='object',
					type="SCENE:CONSTRAINTS",
					message=( 'Constraint object "{}" is not under parent empty "{}".'
						.format( item.name, self.constraints_group_name ) )
				)

	def automatic_fix_hook( self ):
		## loop twice to ensure the scene constraint group
		for error in self.errors:
			if error.type == 'SCENE:CONSTRAINTS GROUP':
				group = bpy.data.objects.new( self.constraints_group_name, None )
				self.scene.objects.link( group )

				group.rotation_mode = 'XYZ'
				group.lock_location = ( True, True, True )
				group.lock_rotation = ( True, True, True )
				group.lock_scale    = ( True, True, True )
				group.hide_select   = True
				group.hide_render   = True

				print( '+ Added constraint group "{}".'.format(group.name) )

		group = bpy.data.objects[ self.constraints_group_name ]

		for error in self.errors:
			if error.type == 'SCENE:CONSTRAINTS':
				constraint = bpy.data.objects[ error.ob ]
				constraint.parent = group

				print( '+ Reparented constraint "{}" to "{}".'
						.format( self.constraints_group_name, error.ob) )



