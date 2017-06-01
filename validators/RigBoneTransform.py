import bpy

from scene_check.validators.base_validator import BaseValidator

class RigBoneTransform(BaseValidator):
	automatic_fix = True

	def __init__(self):
		super(RigBoneTransform, self).__init__()
		self.rejected_orders = {
			'QUATERNION',
			'AXIS_ANGLE'
			# 'XYZ', 'XZY', 'YXZ',
			# 'YZX', 'ZXY', 'ZYX'
		}

		self.specials = [
			'ctl.god.C.001',
			'ctl.god_secondary.C.001',
			'ctl.ground.C.001',
			'ctl.ground_secondary.C.001',
			'ctl.root.C.001',
			'ctl.root_secondary.C.001'
		]

	def process_hook( self ):
		for arm in self.get_objects( type='ARMATURE' ):
			for special in self.specials:
				if special in arm.pose.bones:
					bone = arm.pose.bones[special]


			for bone in arm.pose.bones:
				if bone.name in self.specials:
					continue

				if bone.rotation_mode in self.rejected_orders:
					self.error( ob=arm, subob=bone.name,
						message='{}::{}: Bone has invalid rotation order.'
							.format(arm.name, bone.name) )

				if 'god' in bone.name and not bone.parent:
					if sum(bone.head):
						self.error( ob=arm, subob=bone.name,
							message=('{}::{}: TOP node in armature hierarchy '
									'should be centered at origin (0,0,0).')
								.format(arm.name, bone.name) )


	def automatic_fix_hook( self ):
		for error in self.errors:
			if error.type == 'special':
				bone = error.ob.pose.bones[error.subob]
				bone.rotation_mode = 'XYZ'
				print( "+ Fixed rotation order for {}::{}."
						.format(error.ob.name, error.subob) )
