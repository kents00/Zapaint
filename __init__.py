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


class Zapaint_op_Materials(Operator):
    bl_label = ""
    bl_idname = "zapaint.op.materials"

    @classmethod
    def poll(cls,context):
        if context.active_object and context.active_object.type == 'MESH':
            if not context.active_object.data.materials:
                return True
        return False

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

class Zapaint_op_Brush(Operator):
    bl_label = ""
    bl_idname = "zapaint.op.brush"

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

    def draw(self,context):
        if context.active_object and context.active_object.type != 'MESH':
            layout = self.layout.box()
            row = layout.row()
            row.label(text="Select an Object", icon="ERROR")

class Zapaint_pl_Materials(Zapaint_pl_Base,Panel):
    bl_parent_id = "PiXel_pl_Base"
    bl_label = "Materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 1

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        _object = context.active__object

        if _object and _object.type == 'MESH':
            layout = self.layout.box()
            row = layout.row()
            row.template_list("MATERIAL_UL_matslots", "", _object, "material_slots", _object, "active_material_index", rows=5)
            is_sortable = len(_object.material_slots) > 1
            col = row.column(align=True)
            col.operator("_object.material_slot_add", icon='ADD', text="")
            col.operator("_object.material_slot_remove", icon='REMOVE', text="")
            col.separator()
            col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")
            if is_sortable:
                col.separator()
                col.operator("_object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("_object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
            row = layout.row()
            row.template_ID(_object, "active_material", new="material.new")

            if _object.mode == 'EDIT':
                row = layout.row(align=True)
                row.enabled = False
                row.enabled = True
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

class Zapaint_pl_Node(Zapaint_pl_Base,Panel):
    bl_parent_id = "Zapaint_pl_Base"
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
class Zapaint_pl_Brush(Zapaint_pl_Base,Panel):
    bl_parent_id = "Zapaint_pl_Base"
    bl_label = "Brush"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 3

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        pass

class Zapaint_pl_Palettes(Zapaint_pl_Base,Panel):
    bl_parent_id = "Zapaint_pl_Base"
    bl_label = "Palettes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return not False

    def draw(self, context):
        pass

class Zapaint_pl_Layers(Zapaint_pl_Base,Panel):
    bl_parent_id = "Zapaint_pl_Base"
    bl_label = "Layers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_context = ''
    bl_order = 5

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