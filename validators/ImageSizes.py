import os
import re
import bpy

from scene_check.validators.base_validator import BaseValidator

class ImageSizes(BaseValidator):
	'''
	* Make sure textures don't exceed 4096x4096 pixels
	* Make sure that the image isn't more than 8bpp
	* Warns if the texture is not square
	'''

	def __init__(self):
		super(ImageSizes, self).__init__()

	def process_hook( self ):
		regex = re.compile( r"(img)\.([A-Za-z\_]+)\.(v[0-9]{4})\.(png)" )

		unique_paths = {}

		MAX_SIZE = 4096

		for image in bpy.data.images:
			if image.size[0] > MAX_SIZE or image.size[1] > MAX_SIZE:
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - OVERSIZED',
					message=( 'Image {name} is too large ({sizeA}x{sizeB}). '
							  'Maximum size is {max_size}x{max_size} pixels.' )
					.format(
						name=image.name,
						sizeA=image.size[0],
						sizeB=image.size[1],
						max_size=MAX_SIZE
					)
				)

			elif not image.size[0] == image.size[1]:
				self.warning( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - NON-SQUARE',
					message=( 'Image {name} not square (currently {sizeA}x{sizeB} pixels).' )
					.format(
						name=image.name,
						sizeA=image.size[0],
						sizeB=image.size[1],
					)
				)

			if image.depth > 32 and not image.name.endswith(('.hdr','.exr')):
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - OVER DEPTH',
					message=( 'Image {name} is is not an 8bpp image (depth {depth}).')
					.format(
						name=image.name,
						depth=image.depth
					)
				)



