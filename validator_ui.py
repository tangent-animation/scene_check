## ======================================================================

from imp import reload
import json
import os
import sys
import time

import bpy

path = os.path.dirname( os.path.abspath(__file__) )
if not path in sys.path:
	sys.path.insert( 0, path )

from scene_check.validators.base_validator import update_view

## ======================================================================
## need to keep this here to keep things we're relying on from
## getting garbage collected before they're due
gc_guard = { 'result': {'errors':[], 'warnings':[]} }


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
	draw_item    = _draw_item
	filter_items = _filter_items

	def draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
		outliner = context.screen.tangent_outliner     
		asset_map = outliner.asset_map
		proxy_map = outliner.proxy_map
				
		row = layout.row(align = True)
		
		if outliner.list_mode == 'LINKED':
			row.prop(item, "select_both", text="")
			
			obj = proxy_map[item.name] if item.name in proxy_map else item
			if obj and obj.dupli_group:
				res = resolution_tools.asset_resolutions[obj.dupli_group.asset_resolution]['short']
				name = "(%s) %s" % (res, item.name)
			else:
				name = item.name
 
			row.label(text=name, icon = 'GROUP')            
			#row.prop(item, "name", text="", emboss=False)        
			if item.hide:
				row.label(text="", icon = 'RESTRICT_VIEW_ON')          
			if obj:
				object_icon = 'OBJECT_DATA' if obj.select else 'MATCUBE'
				row.prop(obj, "select", text="", icon = object_icon, toggle=True, emboss=False)
			proxy = asset_map[item.name] if not item.proxy and item.name in asset_map else item
			if proxy:
				armature_icon = 'OUTLINER_OB_ARMATURE' if proxy.select else 'ARMATURE_DATA'
				row.prop(proxy, "select", text="", icon = armature_icon, toggle=True, emboss=False)

		else:
			row.prop(item, "select", text="")
			row.prop(item, "name", text="", emboss=False, icon = 'OUTLINER_OB_' + item.type)

	def draw_filter(self, context, layout):
		outliner = context.screen.tangent_outliner
	
		col = layout.column()
		row = col.row(align = True)
		if outliner.list_mode == 'LINKED':
			split = row.split(percentage = 0.75, align = True)
			split.prop(outliner, "list_mode", text="")
			split.prop(outliner, "active_object_type", text = "")
		else:
			row.prop(outliner, "list_mode", text="")
		
		row = col.row(align = True)
		row.operator("tangent_outliner.select_all", text="Select All").select = True
		row.operator("tangent_outliner.select_all", text="Deselect All").select = False
	
	def filter_items(self, context, data, property):
		'''
		This is a callback that filters the object list.
		bitflag_filter_item is a bit reserved for setting whether to show the item.
		LINKED: Show only the linked objects that have proxies
		LOCAL: Show only the locally created objects
		ALL: Show all the objects in the scene
		'''
		self.use_filter_show = True
		
		objs = getattr(data, property)
		
		flt_flags = [self.bitflag_filter_item] * len(objs)
		flt_neworder = [] #Not used, return empty for optimization
	  
		outliner = context.screen.tangent_outliner
	  
		displayed_objects = outliner.displayed_objects
		displayed_objects.clear()
		
		asset_map = outliner.asset_map
		asset_map.clear()
		
		proxy_map = outliner.proxy_map
		proxy_map.clear()
				  
		if outliner.list_mode == 'LINKED':
			for idx, obj in enumerate(objs):
				if self.is_linked(obj):
					if obj.proxy:
						proxy_group = self.find_user_object(context, obj.proxy)
						proxy_map[obj.name] = proxy_group
						if proxy_group: 
							asset_map[proxy_group.name] = obj

						if outliner.active_object_type == 'PROXY':
							displayed_objects.append(obj)
						else:
							flt_flags[idx] &= ~self.bitflag_filter_item #hide proxy
						
					else:
						if not obj.name in asset_map:
							asset_map[obj.name] = None
						 
						if outliner.active_object_type == 'GROUP':                        
							displayed_objects.append(obj) 
						else:
							flt_flags[idx] &= ~self.bitflag_filter_item #hide group
						   
				else:
					flt_flags[idx] &= ~self.bitflag_filter_item #hide obj  
			
		elif outliner.list_mode == 'LOCAL':
			for idx, obj in enumerate(objs):
				if self.is_linked(obj):
					flt_flags[idx] &= ~self.bitflag_filter_item #hide obj
				else:
					displayed_objects.append(obj)
		else:
			for obj in objs:
				displayed_objects.append(obj)
				
		return (flt_flags, flt_neworder)
		
	def is_linked(self, obj):
		if obj.library:
			return True
		if obj.data and obj.data.library:
			return True
		if obj.dupli_group and obj.dupli_group.library:
			return True
			
		return False
	
	def find_user_object(self, context, proxy):
		for group in proxy.users_group:
			for dupli_group in group.users_dupli_group: 
				if dupli_group.name in context.scene.objects:
					return dupli_group


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
def populate_scene_error_list():
	'''
	Once the data is collected in gc_guard, this function
	fills the in-scene Error and Warning memory spots for
	the UI to display, and for searching.
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

	for index, item in enumerate( result['auto_fixes'] ):
		auto_fix = scene.validator_auto_fixes.add()
		auto_fix.label       = item.parent
		auto_fix.type        = item.type
		auto_fix.description = item.message
		auto_fix.error_index = index

	update_view()


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
		index = context.scene.validator_errors_idx

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
class KikiValidatorClearAll(bpy.types.Operator):
	"""Clears the Errors and Warnings lists."""
	bl_idname = "kiki.validator_clear_all"
	bl_label = "Validator: Clear All"

	@classmethod
	def poll(cls, context):
		return len(context.scene.validator_errors) or len(context.scene.validator_warnings)
		return True

	def execute(self, context):
		gc_guard['result'] = { 'errors':[], 'warnings':[], 'auto_fixes':[] }
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
			col.label( 'Validator Automatic Fixes: {} Found'.format(len(scene.validator_warnings)), icon='QUESTION' )
			col.template_list("MESH_UL_ValidatorWarnings", "", context.scene, "validator_auto_fixes", 
					context.scene, "validator_auto_fixes_idx", item_dyntip_propname="description")
			# col.operator( 'kiki.validator_select_auto_fixes' )
			# col.operator( 'kiki.validator_select_auto_fixes' )


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


## ======================================================================
def unregister():
	for cls in module_classes:
		bpy.utils.register_class( cls )
		try:
			bpy.utils.unregister_class( cls )
		except:
			pass

	Scene = bpy.types.Scene

	for prop in [ 'validator_errors', 'validator_errors_idx', 
			'validator_warnings', 'validator_warnings_idx',
			'validator_auto_fixes', 'validator_auto_fixes_idx',
			 ]:
		locals_dict = locals()
		try:
			exec( 'del Scene.{}'.format(prop), globals(), locals_dict ) 
		except:
			pass


## ======================================================================
if __name__ == "__main__":
	unregister()
	register()
	print("Test registered.")

