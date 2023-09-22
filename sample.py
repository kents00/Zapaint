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