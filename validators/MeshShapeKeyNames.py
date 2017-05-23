import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

class MeshShapeKeyNames(BaseValidator):
	enabled = False

	def __init__(self):
		super(MeshShapeKeyNames, self).__init__()

	def process_hook( self ):
		regex = re.compile( r"^(shp)\.([A-Za-z\_]+)\.([CLR])\.([0-9]{3})$" )

		for mesh in [ x for x in self.get_objects( type='MESH' ) if x.data.shape_keys ]:
			for key in mesh.data.shape_keys.key_blocks:
				if key.name == 'Basis':
					continue
				match = regex.match( key.name )
				if not match:
					self.error( ob=mesh, subob=key.name,
						type='whitespace' if (key.name.startswith(' ') or key.name.endswith(' ')) else None,
						message="{}::'{}' shape key does not follow naming convention."
							.format(mesh.name, key.name) )
