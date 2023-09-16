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


class Zapaint_op_Shaders(Operator):
    bl_label = ""
    bl_idname = "zapaint.op.shaders"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_op_Node(Operator):
    bl_label = ""
    bl_idname = "zapaint.op.node"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_op_Palettes(Operator):
    bl_label = ""
    bl_idname = "zapaint.op.palettes"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_op_Layers(Operator):
    bl_label = ""
    bl_idname = "zapaint.op.layers"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_pl_Base:
    bl_idname = "Zapaint_pl_Base"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'TOOLS' if bpy.app.version < (2, 80) else 'UI'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_category = "PiXel"
    bl_order = 0
    bl_ui_units_x=1

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'BLENDER_EEVEE'

class Zapaint_pl_Shaders(Zapaint_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Base"
    bl_label = "Shaders"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        pass

class Zapaint_pl_Node(Zapaint_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Base"
    bl_label = "Shaders"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        pass

class Zapaint_pl_Palettes(Zapaint_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Base"
    bl_label = "Palettes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 2

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        pass

class Zapaint_pl_Layers(Zapaint_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Base"
    bl_label = "Layers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        pass

classes = (
    Zapaint_pl_Base,
    Zapaint_pl_Layers,
    Zapaint_pl_Node,
    Zapaint_pl_Palettes,
    Zapaint_pl_Layers,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()