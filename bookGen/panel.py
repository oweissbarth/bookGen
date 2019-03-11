import bpy

class OBJECT_PT_BookGenPanel(bpy.types.Panel):
    bl_label = "Shelf Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()

    def draw(self, context):
        properties = bpy.context.collection.BookGenProperties
        layout = self.layout

        layout.prop(properties, "width", text="Width")
        layout.prop(properties, "scale", text="Scale")
        layout.prop(properties, "seed", text="Seed")

        row = layout.row(align=True)
        row.prop(properties, "spacing")
        row.prop(properties, "rndm_spacing_factor")

        layout.separator()
        layout.label(text="Axis")
        layout.prop(properties, "axis", expand=True)
        sub = layout.column()
        sub.active = properties.axis == "2"
        sub.prop(properties, "angle")

        layout.separator()

        layout.label(text="alignment")
        layout.prop(properties, "alignment", expand=True)

        layout.separator()

        leaning = layout.box()
        leaning.label(text="leaning")
        leaning.prop(properties, "lean_amount")
        leaning.prop(properties, "lean_direction")
        row = leaning.row(align=True)
        row.prop(properties, "lean_angle")
        row.prop(properties, "rndm_lean_angle_factor")

        layout.separator()

        proportions = layout.box()
        proportions.label(text="Proportions:")

        row = proportions.row(align=True)
        row.prop(properties, "book_height")
        row.prop(properties, "rndm_book_height_factor")

        row = proportions.row(align=True)
        row.prop(properties, "book_depth")
        row.prop(properties, "rndm_book_depth_factor")

        row = proportions.row(align=True)
        row.prop(properties, "book_width")
        row.prop(properties, "rndm_book_width_factor")

        layout.separator()

        details_box = layout.box()
        details_box.label(text="Details:")

        row = details_box.row(align=True)
        row.prop(properties, "textblock_offset")
        row.prop(properties, "rndm_textblock_offset_factor")

        row = details_box.row(align=True)
        row.prop(properties, "cover_thickness")
        row.prop(properties, "rndm_cover_thickness_factor")

        row = details_box.row(align=True)
        row.prop(properties, "spline_curl")
        row.prop(properties, "rndm_spline_curl_factor")

        row = details_box.row(align=True)
        row.prop(properties, "hinge_inset")
        row.prop(properties, "rndm_hinge_inset_factor")

        row = details_box.row(align=True)
        row.prop(properties, "hinge_width")
        row.prop(properties, "rndm_hinge_width_factor")

        layout.separator()

        layout.prop(properties, "subsurf")
        layout.prop(properties, "smooth")
        layout.prop(properties, "unwrap")


class OBJECT_PT_BookGen_MainPanel(bpy.types.Panel):
    bl_label = "Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BookGen"
    bl_options = set()

    def draw(self, context):
        properties = bpy.context.collection.BookGenProperties
        layout = self.layout
        layout.prop(properties, "auto_rebuild")
        layout.operator("object.book_gen", text="rebuild")
        