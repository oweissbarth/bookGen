import bpy

from .utils import get_bookgen_collection


class OBJECT_PT_BookGen_LeaningPanel(bpy.types.Panel):
    bl_label = "Leaning"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()
    bl_parent_id = "OBJECT_PT_BookGenPanel"

    def draw(self, context):
        properties = get_bookgen_collection().BookGenProperties
        layout = self.layout
        layout.use_property_split = True


        layout.prop(properties, "lean_amount")
        layout.prop(properties, "lean_direction")
        col = layout.column(align=True)
        col.prop(properties, "lean_angle")
        col.prop(properties, "rndm_lean_angle_factor")

class OBJECT_PT_BookGen_ProportionsPanel(bpy.types.Panel):
    bl_label = "Proportions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()
    bl_parent_id = "OBJECT_PT_BookGenPanel"

    def draw(self, context):
        properties = get_bookgen_collection().BookGenProperties
        layout = self.layout
        layout.use_property_split = True

        col = layout.column(align=True)
        col.prop(properties, "book_height")
        col.prop(properties, "rndm_book_height_factor")

        col = layout.column(align=True)
        col.prop(properties, "book_depth")
        col.prop(properties, "rndm_book_depth_factor")

        col = layout.column(align=True)
        col.prop(properties, "book_width")
        col.prop(properties, "rndm_book_width_factor")

class OBJECT_PT_BookGen_DetailsPanel(bpy.types.Panel):
    bl_label = "Details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()
    bl_parent_id = "OBJECT_PT_BookGenPanel"

    def draw(self, context):
        properties = get_bookgen_collection().BookGenProperties
        layout = self.layout
        layout.use_property_split = True


        col = layout.column(align=True)
        col.prop(properties, "textblock_offset")
        col.prop(properties, "rndm_textblock_offset_factor")

        col = layout.column(align=True)
        col.prop(properties, "cover_thickness")
        col.prop(properties, "rndm_cover_thickness_factor")

        col = layout.column(align=True)
        col.prop(properties, "spine_curl")
        col.prop(properties, "rndm_spine_curl_factor")

        col = layout.column(align=True)
        col.prop(properties, "hinge_inset")
        col.prop(properties, "rndm_hinge_inset_factor")

        col = layout.column(align=True)
        col.prop(properties, "hinge_width")
        col.prop(properties, "rndm_hinge_width_factor")

        layout.separator()

        layout.prop(properties, "subsurf")


class OBJECT_PT_BookGenPanel(bpy.types.Panel):
    bl_label = "Shelf Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()

    def draw(self, context):
        properties = get_bookgen_collection().BookGenProperties
        layout = self.layout
        layout.use_property_split = True

        layout.prop(properties, "scale", text="scale")
        layout.prop(properties, "seed", text="Seed")

        layout.prop(properties, "alignment")

 

class OBJECT_PT_BookGen_MainPanel(bpy.types.Panel):
    bl_label = "Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BookGen"
    bl_options = set()

    def draw(self, context):
        properties = get_bookgen_collection().BookGenProperties
        layout = self.layout
        layout.prop(properties, "auto_rebuild")
        layout.operator("object.book_gen_rebuild", text="rebuild")
        layout.operator("object.book_gen_select_shelf", text="Add shelf")
        layout.label(text="Shelves")
        row = layout.row()
        row.template_list("BOOKGEN_UL_Shelves", "", get_bookgen_collection(), "children", bpy.context.collection.BookGenProperties, "active_shelf")
        col = row.column(align=True)
        props = col.operator("object.book_gen_remove_shelf", icon="REMOVE", text="")