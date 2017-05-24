import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigControllerConstraintNames(BaseValidator):
	def __init__(self):
		super(RigControllerConstraintNames, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		for arm in armatures:
			for bone in [ x for x in arm.pose.bones if x.name.startswith('ctl.') ]:
				for cnst in bone.constraints:
					if not cnst.name.startswith('DO_NOT_TOUCH'):
						self.error( ob=arm, subob=bone.name,
							message='Constraint "{}" on bone {}::{} should start with "DO_NOT_TOUCH"'
								.format(cnst.name, arm.name, bone.name) )
