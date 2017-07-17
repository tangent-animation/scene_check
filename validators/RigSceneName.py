import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class RigSceneName(BaseValidator):
	"""
	* Makes sure that the file's scene name matches
	the name of the rig.
	"""

	def __init__(self):
		super(RigSceneName, self).__init__()

	def process_hook( self ):
		base_name = os.path.basename( bpy.data.filepath )
		char_name = base_name.replace('.blend','').rpartition('_')[2]

		if not self.scene.name == '{}_rig'.format(char_name):
			self.error( message="Scene name ({}) / File name ({}) mismatch."
							.format(base_name, self.scene.name) )
