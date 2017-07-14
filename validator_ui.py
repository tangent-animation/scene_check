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
		master_split = layout.split( 0.4)
		split = master_split.split( 0.3 )
		split.prop(item, "label", text="", emboss=False)
		split.label( item.type )
		master_split.prop(item, "description", text="", emboss=False)

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
class SCHEME_UL_ValidatorSchemes( bpy.types.UIList ):
	"""

	"""
	def filter_items(self, context, data, propname):
		'''
		Called once to filter/reorder items.
		'''

		column = getattr(data, propname)
		filter_name = self.filter_name.lower()

		flt_flags = [self.bitflag_filter_item if any(
				filter_name in filter_set for filter_set in ( str(i), item.label.lower() )
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

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
		'''
		Custom draw function for the custom UIList display class.
		'''

		self.use_filter_show = True

		if self.layout_type in {'DEFAULT', 'COMPACT'}:
			split = layout.split(0.15)
			split.prop( item, 'enabled', text="" )
			split.prop( item, "label", text="", emboss=False)

		elif self.layout_type in {'GRID'}:
			pass	

## ======================================================================
def set_active_text_block( text:bpy.types.Text ):
	editors = []
	for area in bpy.context.screen.areas:
		for space in area.spaces:
			if space.type == 'TEXT_EDITOR':
				space.text = text
				space.show_line_numbers     = True
				space.show_word_wrap        = True
				space.show_syntax_highlight = True


## ======================================================================
class SchemeValidatorList( bpy.types.PropertyGroup ):
	"""
	In-scene storage for the Validators when using Select mode 
	for the Scheme type.
	"""

	enabled = bpy.props.BoolProperty()
	label   = bpy.props.StringProperty()


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

	try:
		scene = bpy.context.scene	

		for prop in scene.validator_errors, scene.validator_warnings, scene.validator_auto_fixes:
			prop.clear()
	except:
		## probably starting up
		pass

## ======================================================================
def generate_schemes_list():
	"""
	Generates the information for the Schemes enum.
	"""
	from scene_check.validator_factory import ValidatorFactory
	vf = ValidatorFactory()

	result = [
		('All','All','Run all Validators', 0),
		('Selected','Selected', 'Run Validators from selection list', 1)
	]

	for index, scheme in enumerate(vf.schemes):
		scheme = scheme[0].upper() + scheme[1:]
		result.append(
			(scheme, scheme, 'Run scheme {}.'.format(scheme), index+2)
		)

	return result


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
def populate_scene_validators_list():
	"""
	Populates the scene Validators list for when using the Selected
	Scheme run type.
	"""

	scene = bpy.context.scene

	from scene_check.validator_factory import ValidatorFactory
	vf = ValidatorFactory()

	scene.validator_all.clear()

	for item in vf.modules:
		validator = scene.validator_all.add()
		validator.enabled = False
		validator.label   = item  


## ======================================================================
@persistent
def file_load_post_cb( *args ):
	print("+ ValidatorUI: File Load Callback.")
	clear_scene_error_list()
	gc_guard = deepcopy( result_default )


## ======================================================================
class KikiValidatorRun(bpy.types.Operator):
	"""
	Runs Validators based on selected Scheme type.
	"""
	bl_idname = "kiki.validator_run"
	bl_label = "Validator: Run"

	task_list = bpy.props.StringProperty()
	task_filter = bpy.props.StringProperty()

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		from scene_check import validator_factory
		reload( validator_factory )

		scene = context.scene

		scheme = scene.validator_scheme_type
		f = validator_factory.ValidatorFactory()

		if not scheme in { 'All','Selected' }:
			print( '+ Running Scheme "{}"...'.format(scheme) )
			result = f.run_scheme( scheme )
		elif scheme == 'Selected':
			print( '+ Running Selected...' )
			schemes = [ x.label for x in scene.validator_all if x.enabled ]
			print( "\t+ Validators: {}".format(str(schemes)) )
			result = f.run_all( *schemes )
		else:
			print( '+ Running All...' )
			result = f.run_all()
		
		gc_guard['result'] = result

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
		log.write( 'import bpy\n' )

		if not len( context.scene.validator_all ):
			populate_scene_validators_list()

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

			log.write( '"""{}"""'.format(repr(auto_fix)) )
			log.write( "\n\n{}\n\n".format(auto_fix.auto_fix) )
			set_active_text_block( log )

			result['auto_fixes'].pop( index )
			populate_scene_auto_fix_list()

		except Exception as e:
			error_msg = '-- Unable to run auto-fix (please see error log).'
			for item in '"""', auto_fix, error_msg, e.args[0], '"""':
				text = '\n{}\n'.format( item )
				print( text )
				log.write( text )

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

				log.write( '"""{}"""'.format(repr(auto_fix)) )
				log.write( "\n\n{}\n\n".format(auto_fix.auto_fix) )
				set_active_text_block( log )

				finished.append(index)

			except Exception as e:
				error_msg = '-- Unable to run auto-fix (please see error log).'
				
				for item in '"""', auto_fix, error_msg, e.args[0], '"""':
					text = '\n{}\n'.format( item )
					print( text )
					log.write( text )


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
class KikiValidatorSchemeClearAll(bpy.types.Operator):
	"""Clears the selection checks for Validators in the Selected Scheme type."""
	bl_idname = "kiki.validator_scheme_clear_all"
	bl_label = "Validator: Scheme Clear All"

	def invoke(self, context, event):
		populate_scene_validators_list()
		update_view()
		return { 'FINISHED' }


## ======================================================================
class KikiValidatorSchemeSelectAll(bpy.types.Operator):
	"""Enabled every Validator in the Selected Scheme type."""
	bl_idname = "kiki.validator_scheme_select_all"
	bl_label = "Validator: Scheme Select All"

	def invoke(self, context, event):
		for item in context.scene.validator_all:
			item.enabled = True
		update_view()
		return { 'FINISHED' }


## ======================================================================
class KikiValidatorPanel(bpy.types.Panel):
	"""Creates a Panel in the Object properties window"""
	bl_space_type = 'VIEW_3D'
	bl_region_type = 'TOOLS'
	bl_category = "AN"
	bl_label = "Scene Checker Tools"
	# bl_context = "scene"

	def draw(self, context):
		scene  = context.scene
		layout = self.layout

		error_count    = len( scene.validator_errors )
		warning_count  = len( scene.validator_warnings )
		auto_fix_count = len( scene.validator_auto_fixes )

		layout.prop( scene, 'validator_scheme_type', text='Scheme Type' )

		if scene.validator_scheme_type == 'Selected':
			layout.template_list( 'SCHEME_UL_ValidatorSchemes', "", scene, "validator_all",
								scene, "validator_all_idx" )

			split = layout.split( 0.5)
			split.operator( 'kiki.validator_scheme_select_all', text="Select All", icon='GHOST_ENABLED' )
			split.operator( 'kiki.validator_scheme_clear_all',  text="Clear All",  icon='GHOST_DISABLED' )

			selected = sum( [1 for x in scene.validator_all if x.enabled] )
			row = layout.row()
			row.alignment = 'CENTER'
			row.label( '{} Validator{} selected.'.format(selected, '' if selected == 1 else 's') )

			layout.separator()

		layout.operator( 'kiki.validator_run', icon='LOGIC' )
		layout.operator( 'kiki.validator_clear_all', icon='X' )

		split = layout.split( 0.5 )
		split.operator( 'kiki.validator_load', icon='LIBRARY_DATA_DIRECT' )
		split.operator( 'kiki.validator_save', icon='DISK_DRIVE' )

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
	SCHEME_UL_ValidatorSchemes,
	ValidatorList,
	SchemeValidatorList,
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
	KikiValidatorSchemeClearAll,
	KikiValidatorSchemeSelectAll,
]

def register():
	for cls in module_classes:
		bpy.utils.register_class( cls )

	bpy.types.Scene.validator_errors         = bpy.props.CollectionProperty( type=ValidatorList, options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_errors_idx     = bpy.props.IntProperty( default=0, min=0 )

	bpy.types.Scene.validator_warnings       = bpy.props.CollectionProperty( type=ValidatorList, options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_warnings_idx   = bpy.props.IntProperty( default=0, min=0 )

	bpy.types.Scene.validator_auto_fixes     = bpy.props.CollectionProperty( type=ValidatorList, options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_auto_fixes_idx = bpy.props.IntProperty( default=0, min=0 )

	bpy.types.Scene.validator_scheme_type = bpy.props.EnumProperty(
		items=generate_schemes_list(),
		description="Validator Scheme to run.",
		default='All'
	)

	bpy.types.Scene.validator_all = bpy.props.CollectionProperty( type=SchemeValidatorList,
																options={'SKIP_SAVE'} )
	bpy.types.Scene.validator_all_idx = bpy.props.IntProperty( default=0, min=0 )

	clear_scene_error_list()
	populate_scene_validators_list()

	## new feature: file load handler
	## remove the information on file load so the UI isn't broken

	if not file_load_post_cb in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.append( file_load_post_cb )


## ======================================================================
def unregister():
	for cls in module_classes:
		try:
			bpy.utils.unregister_class( cls )
		except:
			pass

	for prop in [ 'validator_errors', 'validator_errors_idx', 
			'validator_warnings', 'validator_warnings_idx',
			'validator_auto_fixes', 'validator_auto_fixes_idx',
			'validator_scheme_type', 'validator_all',
			]:
		locals_dict =  locals()
		try:
			exec( 'del bpy.types.Scene.{}'.format(prop), globals(), locals_dict ) 
		except:
			pass


	## new feature: file load handler
	if file_load_post_cb in bpy.app.handlers.load_post:
		bpy.app.handlers.load_post.remove( file_load_post_cb )


## ======================================================================
if __name__ == "__main__":
	unregister()
	register()
	print("Scene Check registered.")

