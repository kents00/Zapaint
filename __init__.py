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

class UnifiedPaintPanel:

    @staticmethod
    def get_brush_mode(context):
        """ Get the correct mode for this context. For any context where this returns None,
            no brush options should be displayed."""
        mode = context.mode

        from bl_ui.space_toolsystem_common import ToolSelectPanelHelper
        tool = ToolSelectPanelHelper.tool_active_from_context(context)

        if not tool:
            # If there is no active tool, then there can't be an active brush.
            return None

        if not tool.has_datablock:
            # tool.has_datablock is always true for tools that use brushes.
            return None

        space_data = context.space_data
        tool_settings = context.tool_settings

        if space_data:
            space_type = space_data.type
            if space_type in {'VIEW_3D', 'PROPERTIES'}:
                if mode == 'PAINT_TEXTURE':
                    if tool_settings.image_paint:
                        return mode
                    else:
                        return None
                return mode
        return None

    @staticmethod
    def paint_settings(context):
        tool_settings = context.tool_settings

        mode = UnifiedPaintPanel.get_brush_mode(context)

        # 3D paint settings
        if mode == 'PAINT_TEXTURE':
            return tool_settings.image_paint
        return None

    @staticmethod
    def prop_unified(
            layout,
            context,
            brush,
            prop_name,
            unified_name=None,
            pressure_name=None,
            icon='NONE',
            text=None,
            slider=False,
            header=False,
    ):
        """ Generalized way of adding brush options to the UI,
            along with their pen pressure setting and global toggle, if they exist. """
        row = layout.row(align=True)
        ups = context.tool_settings.unified_paint_settings
        prop_owner = brush
        if unified_name and getattr(ups, unified_name):
            prop_owner = ups

        row.prop(prop_owner, prop_name, icon=icon, text=text, slider=slider)

        if pressure_name:
            row.prop(brush, pressure_name, text="")

        if unified_name and not header:
            # NOTE: We don't draw UnifiedPaintSettings in the header to reduce clutter. D5928#136281
            row.prop(ups, unified_name, text="", icon='BRUSHES_ALL')

        return row

    @staticmethod
    def prop_unified_color(parent, context, brush, prop_name, *, text=None):
        ups = context.tool_settings.unified_paint_settings
        prop_owner = ups if ups.use_unified_color else brush
        parent.prop(prop_owner, prop_name, text=text)

    @staticmethod
    def prop_unified_color_picker(parent, context, brush, prop_name, value_slider=True):
        ups = context.tool_settings.unified_paint_settings
        prop_owner = ups if ups.use_unified_color else brush
        parent.template_color_picker(prop_owner, prop_name, value_slider=value_slider)


class Zapaint_op_PasteHexColor(bpy.types.Operator):
    bl_idname = "zapaintop.paste_colors"
    bl_label = "Paste HEX"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        obj = context.object
        return (obj and obj.type == 'MESH' and context.tool_settings.image_paint.palette)

    @staticmethod
    def PastehexColors(self, context):
        url = str(context.window_manager.clipboard)
        color = False
        color_text = []
        i = 0
        length = len(url) - 5
        while i < length:
            color_text = url[i:i+6]
            color = True
            for char in color_text:
                if char not in ("0", "1", "2", "3", "4", "5", "6", "7", "8", "9", 'a', 'A', 'b', 'B', 'c', 'C', 'd', 'D', 'e', 'E', 'f', 'F'):
                    color = False
                    i += 1
                    break
            if color:
                R = int(color_text[:2], base=16)/255
                G = int(color_text[2:4], base=16)/255
                B = int(color_text[4:6], base=16)/255
                RGB_color = (R, G, B)
                bpy.context.tool_settings.image_paint.brush.color = RGB_color
                bpy.ops.palette.color_add()
                i += 6

    def execute(self, context):
        self.PastehexColors(self=self, context=context)
        return {'FINISHED'}

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


class Zapaint_pl_Brush(UnifiedPaintPanel,Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Brush"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Brush"

    def draw(self, context):
        layout = self.layout

        if context.active_object and context.active_object.type == 'MESH':
            settings = self.paint_settings(context)

            if settings is not None:
                brush = settings.brush

                row = layout.row()
                large_preview = True
                if large_preview:
                    row.column().template_ID_preview(settings, "brush", new="brush.add", rows=3, cols=8, hide_buttons=False)
                else:
                    row.column().template_ID(settings, "brush", new="brush.add")
                col = row.column()
                col.menu("VIEW3D_MT_brush_context_menu", icon='DOWNARROW_HLT', text="")

                if brush is not None:
                    col.prop(brush, "use_custom_icon", toggle=True, icon='FILE_IMAGE', text="")

                    if brush.use_custom_icon:
                        layout.prop(brush, "icon_filepath", text="")
            else:
                layout.label(text="Switch to Texture Paint Mode", icon='ERROR')
        else:
            layout.label(text="Select a mesh object to paint", icon='ERROR')

class Zapaint_pl_ColorPicker(Zapaint_UI,bpy.types.Panel):
    bl_idname = "Zapaint_pl_ColorPicker"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Color Picker"

    def draw(self,context):
        layout = self.layout.box()
        col = layout.column()
        if context.active_object and context.active_object.type == 'MESH':
            brush = context.tool_settings.image_paint.brush
            if not brush:
                col.label(text="Switch to Texture Paint Mode", icon='ERROR')
            else:
                if context.tool_settings.image_paint.palette:
                    if brush.color_type == 'COLOR':
                        UnifiedPaintPanel.prop_unified_color_picker(layout, context, brush, "color", value_slider=True)
                        row = layout.row(align=True)
                        UnifiedPaintPanel.prop_unified_color(row, context, brush, "color", text="")
                        UnifiedPaintPanel.prop_unified_color(row, context, brush, "secondary_color", text="")
                        row.separator()
                        row.operator("paint.brush_colors_flip", icon='FILE_REFRESH', text="", emboss=False)
                    elif brush.color_type == 'GRADIENT':
                        layout.template_color_ramp(brush, "gradient", expand=True)
                        layout.use_property_split = True
                        col = layout.column()

                        if brush.image_tool == 'DRAW':
                            UnifiedPaintPanel.prop_unified(
                                col,
                                context,
                                brush,
                                "secondary_color",
                                unified_name="use_unified_color",
                                text="Background Color",
                                header=True,
                            )

                            col.prop(brush, "gradient_stroke_mode", text="Gradient Mapping")
                            if brush.gradient_stroke_mode in {'SPACING_REPEAT', 'SPACING_CLAMP'}:
                                col.prop(brush, "grad_spacing")
                    else:
                        col.label(text="Create New Color Palette", icon='ERROR')
                else:
                    col.label(text="Create New Color Palette", icon='ERROR')


class Zapaint_pl_Palettes(UnifiedPaintPanel,Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Palettes"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Palettes"

    def draw(self, context):
        ob = context.active_object
        if ob and ob.type == 'MESH':
            tool_settings = context.tool_settings.image_paint
            layout = self.layout.box()
            col = layout.column()
            col.template_ID(tool_settings, "palette", new="palette.new")

            brush = context.tool_settings.image_paint.brush
            if not brush:
                col.label(text="Switch to Texture Paint Mode", icon='ERROR')
            if tool_settings.palette:
                    col.template_palette(tool_settings, "palette", color=True)

class Zapaint_pl_Layers(Zapaint_UI, bpy.types.Panel):
    bl_idname = "Zapaint_pl_Layers"
    bl_parent_id = "Zapaint_pl_Logs"
    bl_label = "Layers"


    def draw(self, context):
        layout = self.layout
        layout.label(text="Fourth Sub Panel of Panel 1.")


classes = (
    Zapaint_op_PasteHexColor,
    Zapaint_pl_Logs,
    Zapaint_pl_Materials,
    Zapaint_pl_Nodes,
    Zapaint_pl_Brush,
    Zapaint_pl_ColorPicker,
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