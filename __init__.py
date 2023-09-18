bl_info = {
    "name" : "Zapaint",
    "blender" : (3,6,1),
    "category" : "3D View",
    "location" : "3D View > Zapaint",
    "version" : (1,0),
    "author" : "Kent Edoloverio",
    "description" : "Paint your objects easily",
    "wiki_url" : "https://github.com/kents00/Zapaint",
    "tracker_url" : "https://github.com/kents00/Zapaint/issues",
    }

import bpy
import os
from bpy.types import Panel, Operator

class Zapaint_UI:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Zapaint"
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class Zapaint_pl_Logs(Zapaint_UI,bpy.types.Panel):
    bl_idname = "Zapaint_pl_Logs"
    bl_label = "Zapaint"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")


class Zapaint_pl_Materials(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Materials"
    bl_parentid = "Zapaint_pl_Logs"
    bl_label = "Materials"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")

class Zapaint_pl_Nodes(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Nodes"
    bl_parentid = "Zapaint_pl_Logs"
    bl_label = "Nodes"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")

class Zapaint_pl_Brush(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Brush"
    bl_parentid = "Zapaint_pl_Logs"
    bl_label = "Brush"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")

class Zapaint_pl_Layers(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Layers"
    bl_parentid = "Zapaint_pl_Logs"
    bl_label = "Layers"


    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")

class Zapaint_pl_Palettes(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Palettes"
    bl_parentid = "Zapaint_pl_Logs"
    bl_label = "Palettes"


    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")

classes = (
    Zapaint_pl_Logs,
    Zapaint_pl_Materials,
    Zapaint_pl_Nodes,
    Zapaint_pl_Brush,
    Zapaint_pl_Layers,
    Zapaint_pl_Palettes,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)


if __name__ == "__main__":
    register()
    register()