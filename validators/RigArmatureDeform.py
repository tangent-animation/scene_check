import re
import os
import bpy

from validators.base_validator import BaseValidator

class RigArmatureDeform(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigArmatureDeform, self).__init__()

	def process_hook( self ):
		regex = re.compile( r"^(def)\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		## bone type names matching deform type
		for arm in self.get_objects( type='ARMATURE' ):
			for bone in arm.data.bones:
				match = regex.match( bone.name )
				if not match and bone.use_deform:
					self.error( ob=arm, subob=bone.name,
						type='non_deform',
						message="{}::'{}' non-deform bone marked for deform."
							.format(arm.name, bone.name) )
				elif match and not bone.use_deform:
					self.error( ob=arm, subob=bone.name,
						type='deform',
						message="{}::'{}' deform bone not marked for deform."
							.format(arm.name, bone.name) )

	def automatic_fix_hook(self):
		for error in self.errors:
			bone = error.ob.data.bones[error.subob]
			if error.type == 'non_deform':
				bone.use_deform = False
				print("+ Marked bone {}::{} as non-deform."
						.format(error.ob.name, error.subob) )
			elif error.type == 'deform':
				bone.use_deform = True
				print("+ Marked bone {}::{} as deform."
						.format(error.ob.name, error.subob) )
