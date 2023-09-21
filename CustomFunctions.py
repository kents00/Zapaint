# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

import bpy
import mathutils
import datetime


def getActiveLayer(layers):
    if layers:
        for layer in layers:
            if layer.active:
                return layer
    return None


def setActiveLayer(layers, index):
    index = 0 if index == 0 else index-1
    if layers:
        for layer in layers:
            if layer.index == index:
                layer.active = True
                break


def setLayerIndex(layers):
    if layers:
        return len(layers)
    return 0


def updateLayersIndices(layers, deletedIndex):
    if layers:
        if layers.index > deletedIndex:
            layers.index -= 1


def shiftLayersIndices(layers, fromIndex, shiftValue):
    if layers:
        for i in reversed(range(0, len(layers))):
            if layers[i].index >= fromIndex:
                layers[i].index += shiftValue
            else:
                nodeGroup = getNodeGroup(layers[i])
                nodeGroup.location -= mathutils.Vector((shiftValue*200, 0))


def switchLayers(layers, activeLayer, index, value, paint_layers_data, UpdateShading, UpdateTransparent, context):
    if layers:
        if activeLayer:
            nextIndex = index + value
            if nextIndex >= 0 and nextIndex < len(layers):
                for layer in layers:
                    if layer.index == nextIndex:
                        material = bpy.context.active_object.active_material
                        if material:
                            nodeTree = material.node_tree

                            nodeGroup = getNodeGroup(layer)
                            activeNodeGroup = getNodeGroup(activeLayer)
                            activeLayer.index = nextIndex
                            activeNodeGroup.location += mathutils.Vector((value*200, 0))

                            activeNodeGroupColorInput = activeNodeGroup.inputs['Color']
                            activeNodeGroupAlphaInput = activeNodeGroup.inputs['Alpha']
                            activeNodeGroupColorOutput = activeNodeGroup.outputs['Color']
                            activeNodeGroupAlphaOutput = activeNodeGroup.outputs['Alpha']

                            for input in activeNodeGroup.inputs:
                                if input.is_linked:
                                    nodeTree.links.remove(input.links[0])
                            for output in activeNodeGroup.outputs:
                                if output.is_linked:
                                    nodeTree.links.remove(output.links[0])

                            layer.index = index
                            nodeGroup.location += mathutils.Vector((-value*200, 0))

                            if value == 1:
                                prevNodeGroup = getNodeGroup(getLayerByIndex(layers, index))
                                prevNodeGroupColorOutput = prevNodeGroup.outputs['Color']
                                prevNodeGroupAlphaOutput = prevNodeGroup.outputs['Alpha']

                                nodeTree.links.new(prevNodeGroupColorOutput, activeNodeGroupColorInput)
                                nodeTree.links.new(prevNodeGroupAlphaOutput, activeNodeGroupAlphaInput)

                                if nextIndex + 1 < len(layers):
                                    nextNodeGroup = getNodeGroup(getLayerByIndex(layers, nextIndex+1))
                                    nextNodeGroupColorInput = nextNodeGroup.inputs['Color']
                                    nextNodeGroupAlphaInput = nextNodeGroup.inputs['Alpha']

                                    nodeTree.links.new(activeNodeGroupColorOutput, nextNodeGroupColorInput)
                                    nodeTree.links.new(activeNodeGroupAlphaOutput, nextNodeGroupAlphaInput)
                                else:
                                    UpdateShading(paint_layers_data, context)
                                    UpdateTransparent(paint_layers_data, context)

                                if index - 1 >= 0:
                                    oldPrevNodeGroup = getNodeGroup(getLayerByIndex(layers, index-1))

                                    oldPrevNodeGroupColorOutput = oldPrevNodeGroup.outputs['Color']
                                    oldPrevNodeGroupAlphaOutput = oldPrevNodeGroup.outputs['Alpha']

                                    nodeTree.links.new(oldPrevNodeGroupColorOutput, prevNodeGroup.inputs['Color'])
                                    nodeTree.links.new(oldPrevNodeGroupAlphaOutput, prevNodeGroup.inputs['Alpha'])

                            elif value == -1:
                                nextNodeGroup = getNodeGroup(getLayerByIndex(layers, index))
                                nextNodeGroupColorInput = nextNodeGroup.inputs['Color']
                                nextNodeGroupAlphaInput = nextNodeGroup.inputs['Alpha']

                                nodeTree.links.new(activeNodeGroupColorOutput, nextNodeGroupColorInput)
                                nodeTree.links.new(activeNodeGroupAlphaOutput, nextNodeGroupAlphaInput)

                                if index + 1 == len(layers):
                                    UpdateShading(paint_layers_data, context)
                                    UpdateTransparent(paint_layers_data, context)

                                else:
                                    oldNextNodeGroup = getNodeGroup(getLayerByIndex(layers, index+1))

                                    oldNextNodeGroupColorInput = oldNextNodeGroup.inputs['Color']
                                    oldNextNodeGroupAlphaInput = oldNextNodeGroup.inputs['Alpha']

                                    nodeTree.links.new(nextNodeGroup.outputs['Color'], oldNextNodeGroupColorInput)
                                    nodeTree.links.new(nextNodeGroup.outputs['Alpha'], oldNextNodeGroupAlphaInput)

                                if index - 2 >= 0:
                                    prevNodeGroup = getNodeGroup(getLayerByIndex(layers, index-2))
                                    prevNodeGroupColorOutput = prevNodeGroup.outputs['Color']
                                    prevNodeGroupAlphaOutput = prevNodeGroup.outputs['Alpha']

                                    nodeTree.links.new(prevNodeGroupColorOutput, activeNodeGroupColorInput)
                                    nodeTree.links.new(prevNodeGroupAlphaOutput, activeNodeGroupAlphaInput)
                            break


def addLayer(empty, layers, nodes, index, name, image_name, image_width, image_height, image_color):
    layer = layers.add()
    layer.index = index
    layer.name = name
    nodeGroup = nodes_addLayer(empty, layers, nodes, index, layer, image_name, image_width, image_height, image_color)
    layer.active = True
    return layer, nodeGroup


def duplicateLayer(layers, nodes, index, activeLayer, image_name, image_width, image_height, image_color):
    if layers and activeLayer:
        layer_names = [layer.name for layer in layers]
        name = activeLayer.name.split(".", 1)[0]
        suffix = 1
        while True:
            new_name = f"{name}.{str(suffix).zfill(3)}"
            if new_name not in layer_names:
                name = new_name
                break
            suffix += 1

    duplicateLayer = addLayer(False, layers, nodes, index, name, image_name, image_width, image_height, image_color)
    duplicateLayer[0].image.pixels = activeLayer.image.pixels[:]
    duplicateLayer[0].hide = activeLayer.hide
    duplicateLayer[0].opacity = activeLayer.opacity
    duplicateLayer[0].lock = activeLayer.lock
    duplicateLayer[0].blendMode = activeLayer.blendMode


def getCollectionIndex(layers, index):
    if layers:
        for i in range(0, len(layers)):
            layer = layers[i]
            if layer.index == index:
                return i
    return -1


def getLayerByIndex(layers, index):
    if layers:
        collIndex = getCollectionIndex(layers, index)
        if collIndex != -1:
            return layers[collIndex]
    return None


def getNodeGroup(layer):
    if layer:
        nodes = bpy.context.active_object.active_material.node_tree.nodes
        nodeTree = layer.nodeGroupTree
        for node in nodes:
            try:
                if node.node_tree == nodeTree:
                    return node
            except Exception:
                continue
    return None


def nodes_addLayer(empty, layers, nodes, index, layer, image_name, image_width, image_height, image_color):

    name = "Layer_" + str(datetime.datetime.now())
    group_node = nodes.new("ShaderNodeGroup")
    group_node.name = name
    group_node.node_tree = bpy.data.node_groups.new(name, "ShaderNodeTree")

    layer.nodeGroupTree = group_node.node_tree

    G_nodeTree = group_node.node_tree
    G_nodes = G_nodeTree.nodes

    input_node = G_nodes.new("NodeGroupInput")
    input_node.location = (-200, 0)

    output_node = G_nodes.new("NodeGroupOutput")
    output_node.location = (600, 0)

    G_nodeTree.inputs.new('NodeSocketColor', "Color")
    G_nodeTree.inputs.new('NodeSocketColor', "Alpha")

    G_nodeTree.outputs.new('NodeSocketColor', "Color")
    G_nodeTree.outputs.new('NodeSocketColor', "Alpha")

    imageNode = G_nodes.new('ShaderNodeTexImage')
    imageNode.name = "IMAGE_" + name

    if not empty:
        image = bpy.data.images.new(name=image_name, width=image_width, height=image_height, alpha=True)
        image.generated_color = image_color
        image.pack()
        imageNode.image = image

    if not empty:
        layer.image = image

    alphaMixNode = G_nodes.new('ShaderNodeMix')
    alphaMixNode.data_type = 'RGBA'
    alphaMixNode.inputs[0].default_value = 1
    alphaMixNode.clamp_result = True
    alphaMixNode.blend_type = 'ADD'
    alphaMixNode.name = "ALPHA_MIX_" + name

    alphaMultiply = G_nodes.new('ShaderNodeMath')
    alphaMultiply.name = "OPACITY_" + name
    alphaMultiply.operation = 'MULTIPLY'
    alphaMultiply.inputs[1].default_value = 1

    mixNode = G_nodes.new('ShaderNodeMix')
    mixNode.data_type = 'RGBA'
    mixNode.name = "MIX_" + name

    G_nodeTree.links.new(imageNode.outputs[0], mixNode.inputs[7])
    G_nodeTree.links.new(imageNode.outputs[1], alphaMultiply.inputs[0])
    G_nodeTree.links.new(alphaMultiply.outputs[0], mixNode.inputs[0])
    G_nodeTree.links.new(alphaMultiply.outputs[0], alphaMixNode.inputs[7])
    G_nodeTree.links.new(input_node.outputs["Alpha"], alphaMixNode.inputs[6])
    G_nodeTree.links.new(input_node.outputs["Color"], mixNode.inputs[6])
    G_nodeTree.links.new(output_node.inputs["Alpha"], alphaMixNode.outputs[2])
    G_nodeTree.links.new(output_node.inputs["Color"], mixNode.outputs[2])

    imageNode.location = (0, 0)
    alphaMixNode.location = (250, 0)
    alphaMultiply.location = (250, -250)
    mixNode.location = (400, 0)

    x = -300
    y = 220
    offset = 0 if not layers else (len(layers) - index - 1)
    group_node.location = (x - (offset*200), y)

    return group_node


def nodes_linkLayers(material, layers, nodeTree, nodes, lastNodeGroup, newNodeGroup, nextNodeGroup):
    if material:
        if layers:
            if nextNodeGroup:
                nodeTree.links.new(newNodeGroup.outputs[0], nextNodeGroup.inputs[0])
                nodeTree.links.new(newNodeGroup.outputs[1], nextNodeGroup.inputs[1])
            else:
                for node in nodes:
                    if node.type == "BSDF_PRINCIPLED":
                        BSDFnode = node
                        if material.psd_layers_data.shading == 'PRINCIPLED_BSDF':
                            nodeTree.links.new(newNodeGroup.outputs[0], node.inputs[0])

                        elif material.psd_layers_data.shading == 'EMISSIVE':
                            nodeTree.links.new(newNodeGroup.outputs[0], node.inputs[19])

                        if material.psd_layers_data.transparent:
                            nodeTree.links.new(newNodeGroup.outputs[1], BSDFnode.inputs[21])
                        break

            if lastNodeGroup:
                nodeTree.links.new(lastNodeGroup.outputs[0], newNodeGroup.inputs[0])
                nodeTree.links.new(lastNodeGroup.outputs[1], newNodeGroup.inputs[1])


def setBlendingMode(blendingMode):
    if blendingMode == "MIX":
        return b"norm"
    elif blendingMode == "DARKEN":
        return b"dark"
    elif blendingMode == "MULTIPLY":
        return b"mul "
    elif blendingMode == "LIGHTEN":
        return b"lite"
    elif blendingMode == "SCREEN":
        return b"scrn"

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