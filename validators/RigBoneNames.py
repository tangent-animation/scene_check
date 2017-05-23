import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigBoneNames(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigBoneNames, self).__init__()
		self.accepted_types = {
			'ctl', 'mst', 'def',
			'ikm', 'fkm', 'hlp',
			'prt', 'con', 'wgt',
			'psd', 'pos'
		}

	def process_hook( self ):
		regex = re.compile( r"^([A-Za-z]{3})\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		for arm in self.get_objects( type='ARMATURE' ):
			for bone in arm.data.bones:
				match = regex.match( bone.name )
				if not match:
					self.error( ob=arm, subob=bone.name,
						type='whitespace' if (bone.name.startswith(' ') or bone.name.endswith(' ')) else None,
						message="{}::'{}' bone does not follow naming convention."
							.format(arm.name, bone.name) )
				else:
					bone_type = match.group(1)
					if not bone_type in self.accepted_types:
						self.error( ob=arm, subob=bone.name,
							message="{}::'{}' bone does not start with an approved token."
								.format(arm.name, bone.name) )

	def automatic_fix_hook(self):
		for error in self.errors:
			#TODO(kiki): update drivers and skip controls?
			if error.type == 'whitespace':
				bone = error.ob.data.bones[error.subob]
				stripped = bone.name.strip()
				if stripped in error.ob.data.bones:
					print("-- Unable to auto-fix whitespace around bone %s: stripped bone already exists." % stripped )
				else:
					bone.name = stripped
					print( "+ Removed whitespace from bone %s." % stripped )