import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class Camera(BaseValidator):
	'''
	* Makes sure cameras are properly named.
	* Makes sure camera is parented under a rig
	* Makes sure camera rig is properly named.
	* Makes sure camera rig is locked.
	* Makes sure the camera rig has a DOF object.
	'''

	camera_name_regex = re.compile( r"cam\.([0-9]{3})_([0-9]{4})_(t01)" )
	rig_name_regex    = re.compile( r"rig\.cam_([0-9]{3})_([0-9]{4})\.t01\.([0-9]{3})" )

	def __init__(self):
		super(Camera, self).__init__()

	def process_hook( self ):
		scene = bpy.context.scene

		cameras = []

		for camera in [ x for x in scene.objects if x.type == 'CAMERA' ]:
			name = camera.name
			match = self.camera_name_regex.match( name )
			if not match:
				self.error(
					ob=name,
					select_func='object',
					type='CAMERA:NAME',
					message=( 'Camera "{}" name does not match show standard.'
							.format(name) )
				)
			else:
				parent = camera.parent
				if not parent or not parent.type == 'ARMATURE':
					self.error(
						ob=name,
						select_func='object',
						type='CAMERA:PARENT',
						message=( 'Camera "{}" is not under a proper rig parent.'
								.format(name) )
					)
				else:
					cameras.append( name )
		
		for cam in cameras:
			camera   = bpy.data.objects[ cam ]
			armature = camera.parent

			match = self.rig_name_regex.match( armature.name )
			if not match:
				self.error(
					ob=armature.name,
					select_func='object',
					type='CAMERA:RIG NAME',
					message=( 'Camera "{}" is parented to an armature that is not properly named ("{}").'
							.format(cam, armature.name) )
				)
			
			if not armature.name == armature.data.name:
				self.error(
					ob=armature.name,
					select_func='object',
					type='CAMERA:DATA NAME',
					message=( 'Camera Armature "{}" has data whose name does not match ("{}").'
							.format( armature.name, armature.data.name ) )
				)
			
				fix_code = (
					'armature = bpy.data.objects["{}"]\n'
					'armature.data.name = armature.name'
				).format( armature.name )
			
				self.auto_fix_last_error(
					fix_code,
					message='Rename data on Camera Armature "{}".'.format( armature.name )
				)

			total_unlocked_bones = 0
			for bone in [ x for x in armature.pose.bones if x.name.startswith('ctl.') ]:
				locked = sum(
					list( bone.lock_location ) + 
					list( bone.lock_rotation ) + 
					list( bone.lock_scale )
				)
				if not locked == 9:
					self.error(
						ob=armature.name,
						subob=bone.name,
						select_func='armature_bone',
						type='CAMERA:UNLOCKED BONE',
						message=( 'Camera Armature "{}" has unlocked bone "{}".'
								.format( armature.name, bone.name ) )
					)
				
					fix_code = (
						'armature = bpy.data.objects["{}"]\n'
						'bone = armature.pose.bones["{}"]\n'
						'bone.lock_location = [True] * 3\n'
						'bone.lock_rotation = [True] * 3\n'
						'bone.lock_scale = [True] * 3\n'
					).format( armature.name, bone.name )
				
					self.auto_fix_last_error(
						fix_code,
						message=( 'Lock Pose Bone "{}" on Camera Armature "{}".'
								.format(bone.name, armature.name) )
					)
			





