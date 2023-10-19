import bpy
import bpy.utils.previews

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
    bl_label = "Duplicate Layer"
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
    bl_label = "Delete Layer"
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