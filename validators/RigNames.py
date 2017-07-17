import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigNames(BaseValidator):
	"""
	* Makes sure that Armature names conform
	to show standards.
	"""

	def __init__(self):
		super(RigNames, self).__init__()

	def process_hook( self ):
		base_name = os.path.basename( bpy.data.filepath ).replace('.blend','')
		char_name = base_name.rpartition('_')[2]
		base_rig_name = 'rig.{}.000'.format( base_name )
		if not base_rig_name in bpy.data.objects:
			self.error( message="Base rig object is missing ({})."
							.format(base_rig_name) )

		for ob in [ x for x in self.scene.objects if x.type == 'ARMATURE' ]:
			if ob.name == base_rig_name:
				continue

			match = self.rig_regex.match( ob.name )

			if not match:
				self.error(
					ob=ob.name,
					select_func='object',
					type='ARMATURE:NAME',
					message="Armature object {} does not follow naming convention.'"
							.format(ob.name)
				)

			elif match and '_low.' in ob.name and ob.proxy_group:
				self.error(
					ob=ob.name,
					select_func='object',
					type='ARMATURE:NAME',
					message='Proxy armature "{}" has "_low" in the name.'
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



