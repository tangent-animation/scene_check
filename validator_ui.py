## ======================================================================

from imp import reload
import os
import sys
import time

import bpy


## ======================================================================
## need to keep this here to keep things we're relying on from
## getting garbage collected before they're due
gc_guard = { 'result': {'errors':[], 'warnings':[]} }


## ======================================================================
def _draw_item(self, context, layout, data, item, icon, active_data, active_propname, index, flt_flag):
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

# Called once to filter/reorder items.
def _filter_items(self, context, data, propname):
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
	'''
	draw_item    = _draw_item
	filter_items = _filter_items

class MESH_UL_ValidatorWarnings( bpy.types.UIList ):
	'''
	Custom UI List class that allows for filtering in the search.
	Need two because every separate one needs a separate subclass--
	they all store information in RNA.
	'''
	draw_item    = _draw_item
	filter_items = _filter_items


## ======================================================================
class ValidatorList(bpy.types.PropertyGroup):
	label = bpy.props.StringProperty()
	type = bpy.props.StringProperty()
	description = bpy.props.StringProperty()
	error_index = bpy.props.IntProperty( min=0, options={ 'HIDDEN' } )


## ======================================================================
def clear_scene_error_list():
	scene = bpy.context.scene	

	for prop in scene.validator_errors, scene.validator_warnings:
		prop.clear()


## ======================================================================
class KikiValidatorRun(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "kiki.validator_run"
	bl_label = "Validator: Run"

	task_list = bpy.props.StringProperty()
	task_filter = bpy.props.StringProperty()

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
		path = 'C:/dev/blender/python'
		if not path in sys.path:
			sys.path.insert( 0, path )

		from scene_check import validator_factory
		reload(validator_factory)

		f = validator_factory.ValidatorFactory()
		gc_guard['result'] = result = f.run_all()

		error_count   = len( result['errors'] )
		warning_count = len( result['warnings'] )

		report_type = { 'INFO' } if not (error_count + warning_count) else { 'ERROR' }

		self.report(
			report_type,
			'Validation complete. {} Error{}, {} Warning{}.'
			.format(
				error_count,
				'' if error_count == 1 else 's',
				warning_count,
				'' if warning_count == 1 else 's',
			)
		)

		scene = context.scene

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

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorSelectError(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "kiki.validator_select_error"
	bl_label = "Validator: Select Error"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
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
			error.select_func(error)
		else:
			report_type = { 'ERROR' }
			self.report( report_type, 'No errors for selection.' )

		return {'FINISHED'}

	def invoke(self, context, event):
		return self.execute( context )


## ======================================================================
class KikiValidatorSelectWarning(bpy.types.Operator):
	"""Tooltip"""
	bl_idname = "kiki.validator_select_warning"
	bl_label = "Validator: Select Warning"

	@classmethod
	def poll(cls, context):
		return True

	def execute(self, context):
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
			warning.select_func(warning)
		else:
			report_type = { 'ERROR' }
			self.report( report_type, 'No warning for selection.' )

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

		error_count   = len(scene.validator_errors)
		warning_count = len(scene.validator_warnings)

		layout.operator( 'kiki.validator_run' )

		if not (error_count + warning_count):
			layout.label( "No errors or warnings found." )

		if error_count:
			layout.separator()
			layout.label( 'Validator Errors: {} Found'.format(error_count) )
			layout.template_list("MESH_UL_ValidatorErrors", "", context.scene, "validator_errors", 
					context.scene, "validator_errors_idx")
			layout.operator( 'kiki.validator_select_error' )

		if warning_count:
			layout.separator()
			layout.label( 'Validator Warnings: {} Found'.format(len(scene.validator_warnings)) )
			layout.template_list("MESH_UL_ValidatorWarnings", "", context.scene, "validator_warnings", 
					context.scene, "validator_warnings_idx")
			layout.operator( 'kiki.validator_select_warning' )


## ======================================================================
module_classes = [
	MESH_UL_ValidatorErrors, 
	MESH_UL_ValidatorWarnings, 
	ValidatorList, 
	KikiValidatorPanel, 
	KikiValidatorRun,
	KikiValidatorSelectError,
	KikiValidatorSelectWarning,
]

def register():
	scene = bpy.context.scene

	for cls in module_classes:
		bpy.utils.register_class( cls )

	bpy.types.Scene.validator_errors           = bpy.props.CollectionProperty( type=ValidatorList )
	bpy.types.Scene.validator_errors_idx       = bpy.props.IntProperty( default=0, min=0 )

	bpy.types.Scene.validator_warnings         = bpy.props.CollectionProperty( type=ValidatorList )
	bpy.types.Scene.validator_warnings_idx     = bpy.props.IntProperty( default=0, min=0 )

	clear_scene_error_list()


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
			'validator_warnings', 'validator_warnings_idx' ]:
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

