import re
import os
import bpy

from scene_check.validators.base_validator import BaseValidator

bd = bpy.data
bc = bpy.context
bp = bpy.context.user_preferences


valid_types = { 'SOUND' }


class FinalingSequencer(BaseValidator):
	'''
	* Checks for all sequencer clips in the current scene 
	that are not audio and marks them for muting.
	'''

	def __init__(self):
		super(FinalingSequencer, self).__init__()

	def process_hook( self ):
		scene = bpy.context.scene

		if not scene.sequence_editor:
			return

		for clip in scene.sequence_editor.sequences:
			if not clip.type in valid_types and not clip.mute:
				self.error(
					ob=clip.name,
					select_func='sequence',
					type='FINALING:SEQUENCER',
					message=( 'Sequencer clip "{}" should be muted.'
							.format(clip.name) )
				)

				fix_code = (
					'clip = bpy.data.scenes["{}"].sequence_editor.sequences["{}"]\n'
					'clip.mute = True'
				).format( scene.name, clip.name )
			
				self.auto_fix_last_error(
					fix_code,
					message='Mute sequencer clip "{}".'.format( clip.name )
				)
