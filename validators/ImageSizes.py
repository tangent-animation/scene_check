import os
import re
from math import floor
import bpy

from scene_check.validators.base_validator import BaseValidator

class ImageSizes(BaseValidator):
	'''
	* Make sure textures don't exceed 4096x4096 pixels
	* Make sure that the image isn't more than 8bpp
	* Warns if the texture is not square
	* Warns if texture size is not a power of two.
	'''

	def __init__(self):
		super(ImageSizes, self).__init__()

	def file_size( self, file_name ):
		return os.stat( bpy.path.abspath(file_name) ).st_size

	def process_hook( self ):
		regex = re.compile( r"(img)\.([A-Za-z\_]+)\.(v[0-9]{4})\.(png|exr)" )

		unique_paths = {}

		MAX_SIZE      = 4096
		MAX_FILE_SIZE = (2**20) * 10	## ten megabytes
		POWER2_SIZES  = [ 2**x for x in range(14) ]

		for image in bpy.data.images:
			filepath = os.path.abspath( bpy.path.abspath(image.filepath) )

			if image.size[0] > MAX_SIZE or image.size[1] > MAX_SIZE:
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - OVERSIZED',
					message=( 'Image {name} is too large ({sizeA}x{sizeB}). '
							  'Maximum size is {max_size}x{max_size} pixels.' )
					.format(
						name=filepath,
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
						name=filepath,
						sizeA=image.size[0],
						sizeB=image.size[1],
					)
				)

			if not image.size[0] in POWER2_SIZES or not image.size[1] in POWER2_SIZES:
				self.warning( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - NON-POWER OF TWO',
					message=( 'Image {name} size not a power of two (currently {sizeA}x{sizeB} pixels).' )
					.format(
						name=filepath,
						sizeA=image.size[0],
						sizeB=image.size[1],
					)
				)

			if image.depth > 32 and not image.name.endswith( ('.hdr','.exr','.png') ):
				self.error( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - OVER DEPTH',
					message=( 'Image {name} is is not an 8bpp image (depth {depth}).')
					.format(
						name=filepath,
						depth=image.depth
					)
				)

			file_size = self.file_size( filepath )

			if file_size > MAX_FILE_SIZE:
				self.warning( ob=image.name,
					select_func='image',
					type='IMAGE:SIZE - OVER FILE SIZE',
					message=( 'Image {name} is larger than ten megabytes ({size}kb).' )
					.format(
						name=filepath,
						size=int(floor(file_size / 1024))
					)
				)

