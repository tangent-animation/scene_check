import os
import re
import bpy

from scene_check.validators.base_validator import BaseValidator

class ImagePaths(BaseValidator):
	'''
	Validates file paths in images:
	* Make sure textures are not packed
	* Make sure texture file path exists on disk
	* Make sure path is on the T drive, and not in a wonky folder
	* Make sure data block is named correctly.
	* Make sure format is PNG
	* Check all images against each other for multiple data blocks pointing
	  to the same file on disk.
	'''

	def __init__(self):
		super(ImagePaths, self).__init__()

	def process_hook( self ):
		regex = re.compile( r"(img)\.([A-Za-z\_]+)\.(v[0-9]{4})\.(png)" )

		unique_paths = {}

		for image in bpy.data.images:
			if image.is_dirty:
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:TEXTURE - PACKED',
					message=( 'Image {} is packed with unsaved changes. '
							  'Please do not pack images into files.' )
					.format( image.name )
				)
				continue

			path = bpy.path.abspath( image.filepath ).lower()
			name = os.path.basename( path )

			if len(path.strip()) == 0 or image.filepath == "T:\\T:":
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:PACKED',
					message="Image {} packed. Please do not pack images."
					.format( image.name )
				)
				continue

			if not path in unique_paths:
				unique_paths[path] = [ image.name ]
			else:
				unique_paths[path].append( image.name )

			if not os.path.exists( path ):
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:TEXTURE - MISSING',
					message=( 'Image {}: file name {} does not exist on disk.' )
					.format( image.name, path )
				)

			elif not path.startswith('t:'):
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:FILE NOT ON T DRIVE',
					message="Image {} is not on the T: drive (current path: {})."
					.format( image.name, path )
				)

			elif 'r_and_d' in path:
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:FILE IN R&D',
					message="Image {} is in the R&D folder-- please move (current path: {})."
					.format( image.name, path )
				)

			if 'desktop' in path:
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:FILE ON DESKTOP',
					message="Image {} is in a Desktop folder-- please move (current path: {})."
					.format( image.name, path )
				)

			if not name.startswith('img.'):
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:TEXTURE - PREFIX',
					message=( 'Image {}: file name {} does not start with prefix "img.".' )
					.format( image.name, path )
				)

			if not name.endswith('.png'):
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:TEXTURE - FORMAT',
					message=( 'Image {}: file {} is not a PNG file.' )
					.format( image.name, path )
				)

			match = regex.match( name )
			if not match:
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:TEXTURE - NAME',
					message=( 'Image {}: file name {} does not conform to show standard.' )
					.format( image.name, path )
				)

		for path, references in unique_paths.items():
			if len( references ) > 1:
				self.error(
					type='IMAGE:DUPLICATE',
					message=( 'File {} is referenced by more than one image '
							  'data block.' )
							.format( path ),
					data = [path] + references
				)				

