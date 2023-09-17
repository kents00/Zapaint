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
    bl_idname = "zapaint.op_materials"

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
    bl_idname = "zapaint.op_node"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_op_Brush(Operator):
    bl_label = ""
    bl_idname = "zapaint.op_brush"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_op_Palettes(Operator):
    bl_label = ""
    bl_idname = "zapaint.op_palettes"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_op_Layers(Operator):
    bl_label = ""
    bl_idname = "zapaint.op_layers"

    @classmethod
    def poll(cls,context):
        pass

    def execute(self,context):
        pass

class Zapaint_UI(Panel):
    bl_label = "Zapaint"
    bl_space_type = "VIEW_3D"
    bl_region_type = 'UI'
    bl_options = {'HEADER_LAYOUT_EXPAND'}
    bl_category = "Zapaint"

    @classmethod
    def poll(cls, context):
        return context.scene.render.engine == 'BLENDER_EEVEE'

    def draw(self, context):
        active_object = context.active_object
        if active_object and active_object.type != 'MESH':
            layout = self.layout.box()
            row = layout.row()
            row.label(text="Select an MESH Object", icon="ERROR")

class Zapaint_pl_Materials(Panel):
    bl_label = "Materials"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zapaint"
    bl_parent_id = "Zapaint_UI"
    bl_context = ''

    @classmethod
    def poll(cls,context):
        pass

    def draw(self, context):
        ob = context.active_object

        if ob and ob.type == 'MESH':
            layout = self.layout.box()
            row = layout.row()
            row.template_list("MATERIAL_UL_matslots", "", ob, "material_slots", ob, "active_material_index", rows=5)
            is_sortable = len(ob.material_slots) > 1
            col = row.column(align=True)
            col.operator("object.material_slot_add", icon='ADD', text="")
            col.operator("object.material_slot_remove", icon='REMOVE', text="")
            col.separator()
            col.menu("MATERIAL_MT_context_menu", icon='DOWNARROW_HLT', text="")
            if is_sortable:
                col.separator()
                col.operator("object.material_slot_move", icon='TRIA_UP', text="").direction = 'UP'
                col.operator("object.material_slot_move", icon='TRIA_DOWN', text="").direction = 'DOWN'
            row = layout.row()
            row.template_ID(ob, "active_material", new="material.new")

            if ob.mode == 'EDIT':
                row = layout.row(align=True)
                row.enabled = False
                row.enabled = True
                row.operator("object.material_slot_assign", text="Assign")
                row.operator("object.material_slot_select", text="Select")
                row.operator("object.material_slot_deselect", text="Deselect")

class Zapaint_pl_Node(Panel):
    bl_label = "Node"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zapaint"
    bl_parent_id = "Zapaint_UI"
    bl_context = ''

    @classmethod
    def poll(cls,context):
        pass

    def draw(self,context):
        pass

class Zapaint_pl_Brush(Panel):
    bl_label = "Brush"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zapaint"
    bl_parent_id = "Zapaint_UI"
    bl_context = ''

    @classmethod
    def poll(cls,context):
        pass

    def draw(self,context):
        pass

class Zapaint_pl_Layers(Panel):
    bl_label = "Layers"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zapaint"
    bl_parent_id = "Zapaint_UI"
    bl_context = ''

    @classmethod
    def poll(cls,context):
        pass

    def draw(self,context):
        pass

class Zapaint_pl_Palettes(Panel):
    bl_label = "Palettes"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "Zapaint"
    bl_parent_id = "Zapaint_UI"
    bl_context = ''

    @classmethod
    def poll(cls,context):
        pass

    def draw(self,context):
        pass


classes = (
    Zapaint_UI,
    Zapaint_pl_Materials,
    Zapaint_pl_Node,
    Zapaint_pl_Brush,
    Zapaint_pl_Layers,
    Zapaint_pl_Palettes,
    Zapaint_op_Materials,
    Zapaint_op_Node,
    Zapaint_op_Brush,
    Zapaint_op_Layers,
    Zapaint_op_Palettes,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

if __name__ == "__main__":
    register()