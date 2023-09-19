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

class Zapaint_UI:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Zapaint"
    bl_options = {"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'BLENDER_EEVEE'


class Zapaint_pl_Logs(Zapaint_UI,bpy.types.Panel):
    bl_idname = "Zapaint_pl_Logs"
    bl_label = "Zapaint"

    def draw(self, context):
        layout = self.layout
        layout.label(text="This is the main panel.")


class Zapaint_pl_Materials(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Materials"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Materials"

    def draw(self, context):
        layout = self.layout
        layout.label(text="First Sub Panel of Panel 1.")

class Zapaint_pl_Nodes(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Nodes"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Nodes"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Second Sub Panel of Panel 1.")

class Zapaint_pl_Brush(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Brush"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Brush"

    def draw(self, context):
        layout = self.layout
        layout.label(text="Third Sub Panel of Panel 1.")

class Zapaint_pl_Layers(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Layers"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Layers"


    def draw(self, context):
        layout = self.layout
        layout.label(text="Fourth Sub Panel of Panel 1.")

class Zapaint_pl_Palettes(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Palettes"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Palettes"


    def draw(self, context):
        layout = self.layout
        layout.label(text="Fifth Sub Panel of Panel 1.")

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