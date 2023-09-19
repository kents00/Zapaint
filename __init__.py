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