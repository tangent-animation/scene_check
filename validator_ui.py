## ======================================================================

from copy import deepcopy
from imp import reload
import json
import os
import sys
import time

import bpy
from bpy.app.handlers import persistent

path = os.path.dirname( os.path.abspath(__file__) )
if not path in sys.path:
	sys.path.insert( 0, path )

from scene_check.validators.base_validator import update_view

## ======================================================================
## need to keep this here to keep things we're relying on from
## getting garbage collected before they're due
result_default = { 'result': {'errors':[], 'warnings':[], 'auto_fixes':[] } }
gc_guard = deepcopy( result_default )

auto_fix_log_name = 'auto_fix_log.txt'


## ======================================================================
def _draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
	'''
	Custom draw function for the custom UIList display classes.
	'''

	self.use_filter_show = True

	if self.layout_type in {'DEFAULT', 'COMPACT'}:
		split = layout.split(0.2)
		split.prop(item, "label", text="", emboss=False)
		split = split.split(0.25)
		split.label( item.type )
		split = split.split(1.0)
		split.prop(item, "description", text="", emboss=False)

	elif self.layout_type in {'GRID'}:
		pass

def _filter_items(self, context, data, propname):
	'''
	Called once to filter/reorder items.
	'''

	column = getattr(data, propname)
	filter_name = self.filter_name.lower()

	flt_flags = [self.bitflag_filter_item if any(
			filter_name in filter_set for filter_set in (
				str(i), item.label.lower(), item.type.lower(), item.description.lower()
			)
		)
		else 0 for i, item in enumerate(column, 1)
	]

	if self.use_filter_sort_alpha:
		flt_neworder = [x[1] for x in sorted(
				zip(
					[x[0] for x in sorted(enumerate(column), key=lambda x: x[1].label)],
					range(len(column))
				)
			)
		]
	else:
		flt_neworder = []

	return flt_flags, flt_neworder


class MESH_UL_ValidatorErrors( bpy.types.UIList ):
	'''
	Custom UI List class that allows for filtering in the search.
	Need multiple because every separate one needs a separate subclass--
	they all store information in RNA.
	'''
	draw_item    = _draw_item
	filter_items = _filter_items


class MESH_UL_ValidatorWarnings( bpy.types.UIList ):
	'''
	Custom UI List class that allows for filtering in the search.
	'''
	draw_item    = _draw_item
	filter_items = _filter_items


class MESH_UL_ValidatorAutoFixes( bpy.types.UIList ):
	'''
	Custom UI List class that allows for filtering in the search.
	'''

class MESH_UL_ValidatorAutoFixes( bpy.types.UIList ):
	'''
	Custom UI List class that allows for filtering in the search.
	'''
	draw_item    = _draw_item
	filter_items = _filter_items


## ======================================================================
def set_active_text_block( text:bpy.types.Text ):
	editors = []
	for area in bpy.context.screen.areas:
		for space in area.spaces:
			if space.type == 'TEXT_EDITOR':
				space.text = text


## ======================================================================
class ValidatorList(bpy.types.PropertyGroup):
	'''
	In-scene storage for the Error and Warning UI fields.
	'''

	label = bpy.props.StringProperty()
	type = bpy.props.StringProperty()
	description = bpy.props.StringProperty()
	error_index = bpy.props.IntProperty( min=0, options={ 'HIDDEN' } )


## ======================================================================
def clear_scene_error_list():
	'''
	Clears the memory in-scene, wiping all Errors and Warnings.
	'''

	scene = bpy.context.scene	

	for prop in scene.validator_errors, scene.validator_warnings, scene.validator_auto_fixes:
		prop.clear()


## ======================================================================
def populate_scene_auto_fix_list():
	'''
	Once the data is collected in gc_guard, this function
	fills the in-scene Auto-fix memory spot for the UI to
	display, and for searching.

	This function is broken out on its own because the
	apply auto fix operator will remove the fix from
	the gc_guard result list.
	'''

	result = gc_guard.get( 'result', result_default )
	scene = bpy.context.scene

	scene.validator_auto_fixes.clear()

	for index, item in enumerate( result['auto_fixes'] ):
		auto_fix = scene.validator_auto_fixes.add()
		auto_fix.label       = item.parent
		auto_fix.type        = item.type
		auto_fix.description = item.message
		auto_fix.error_index = index

	update_view()


## ======================================================================
def populate_scene_error_list():
	'''
	Once the data is collected in gc_guard, this function
	fills the in-scene Error, Warning, and Auto-fix memory
	spots for the UI to display, and for searching.
	'''

	result = gc_guard['result']

	scene = bpy.context.scene

	clear_scene_error_list()

	for index, item in enumerate( result['errors'] ):
		error = scene.validator_errors.add()
		error.label       = item.parent
		error.type        = item.type
		error.description = item.message
		error.error_index = index

	for index, item in enumerate( result['warnings'] ):
		warning = scene.validator_warnings.add()
		warning.label       = item.parent
		warning.type        = item.type
		warning.description = item.message
		warning.error_index = index

	populate_scene_auto_fix_list()

	update_view()


## ======================================================================
@persistent
def file_load_post_cb( *args ):
	print("+ ValidatorUI: File Load Callback.")
	clear_scene_error_list()
	gc_guard = deepcopy( result_default )


## ======================================================================
class KikiValidatorRun(bpy.types.Operator):
	"""Runs all Validators."""
	bl_idname = "kiki.validator_run"
	bl_label = "Validator: Run"

	task_list = bpy.props.StringProperty()
	task_filter = bpy.props.StringProperty()

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		from scene_check import validator_factory
		reload(validator_factory)

		f = validator_factory.ValidatorFactory()
		gc_guard['result'] = result = f.run_all()

		error_count    = len( result['errors'] )
		warning_count  = len( result['warnings'] )
		auto_fix_count = len( result['auto_fixes'] )

		report_type = { 'INFO' } if not (error_count + warning_count) else { 'ERROR' }

		self.report(
			report_type,
			'Validation complete. {} Error{}, {} Warning{}, {} Auto-fix{}.'
			.format(
				error_count,
				'' if error_count == 1 else 's',
				warning_count,
				'' if warning_count == 1 else 's',
				auto_fix_count,
				'' if auto_fix_count == 1 else 'es',
			)
		)

		populate_scene_error_list()
		return {'FINISHED'}

	def invoke(self, context, event):
		if not auto_fix_log_name in bpy.data.texts:
			bpy.data.texts.new( auto_fix_log_name )
		log = bpy.data.texts[ auto_fix_log_name ]
		log.clear()
		return self.execute( context )


## ======================================================================
class KikiValidatorSave( bpy.types.Operator ):
	"""Saves the generated error list to a file."""
	bl_idname = "kiki.validator_save"
	bl_label = "Validator: Save JSON"

	filepath = bpy.props.StringProperty( subtype="FILE_PATH" )

	@classmethod
	def poll( cls, context ):
		scene = bpy.context.scene
		## intentionall returning the actual True / False objects
		return True if len(scene.validator_errors) else False

	def invoke( self, context, event ):
		context.window_manager.fileselect_add( self )
		return { 'RUNNING_MODAL' }

	def execute( self, context ):
		result = gc_guard['result']

		error_count   = len( result['errors'] )
		warning_count = len( result['warnings'] )
		auto_fix_count = len( result['auto_fixes'] )

		data = {
			'warnings':   [ x.to_dict() for x in result['warnings'] ],
			'errors':     [ x.to_dict() for x in result['errors'] ],
			'auto_fixes': [ x.to_dict() for x in result['auto_fixes'] ],
		}

		with open( self.filepath, 'w' ) as fp:
			try:
				json.dump( data, fp, indent=4 )
				self.report(
					{ 'INFO' },
					'Saved Error JSON to {}.'.format( self.filepath )
				)
			except:
				self.report(
					{ 'ERROR' },
					'Unable to save to {}.'.format( self.filepath )
				)

		return { 'FINISHED' }


## ======================================================================
class KikiValidatorLoad(bpy.types.Operator):
	"""Loads a previously-saved error list from a file."""
	bl_idname = "kiki.validator_load"
	bl_label = "Validator: Load JSON"

	filepath = bpy.props.StringProperty( subtype="FILE_PATH" )

	@classmethod
	def poll(cls, context):
		return True

	def invoke(self, context, event):
		context.window_manager.fileselect_add( self )
		return { 'RUNNING_MODAL' }

	def execute(self, context):
		from scene_check.validators import base_validator
		reload( base_validator )
		from scene_check.validators.base_validator import ValidationMessage

		data = None
		with open( self.filepath, 'r' ) as fp:
			data = json.load( fp )

		result = {
			'warnings': [ ValidationMessage().from_dict(x) for x in data['warnings'] ],
			'errors':   [ ValidationMessage().from_dict(x) for x in data['errors'] ],
			'auto_fixes':   [ ValidationMessage().from_dict(x) for x in data['auto_fixes'] ],
		}

		gc_guard['result'] = result

		populate_scene_error_list()

		self.report(
			{ 'INFO' },
			'Loaded Errors JSON from {}.'.format( self.filepath )
		)

		return { 'FINISHED' }


## ======================================================================
class KikiValidatorSelectError(bpy.types.Operator):
	"""Selects the objects related to the currently-selected Error."""
	bl_idname = "kiki.validator_select_error"
	bl_label = "Validator: Select Error"

	@classmethod
	def poll(cls, context):
		result = gc_guard.get( 'result', {'errors':[], 'warnings':[] } )
		index = context.scene.validator_errors_idx

		if not len( result['errors'] ):
			return False
		try:
			error = result['errors'][index]
		except:
			return False

		if error.select_func == 'null':
			return False

		return True

	def execute(self, context):
		from scene_check.validators import base_validator as bv
		reload(bv)
		from scene_check.validators.base_validator import get_select_func		

		scene = context.scene
		result = gc_guard.get( 'result', {'errors':[], 'warnings':[] } )

		try:
			bpy.ops.object.mode_set( mode='OBJECT' )
		except:
			pass

		error_count = len( result['errors'] )

		if error_count:
			index = scene.validator_errors_idx
			error = result['errors'][index]

			## tricksy
			# print( "Error: {} ({})".format( error.select_func, type(error.select_func)) )
			try:
				if error.select_func:
					func = get_select_func( error.select_func )
					func( error )
			except Exception as e:
				report_type = { 'ERROR' }
				self.report( report_type, 'Unable to select (likely due to Driven visibility).' )
				raise e

		else:
			report_type = { 'ERROR' }
			self.report( report_type, 'No errors for selection.' )

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorSelectWarning(bpy.types.Operator):
	"""Selects the objects related to the currently-selected Warning."""
	bl_idname = "kiki.validator_select_warning"
	bl_label = "Validator: Select Warning"

	@classmethod
	def poll(cls, context):
		result = gc_guard.get( 'result', {'errors':[], 'warnings':[] } )
		index = context.scene.validator_warnings_idx

		if not len( result['warnings'] ):
			return False
		try:
			warning = result['warnings'][index]
		except:
			return False

		if warning.select_func == 'null':
			return False

		return True

	def execute(self, context):
		from scene_check.validators import base_validator as bv
		reload(bv)
		from scene_check.validators.base_validator import get_select_func		

		scene = context.scene
		result = gc_guard.get( 'result', {'errors':[], 'warnings':[] } )

		try:
			bpy.ops.object.mode_set( mode='OBJECT' )
		except:
			pass

		error_count = len( result['warnings'] )

		if error_count:
			index = scene.validator_warnings_idx
			warning = result['warnings'][index]

			## tricksy
			try:
				func = get_select_func( warning.select_func )
				func( warning )
			except Exception as e:
				report_type = { 'ERROR' }
				self.report( report_type, 'Unable to select (likely due to Driven visibility).' )
				raise e
		else:
			report_type = { 'ERROR' }
			self.report( report_type, 'No warning for selection.' )

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
def auto_fix_poll( context:bpy.types.Context, run:bool=False, select:bool=False ) -> bool:
	"""
	Determines whether one of the auto-fix operators can run.

	:param context: The Blender context (currently not used)
	:param run: If True, tests whether the auto-fix can be run. Default: False.
	:param select: If True, tests whether the auto-fix can be selected. Default: False.

	:returns: True if the operator can be executed; False otherwise.
	"""

	if run and select:
		raise ValueError( 'auto_fix_poll: please only choose one of "run" and "select".' )

	result = gc_guard.get( 'result', result_default )
	index = context.scene.validator_auto_fixes_idx

	if not len( result['auto_fixes'] ):
		return False
	try:
		auto_fix = result['auto_fixes'][index]
	except:
		return False

	if run:
		if not auto_fix.auto_fix or auto_fix.auto_fix == '':
			return False
	if select:
		if not auto_fix.select_func or auto_fix.select_func == 'null':
			return False

	return True


## ======================================================================
class KikiValidatorSelectAutoFix(bpy.types.Operator):
	"""Selects the objects related to the currently-selected automatic fix."""
	bl_idname = "kiki.validator_select_auto_fix"
	bl_label = "Validator: Select Auto Fix"

	@classmethod
	def poll(cls, context):
		return auto_fix_poll( context, select=True )

	def execute(self, context):
		from scene_check.validators import base_validator as bv
		reload(bv)
		from scene_check.validators.base_validator import get_select_func		

		scene = context.scene
		result = gc_guard.get( 'result', result_default )

		try:
			bpy.ops.object.mode_set( mode='OBJECT' )
		except:
			pass

		fix_count = len( result['auto_fixes'] )

		if fix_count:
			index = scene.validator_auto_fixes_idx
			auto_fix = result['auto_fixes'][index]

			## tricksy
			try:
				func = get_select_func( auto_fix.select_func )
				func( auto_fix )
			except Exception as e:
				report_type = { 'ERROR' }
				self.report( report_type, 'Unable to select.' )
				raise e
		else:
			# print( result['auto_fixes'] )
			report_type = { 'ERROR' }
			self.report( report_type, 'No automatic fix for selection.' )

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorRunAutoFix( bpy.types.Operator ):
	"""Runs the currently-selected automatic fix."""
	bl_idname = "kiki.validator_run_auto_fix"
	bl_label = "Validator: Run Auto Fix"

	@classmethod
	def poll(cls, context):
		return auto_fix_poll( context, run=True )

	def execute(self, context):
		from scene_check.validators import base_validator as bv
		reload(bv)
		from scene_check.validators.base_validator import get_select_func		

		log = bpy.data.texts[ auto_fix_log_name ]

		scene    = context.scene
		result   = gc_guard.get( 'result', result_default )

		index    = scene.validator_auto_fixes_idx
		auto_fix = result['auto_fixes'][index]

		## tricksy
		try:
			print( auto_fix.auto_fix )
			exec( auto_fix.auto_fix )

			log.write( repr(auto_fix) )
			log.write( "\n\n{}\n\n".format(auto_fix.auto_fix) )
			set_active_text_block( log )

			result['auto_fixes'].pop( index )
			populate_scene_auto_fix_list()

		except Exception as e:
			report_type = { 'ERROR' }
			self.report( report_type, 'Unable to run auto-fix (please see error log).' )
			print( e )
			log.clear()
			log.write( str(e) )

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorRunAllAutoFixes( bpy.types.Operator ):
	"""Attempts to run all auto-fixes, removing the successful ones from the list."""
	bl_idname = "kiki.validator_run_all_auto_fixes"
	bl_label = "Validator: Run All Auto Fixes"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		from scene_check.validators import base_validator as bv
		reload(bv)
		from scene_check.validators.base_validator import get_select_func		

		log = bpy.data.texts[ auto_fix_log_name ]

		scene    = context.scene
		result   = gc_guard.get( 'result', result_default )

		finished = []
		for index, auto_fix in enumerate( result['auto_fixes'] ):
			try:
				print( auto_fix.auto_fix )
				exec( auto_fix.auto_fix )

				log.write( repr(auto_fix) )
				log.write( "\n\n{}\n\n".format(auto_fix.auto_fix) )
				set_active_text_block( log )

				finished.append(index)

			except Exception as e:
				report_type = { 'ERROR' }
				self.report( report_type, 'Unable to run auto-fix (please see error log).' )
				print( e )
				log.clear()
				log.write( str(e) )

		for index in reversed( finished ):
			result['auto_fixes'].pop( index )

		populate_scene_auto_fix_list()

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorClearAll(bpy.types.Operator):
	"""Clears the Errors and Warnings lists."""
	bl_idname = "kiki.validator_clear_all"
	bl_label = "Validator: Clear All"

	@classmethod
	def poll(cls, context):
		return len(context.scene.validator_errors) or len(context.scene.validator_warnings)
		return True

	def execute(self, context):
		gc_guard['result'] = result_default
		clear_scene_error_list()
		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorPanel(bpy.types.Panel):
	"""Creates a Panel in the Object properties window"""
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "AN"
	bl_label = "Validator"
	# bl_context = "scene"

	def draw(self, context):
		scene  = context.scene
		layout = self.layout

		error_count    = len( scene.validator_errors )
		warning_count  = len( scene.validator_warnings )
		auto_fix_count = len( scene.validator_auto_fixes )

		layout.operator( 'kiki.validator_run' )
		layout.operator( 'kiki.validator_clear_all' )

		split = layout.split( 0.5 )
		split.operator( 'kiki.validator_load' )
		split.operator( 'kiki.validator_save' )

		if not (error_count + warning_count):
			layout.label( "No errors or warnings found." )

		if error_count:
			col = layout.column()
			col.alert = True
			col.separator()
			col.label( 'Validator Errors: {} Found'.format(error_count), icon='ERROR' )
			col.template_list("MESH_UL_ValidatorErrors", "", context.scene, "validator_errors", 
					context.scene, "validator_errors_idx", item_dyntip_propname="description")
			col.operator( 'kiki.validator_select_error' )

		if warning_count:
			col = layout.column()
			col.separator()
			col.label( 'Validator Warnings: {} Found'.format(len(scene.validator_warnings)), icon='QUESTION' )
			col.template_list("MESH_UL_ValidatorWarnings", "", context.scene, "validator_warnings", 
					context.scene, "validator_warnings_idx", item_dyntip_propname="description")
			col.operator( 'kiki.validator_select_warning' )

		if auto_fix_count:
			col = layout.column()
			col.separator()
			col.label( 'Validator Automatic Fixes: {} Found'.format(len(scene.validator_auto_fixes)), icon='SAVE_COPY' )
			col.template_list("MESH_UL_ValidatorAutoFixes", "", context.scene, "validator_auto_fixes", 
					context.scene, "validator_auto_fixes_idx", item_dyntip_propname="description")
			col.operator( 'kiki.validator_select_auto_fix' )
			col.operator( 'kiki.validator_run_auto_fix' )
			col.operator( 'kiki.validator_run_all_auto_fixes' )


## ======================================================================
module_classes = [
	MESH_UL_ValidatorErrors, 
	MESH_UL_ValidatorWarnings, 
	MESH_UL_ValidatorAutoFixes, 
	ValidatorList, 
	KikiValidatorPanel, 
	KikiValidatorRun,
	KikiValidatorSelectError,
	KikiValidatorSelectWarning,
	KikiValidatorSelectAutoFix,
	KikiValidatorRunAutoFix,
	KikiValidatorRunAllAutoFixes,
	KikiValidatorLoad,
	KikiValidatorSave,
	KikiValidatorClearAll,
]

def register():
	for cls in module_classes:
		bpy.utils.register_class( cls )

	bpy.types.Scene.validator_errors       = bpy.props.CollectionProperty( type=ValidatorList, options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_errors_idx   = bpy.props.IntProperty( default=0, min=0 )

	bpy.types.Scene.validator_warnings     = bpy.props.CollectionProperty( type=ValidatorList, options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_warnings_idx = bpy.props.IntProperty( default=0, min=0 )

	bpy.types.Scene.validator_auto_fixes     = bpy.props.CollectionProperty( type=ValidatorList, options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_auto_fixes_idx = bpy.props.IntProperty( default=0, min=0 )

	clear_scene_error_list()

	## new feature: file load handler
	## remove the information on file load so the UI isn't broken

	if not file_load_post_cb in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append( file_load_post_cb )

## ======================================================================
def unregister():
	for cls in module_classes:
		bpy.utils.register_class( cls )
		try:
			bpy.utils.unregister_class( cls )
		except:
			pass

	scene = bpy.types.Scene

	for prop in [ 'validator_errors', 'validator_errors_idx', 
			'validator_warnings', 'validator_warnings_idx',
			'validator_auto_fixes', 'validator_auto_fixes_idx',
			 ]:
		locals_dict = locals()
		try:
			exec( 'del scene.{}'.format(prop), globals(), locals_dict ) 
		except:
			pass


	## new feature: file load handler
	if file_load_post_cb in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove( file_load_post_cb )


## ======================================================================
if __name__ == "__main__":
	unregister()
	register()
	print("Test registered.")

