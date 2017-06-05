import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigNames(BaseValidator):
	def __init__(self):
		super(RigNames, self).__init__()

	def process_hook( self ):
		base_name = os.path.basename( bpy.data.filepath ).replace('.blend','')
		char_name = base_name.rpartition('_')[2]

		base_rig_name = 'rig.{}.000'.format( base_name )
		if not base_rig_name in bpy.data.objects:
			self.error( message="Base rig object is missing ({})."
							.format(base_rig_name) )

		rig_regex = re.compile( r"(rig)\.([A-Za-z0-9_]+)\.([0-9]{3})" )
		ncr_regex = re.compile( r"(ncr)\.([A-Za-z0-9_]+)\.([0-9]{3})" )

		for ob in [ x for x in self.scene.objects if x.type == 'ARMATURE' ]:
			if ob.name == base_rig_name:
				continue

			match = rig_regex.match( ob.name )
			ncr_match = ncr_regex.match( ob.name )

			if not match and not ncr_match:
				self.error(
					ob=ob.name,
					select_func='object',
					type='ARMATURE:NAME',
					message="Armature object {} does not follow naming convention.'"
							.format(ob.name)
				)

			if not ob.data.name == ob.name:
				self.error(
					ob=ob.name,
					type='ARMATURE:DATA NAME',
					select_func='object',
					message="Armature object {}'s data name does not match {}.'"
							.format(ob.name, ob.data.name)
				)



