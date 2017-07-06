import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


class SceneLayers(BaseValidator):
	'''
	* Checks for namedLayers and sets the correct names.
	* Assigns layers automatically in the auto fix
	'''

	automatic_fix = True

	layer_names = {
		0:  'camera',
		1:  'character',
		2:  'prop',
		3:  'sets',
		4:  'light',
		5:  'fx',
		10: 'constraint',
		18: 'temp',
		19: 'curve'
	}


	def __init__(self):
		super(SceneLayers, self).__init__()

	def process_hook( self ):
		armatures = self.get_objects( type='ARMATURE' )
		empties   = self.get_objects( type='EMPTY' )

		characters  = [ x for x in (armatures+empties) if x.name.startswith('grp.') ]
		constraints = [ x for x in armatures if x.name.startswith('con.') ]

		for character in characters:
			print("+ Processing {}...".format( character.name ))
			layers = self.layers( 1 )
			test = sum([ x == y for x,y in zip(layers, character.layers) ])
			if not test == 20:
				self.error(
					ob=character.name,
					select_func='object',
					data=1,
					type='SCENE:CHARACTER LAYERS',
					message="Character Armature object {} not on layer 1.'"
							.format(character.name)
				)

				fix_code = (
					'bpy.data.objects["{}"].layers = {}'
				).format( character.name, self.layers(1) )

				self.auto_fix_last_error(
					fix_code,
					message='Set correct layers for character "{}".'.format( character.name )
				)
			else:
				print("Character {} passes.".format( character.name ))

		for constraint in constraints:
			layers = self.layers( 10 )
			test = sum([ x == y for x,y in zip(layers, constraint.layers) ])
			if not test == 20:
				self.error(
					ob=constraint.name,
					select_func='object',
					data=10,
					type='SCENE:CONSTRAINT LAYERS',
					message="Constraint Armature object {} not on layer 10.'"
							.format(constraint.name)
				)

				fix_code = (
					'bpy.data.objects["{}"].layers = {}'
				).format( constraint.name, self.layers(10) )

				self.auto_fix_last_error(
					fix_code,
					message='Set correct layers for constraint "{}".'.format( constraint.name )
				)

		scene = self.scene

		if hasattr( scene, 'namedlayers' ):
			count = sum([ scene.namedlayers.layers[index] == x for index, x in self.layer_names.items() ])
			if not count == len( self.layer_names ):
				self.error(
					ob=scene.name,
					type='SCENE:LAYER NAMES',
					message='Layer names in scene "{}" do not match show standard.'
							.format( scene.name )
				)

				fix_code = (
					'layers = bpy.data.scenes["{}"].namedlayers.layers\n'
				).format( scene.name )
				for index, name in self.layer_names.items():
					fix_code += 'layers[{}].name = "{}"\n'.format( index, name )

				self.auto_fix_last_error(
					fix_code,
					message='Set layer names for scene "{}".'.format( scene.name )
				)

	def layers(self, *args):
		for index in args:
			assert( isinstance(index, int) )
			if index < 0 or index > 19:
				raise ValueError( 'Index must be between 0 and 31, inclusive.' )
		result = [False] * 20
		for index in args:
			result[index] = True
		return( result )

	# def automatic_fix_hook( self ):
	# 	for index, name in self.layer_names.items():
	# 		try:
	# 			scene.namedlayers.layers[index].name = name
	# 		except:
	# 			continue

	# 	for error in self.errors:
	# 		ob = self.scene.objects[ error.ob ]
	# 		ob.layers = self.layers( error.data )
	# 		print( 'Set proper layer for "{}" -- now {}.'.format(ob.name, error.data) )

