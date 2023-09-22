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
import bpy.utils.previews
import os
from .CustomFunctions import *

class ZapaintLayersData(bpy.types.PropertyGroup):

    def updateShading(self, context):
        ob = context.active_object
        if ob:
            material = ob.active_material
            if material:
                layers = material.zapaint_layers_layer
                nodeGroup = getNodeGroup(layers[getCollectionIndex(layers, len(layers)-1)])
                nodeTree = material.node_tree
                nodes = nodeTree.nodes

                BSDF_PRINCIPLED = None
                for node in nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        BSDF_PRINCIPLED = node

                if BSDF_PRINCIPLED:

                    if self.shading == 'PRINCIPLED_BSDF':
                        if self.lastShadingType == 1:
                            BSDF_PRINCIPLED.inputs[6].default_value = self.metallic
                            BSDF_PRINCIPLED.inputs[7].default_value = self.specular
                            BSDF_PRINCIPLED.inputs[9].default_value = self.roughness

                        for link in nodeTree.links:
                            if link.from_node.name == nodeGroup.name:
                                if link.to_socket.name == 'Emission':
                                    nodeTree.links.remove(link)
                        nodeTree.links.new(nodeGroup.outputs[0], BSDF_PRINCIPLED.inputs[0])

                        self.lastShadingType = 0

                    elif self.shading == 'EMISSIVE':
                        if self.lastShadingType == 0:
                            self.metallic = BSDF_PRINCIPLED.inputs[6].default_value
                            self.specular = BSDF_PRINCIPLED.inputs[7].default_value
                            self.roughness = BSDF_PRINCIPLED.inputs[9].default_value

                            BSDF_PRINCIPLED.inputs[6].default_value = 0
                            BSDF_PRINCIPLED.inputs[7].default_value = 0
                            BSDF_PRINCIPLED.inputs[9].default_value = 0

                        for link in nodeTree.links:
                            if link.from_node.name == nodeGroup.name:
                                if link.to_socket.name == 'Base Color':
                                    nodeTree.links.remove(link)
                            nodeTree.links.new(nodeGroup.outputs[0], BSDF_PRINCIPLED.inputs[19])
                            node.inputs[0].default_value = (0, 0, 0, 1)
                        self.lastShadingType = 1

    def updateTransparent(self, context):
        ob = context.active_object
        if ob:
            material = ob.active_material
            if material:
                layers = material.zapaint_layers_layer
                nodeGroup = getNodeGroup(layers[getCollectionIndex(layers, len(layers)-1)])
                nodeTree = material.node_tree
                nodes = nodeTree.nodes
                if self.transparent:
                    for node in nodes:
                        if node.type == "BSDF_PRINCIPLED":
                            nodeTree.links.new(nodeGroup.outputs[1], node.inputs[21])

                    material.use_backface_culling = True
                    material.blend_method = 'BLEND'
                    material.shadow_method = 'HASHED'

                else:
                    for link in nodeTree.links:
                        if link.from_node.name == nodeGroup.name:
                            if link.to_socket.name == 'Alpha':
                                nodeTree.links.remove(link)

                    material.use_backface_culling = False
                    material.blend_method = 'OPAQUE'
                    material.shadow_method = 'OPAQUE'

    shading: bpy.props.EnumProperty(items=[
        ('PRINCIPLED_BSDF', 'Principled BSDF', 'Principled BSDF'),
        ('EMISSIVE', 'Emissive', 'Emissive'),
    ], default='PRINCIPLED_BSDF', update=updateShading)

    transparent: bpy.props.BoolProperty(default=False, update=updateTransparent)

    lastShadingType: bpy.props.IntProperty(default=-1)
    metallic: bpy.props.FloatProperty()
    specular: bpy.props.FloatProperty()
    roughness: bpy.props.FloatProperty()

class ZapaintLayersLayer(bpy.types.PropertyGroup):

    def activeLayer(self, context):
        if self.update:
            if self.active:
                image = None
                if self.nodeGroupTree:
                    for node in self.nodeGroupTree.nodes:
                        if node.name.startswith("IMAGE_"):
                            image = node.image
                            break
                    if image:
                        material = context.object.active_material
                        if material:
                            context.scene.tool_settings.image_paint.mode = 'IMAGE'
                            context.tool_settings.image_paint.canvas = image
            if not self.active:
                self.active = True
            layers = context.active_object.active_material.zapaint_layers_layer
            for layer in layers:
                if layer.active:
                    if layer.index == self.index:
                        pass
                    else:
                        layer.update = False
                        layer.active = False
                        layer.update = True

    def updateOpacity(self, context):
        if self.update:
            opacity = None
            for node in self.nodeGroupTree.nodes:
                if node.type == "MATH":
                    opacity = node.inputs[1]
                    break
            if opacity:
                opacity.default_value = self.opacity/100

    def updateBlendMode(self, context):
        if self.update:
            for node in self.nodeGroupTree.nodes:
                if node.name.startswith('MIX_'):
                    node.blend_type = self.blendMode

    def isHidden(self, context):
        if self.update:
            if self.hide:
                for node in self.nodeGroupTree.nodes:
                    if node.type != "GROUP_INPUT" and node.type != "GROUP_OUTPUT":
                        node.mute = True
            else:
                for node in self.nodeGroupTree.nodes:
                    if node.type != "GROUP_INPUT" and node.type != "GROUP_OUTPUT":
                        node.mute = False

    def updateImage(self, context):
        for node in self.nodeGroupTree.nodes:
            if node.name.startswith("IMAGE_"):
                node.image = self.image

    def getImageDirty(self):
        if self.image:
            return self.image.is_dirty
        else:
            return False

    index: bpy.props.IntProperty(default=0)
    hide: bpy.props.BoolProperty(update=isHidden, default=False)
    lock: bpy.props.BoolProperty(default=False)
    opacity: bpy.props.FloatProperty(update=updateOpacity, min=0, max=100, default=100, subtype='PERCENTAGE')
    blendMode: bpy.props.EnumProperty(items=[
        ('MIX', 'Mix', 'Mix'),
        ('DARKEN', 'Darken', 'Darken'),
        ('MULTIPLY', 'Multiply', 'Multiply'),
        ('BURN', 'Color Burn', 'Color Burn'),
        ('LIGHTEN', 'Lighten', 'Lighten'),
        ('SCREEN', 'Screen', 'Screen'),
        ('DODGE', 'Color Dodge', 'Color Dodge'),
        ('ADD', 'Add', 'Add'),
        ('OVERLAY', 'Overlay', 'Overlay'),
        ('SOFT_LIGHT', 'Soft Light', 'Soft Light'),
        ('LINEAR_LIGHT', 'Linear Light', 'Linear Light'),
        ('DIFFERENCE', 'Difference', 'Difference'),
        ('SUBTRACT', 'Subtract', 'Subtract'),
        ('DIVIDE', 'Divide', 'Divide'),
        ('HUE', 'Hue', 'Hue'),
        ('SATURATION', 'Saturation', 'Saturation'),
        ('COLOR', 'Color', 'Color'),
        ('VALUE', 'Value', 'Value')
    ], update=updateBlendMode)
    update: bpy.props.BoolProperty(default=True)
    active: bpy.props.BoolProperty(update=activeLayer)
    nodeGroupTree: bpy.props.PointerProperty(type=bpy.types.NodeTree)
    link: bpy.props.BoolProperty(default=True)
    image: bpy.props.PointerProperty(type=bpy.types.Image, update=updateImage)


class Zapaint_op_Pack_Layer_Image(bpy.types.Operator):

    bl_idname = "zapaint.op_pack_layer_image"
    bl_label = "Pack Layer Image"
    bl_options = {'UNDO', 'INTERNAL'}

    index: bpy.props.IntProperty()

    def execute(self, context):
        material = context.active_object.active_material
        layers = material.zapaint_layers_layer
        for layer in layers:
            if layer.index == self.index:
                if layer.image.is_dirty:
                    layer.image.pack()
        return {'FINISHED'}


class Zapaint_op_LayersAddLayer(bpy.types.Operator):
    bl_idname = "zapaint.op_layers_add_layer"
    bl_label = "Create Layer"
    bl_options = {'UNDO', 'INTERNAL'}

    image_name: bpy.props.StringProperty(name='Name', default='Untitled')
    image_width: bpy.props.IntProperty(name='Width', default=1024)
    image_height: bpy.props.IntProperty(name='Height', default=1024)
    image_color: bpy.props.FloatVectorProperty(name='Color', subtype='COLOR', size=4, min=0, max=1)
    empty: bpy.props.BoolProperty(name='Empty Without Image')

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        material = context.active_object.active_material
        nodeTree = material.node_tree
        nodes = nodeTree.nodes
        layers = material.zapaint_layers_layer
        activeLayer = getActiveLayer(layers)
        lastNodeGroup = None
        nextNodeGroup = None
        index = 0

        if activeLayer:
            index = activeLayer.index + 1
            lastNodeGroup = getNodeGroup(activeLayer)
            if index < len(layers):
                nextIndex = index
                colIndex = getCollectionIndex(layers, nextIndex)
                nextNodeGroup = getNodeGroup(layers[colIndex])
            shiftLayersIndices(layers, index, 1)
        else:
            index = setLayerIndex(layers)
            if index > 0:
                lastIndex = index - 1
                colIndex = getCollectionIndex(layers, lastIndex)
                lastNodeGroup = getNodeGroup(layers[colIndex])
            shiftLayersIndices(layers, index, 1)

        name = "Layer"+str(index)
        layer, newNodeGroup = addLayer(self.empty, layers, nodes, index, name, self.image_name, self.image_width, self.image_height, self.image_color)
        nodes_linkLayers(material, layers, nodeTree, nodes, lastNodeGroup, newNodeGroup, nextNodeGroup)

        return {'FINISHED'}


class Zapaint_op_LayersDuplicate(bpy.types.Operator):
    bl_idname = "zapaint.op_layers_duplicate"
    bl_label = "Duplicate PSD Paint Layer"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def execute(self, context):
        material = context.active_object.active_material
        nodeTree = material.node_tree
        nodes = nodeTree.nodes
        layers = material.zapaint_layers_layer
        if layers:
            activeLayer = getActiveLayer(layers)
            if activeLayer:
                index = activeLayer.index+1
                shiftLayersIndices(layers, index, 1)
                image_name = activeLayer.image.name
                image_width = activeLayer.image.size[0]
                image_height = activeLayer.image.size[1]
                image_color = [0, 0, 0, 0]
                duplicateLayer(layers, nodes, index, activeLayer, image_name, image_width, image_height, image_color)
                nodes_linkLayers(material, layers, nodeTree, nodes, getNodeGroup(getLayerByIndex(layers, index-1)), getNodeGroup(getLayerByIndex(layers, index)), getNodeGroup(getLayerByIndex(layers, index+1)))

        return {'FINISHED'}


class Zapaint_op_LayersDeleteLayer(bpy.types.Operator):
    bl_idname = "zapaint.op_layers_delete_layer"
    bl_label = "Delete PSD Layer"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def execute(self, context):
        layers = context.active_object.active_material.zapaint_layers_layer
        activeLayer = getActiveLayer(layers)
        material = context.active_object.active_material
        nodeTree = material.node_tree

        if activeLayer:
            index = activeLayer.index
            collectionIndex = getCollectionIndex(layers, index)

            fromIndex = index + 1

            bpy.data.node_groups.remove(activeLayer.nodeGroupTree)
            nodeTree.nodes.remove(getNodeGroup(activeLayer))
            layers.remove(collectionIndex)

            shiftLayersIndices(layers, fromIndex, -1)
            if index != 0:
                if index != len(layers):
                    prevNodeGroup = getNodeGroup(getLayerByIndex(layers, index-1))
                    prevNodeGroupColorOutput = prevNodeGroup.outputs['Color']
                    prevNodeGroupAlphaOutput = prevNodeGroup.outputs['Alpha']

                    nodeTree.links.new(prevNodeGroupColorOutput, getNodeGroup(getLayerByIndex(layers, index)).inputs['Color'])
                    nodeTree.links.new(prevNodeGroupAlphaOutput, getNodeGroup(getLayerByIndex(layers, index)).inputs['Alpha'])
                else:
                    paint_layers_data = material.zapaint_layers_data
                    ZapaintLayersData.updateShading(paint_layers_data, context)
                    ZapaintLayersData.updateTransparent(paint_layers_data, context)

            setActiveLayer(layers, index)

        return {'FINISHED'}


class Zapaint_op_LayersUp(bpy.types.Operator):
    bl_idname = "zapaint.op_layers_up"
    bl_label = "Layer UP"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def execute(self, context):
        layers = context.active_object.active_material.zapaint_layers_layer
        paint_layers_data = context.active_object.active_material.zapaint_layers_data
        activeLayer = getActiveLayer(layers)
        switchLayers(layers, activeLayer, activeLayer.index, +1, paint_layers_data, ZapaintLayersData.updateShading, ZapaintLayersData.updateTransparent, context)
        return {'FINISHED'}


class Zapaint_op_LayersDown(bpy.types.Operator):
    bl_idname = "zapaint.op_layers_down"
    bl_label = "Layer Down"
    bl_options = {'UNDO', 'INTERNAL'}

    @classmethod
    def poll(cls, context):
        return context.active_object.active_material is not None

    def execute(self, context):
        layers = context.active_object.active_material.zapaint_layers_layer
        paint_layers_data = context.active_object.active_material.zapaint_layers_data
        activeLayer = getActiveLayer(layers)
        switchLayers(layers, activeLayer, activeLayer.index, -1, paint_layers_data, ZapaintLayersData.updateShading, ZapaintLayersData.updateTransparent, context)
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

            if material := ob.active_material:
                principled_BSDF = None
                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        principled_BSDF = node
                        break

                if principled_BSDF:
                    if material.psd_layers_layers:
                        row = layout.row()
                        row.prop(material.zapaint_layers_data, property='shading', text='')
                        row.prop(material.zapaint_layers_data, property='transparent', text='Transparent')

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
        pcoll = Zapaint_Layers_Preview["main"]
        new_layer = pcoll["new_layer"]
        duplicate_layer = pcoll["duplicate_layer"]
        trash = pcoll["trash"]
        brush = pcoll["brush"]

        ob = context.active_object

        if ob and ob.type == 'MESH':
            if material := ob.active_material:
                layout = self.layout.box()

                row = layout.row(align=True)
                row.scale_y = 1.5
                row.scale_x = 1.5
                material = context.active_object.active_material
                row = layout.row(align=True)
                row.enabled = True
                row.scale_y = 1.5
                row.scale_x = 1.5
                row.operator("zapaint.op_layers_add_layer", text='ADD LAYER', icon_value=new_layer.icon_id)

                layers = material.zapaint_layers_layer
                activeLayer = None
                if layers:
                    for layer in layers:
                        if layer.active:
                            activeLayer = layer
                            break

                if layers:
                    row3 = layout.row(align=True)
                    row3.scale_y = 1.5
                    col3 = layout.row(align=True)
                    col3.scale_y = 1.5

                    row2 = row.row(align=True)
                    row2.operator("zapaint.op_layers_up", text='', icon='TRIA_UP')
                    row2.operator("zapaint.op_layers_down", text='', icon='TRIA_DOWN')

                    row3.prop(activeLayer, property='blendMode', text='')
                    row3.prop(activeLayer, property='opacity', text='')

                    if activeLayer:
                        col3.template_ID_preview(layer, property="image", hide_buttons=True, rows=5, cols=8)

                        if not activeLayer.image:
                            col3.label(text="")
                    else:
                        for i in range(0, 7):
                            col3.label(text="")

                    for i in reversed(range(0, len(layers))):
                        layer = None
                        for layer in layers:
                            if layer.index == i:
                                layer = layer
                                break

                        box = layout.row()
                        rowbase = box.row(align=True)
                        rowbase.scale_y = 1.5
                        rowbase.scale_x = 1.5
                        row = rowbase.row(align=True)
                        row2 = rowbase.row(align=True)

                        active_icon = 'RADIOBUT_OFF'
                        hide_icon = 'HIDE_OFF'
                        lock_icon = 'UNLOCKED'

                        if layer.active:
                            active_icon = 'RADIOBUT_ON'

                        if layer.hide:
                            hide_icon = 'HIDE_ON'

                        if layer.lock:
                            lock_icon = 'LOCKED'
                            row.enabled = False
                            row2.enabled = False

                        row.prop(layer, property='active', icon=active_icon, text='', emboss=False)
                        row.prop(layer, property='hide', text='', icon=hide_icon)
                        row.scale_y = 1.0
                        row.scale_x = 1.0
                        row.prop(layer, property="name", text='')

                        iconPack = "PACKAGE"
                        if layer.image and layer.image.is_dirty:
                            row2.alert = True
                            iconPack = "UGLYPACKAGE"
                        op = row2.operator("zapaint.op_pack_layer_image", text='', icon=iconPack)
                        op.index = i
                        row3 = rowbase.row(align=True)
                        row3.operator("zapaint.op_layers_duplicate", text='', icon_value=duplicate_layer.icon_id)
                        row3.prop(layer, property='lock', text='', icon=lock_icon)
                        row3.operator("zapaint.op_layers_delete_layer", text='', icon_value=trash.icon_id)

            elif not ob.material_slots:
                layout = self.layout.box()
                row = layout.row()
                row.box().label(text="Add Material Slot!", icon="ERROR")

            else:
                layout = self.layout.box()
                row = layout.row()
                row.box().label(text="Select Material!", icon="ERROR")

Zapaint_Layers_Preview = {}

classes = (
    ZapaintLayersData,
    ZapaintLayersLayer,
    Zapaint_op_Pack_Layer_Image,
    Zapaint_op_LayersUp,
    Zapaint_op_LayersDown,
    Zapaint_op_LayersAddLayer,
    Zapaint_op_LayersDuplicate,
    Zapaint_op_LayersDeleteLayer,
    Zapaint_pl_Logs,
    Zapaint_pl_Materials,
    Zapaint_pl_Brush,
    Zapaint_pl_ColorPicker,
    Zapaint_pl_Palettes,
    Zapaint_pl_Layers,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    pcoll = bpy.utils.previews.new()

    absolute_path = os.path.dirname(__file__)
    relative_path = "icons"
    path = os.path.join(absolute_path, relative_path)

    pcoll.load("new_layer", os.path.join(path, "new_layer.png"), 'IMAGE')
    pcoll.load("duplicate_layer", os.path.join(path, "duplicate_layer.png"), 'IMAGE')
    pcoll.load("trash", os.path.join(path, "trash.png"), 'IMAGE')
    pcoll.load("brush", os.path.join(path, "brush.png"), 'IMAGE')
    Zapaint_Layers_Preview["main"] = pcoll

    bpy.types.Material.zapaint_layers_data = bpy.props.PointerProperty(type=ZapaintLayersData)
    bpy.types.Material.zapaint_layers_layer = bpy.props.CollectionProperty(type=ZapaintLayersLayer)

def unregister():
    for cls in classes:
        bpy.utils.unregister_class(cls)

    for pcoll in Zapaint_Layers_Preview.values():
        bpy.utils.previews.remove(pcoll)
    Zapaint_Layers_Preview.clear()

    del bpy.types.Material.zapaint_layers_data
    del bpy.types.Material.zapaint_layers_layer


if __name__ == "__main__":
    register()