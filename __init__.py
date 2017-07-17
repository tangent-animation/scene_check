from imp import reload
import bpy

bl_info = {
    "name": "Kiki's Scene Check",
    "author": "kiki",
    "version": (0, 2, 1),
    "blender": (2, 78),
    "location": "Everywhere!",
    "description": "Asset Validation Tools",
    "warning": "",
    "wiki_url": "https://google.com",
    "tracker_url": "https://google.com",
    "category": "kiki",
}

def register():
	from . import validator_ui
	reload( validator_ui )
	return validator_ui.register()

def unregister():
	return validator_ui.unregister()

