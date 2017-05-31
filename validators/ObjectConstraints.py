import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences

# whitespace_regex = re.compile('(\t|\n|\r| )')

class ObjectConstraints(BaseValidator):
	'''
	**
	'''

	def __init__(self):
		super(ObjectConstraints, self).__init__()

	def process_hook( self ):
		constraint_types = {
			'COPY_LOCATION','COPY_ROTATION','COPY_SCALE',
			'COPY_TRANSFORMS','LIMIT_DISTANCE','TRANSFORM',
			'CLAMP_TO','DAMPED_TRACK','LOCKED_TRACK','STRETCH_TO',
			'TRACK_TO','ACTION','CHILD_OF','FLOOR','FOLLOW_PATH',
			'PIVOT','RIGID_BODY_JOINT','SHRINKWRAP'
		}

		for item in self.get_objects():
			for constraint in item.constraints:
				if not constraint.type in constraint_types:
					continue

				target = constraint.target

				if target:
					for thisgroup in item.users_group:
						if not( target.name in thisgroup.objects ):
							self.error(
								ob=target,
								subob=constraint.name,
								type='RIGGING:GROUP',
								message=('Mesh "{}" Constraint "{}": Target {} not in rig group for linking.')
										.format( item.name, constraint.name, target.name )
							)
				else:
					self.error(
						ob=item,
						subob=constraint.name,
						type='RIGGING:CONSTRAINT TARGET',
						message=('Mesh "{}" Constraint "{}": No target object.')
								.format( item.name, constraint.name )
					)

