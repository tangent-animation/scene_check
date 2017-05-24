import bpy

from scene_check.validators.base_validator import BaseValidator

class ImagePaths(BaseValidator):
	def __init__(self):
		super(ImagePaths, self).__init__()

	def process_hook( self ):
		for image in bpy.data.images:
			path = bpy.path.abspath( image.filepath ).lower()
			if not path.startswith('t:'):
				self.error( ob=image,
					type='not_on_t',
					message="Image {} is not on the T: drive (current path: {})."
					.format( image.name, path )
				)

			elif 'r_and_d' in path:
				self.error( ob=image,
					type='r_and_d',
					message="Image {} is in the R&D folder-- please move (current path: {})."
					.format( image.name, path )
				)

			if 'desktop' in path:
				self.error( ob=image,
					type='desktop',
					message="Image {} is in a Desktop folder-- please move (current path: {})."
					.format( image.name, path )
				)

