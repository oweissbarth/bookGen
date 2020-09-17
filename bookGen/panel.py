"""
This file contains the UI panels.
"""

import bpy

from .utils import get_bookgen_collection, get_shelf_collection_by_index, get_active_settings


class BOOKGEN_PT_ShelfSettings(bpy.types.Panel):
    """
    Draws the main shelf settings panel.
    """
    bl_label = "Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()

    def subdraw(self, context):
        """
        Can be overwritten in subclass
        """
    @classmethod
    def poll(self, context):
        properties = get_active_settings(context)
        return bool(properties)

    def draw(self, context):
        """ Draws the shelf settings panel

        Args:
            context (bpy.types.Context): the execution context
        """
        self.subdraw(context)
        properties = get_active_settings(context)
        if not properties:
            return

        layout = self.layout
        layout.use_property_split = True
        layout.use_property_decorate = False

        layout.prop(properties, "scale", text="Scale")
        layout.prop(properties, "seed", text="Seed")

        layout.prop(properties, "alignment", text="Alignment")

        layout.prop(properties, "cover_material", text="Cover Material")
        layout.prop(properties, "page_material", text="Page Material")


class BOOKGEN_PT_LeaningPanel(bpy.types.Panel):
    """
    Draws the leaning settings panel.
    """
    bl_label = "Leaning"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()
    bl_parent_id = "BOOKGEN_PT_Panel"

    @ classmethod
    def poll(self, context):
        properties = get_active_settings(context)
        return bool(properties)

    def draw(self, context):
        """ Draws the leaning settings panel.

        Args:
            context (bpy.types.Context): the execution context
        """
        properties = get_active_settings(context)
        if not properties:
            return
        layout = self.layout
        layout.use_property_split = True

        layout.prop(properties, "lean_amount", text="Lean Amount")
        layout.prop(properties, "lean_direction", text="Lean Direction")
        col = layout.column(align=True)
        col.prop(properties, "lean_angle", text="Lean Angle")
        col.prop(properties, "rndm_lean_angle_factor", text="Random")


class BOOKGEN_PT_ProportionsPanel(bpy.types.Panel):
    """
    Draws book proportions panel.
    """
    bl_label = "Proportions"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()
    bl_parent_id = "BOOKGEN_PT_Panel"

    @classmethod
    def poll(self, context):
        properties = get_active_settings(context)
        return bool(properties)

    def draw(self, context):
        """ Draws the proportion settings panel

        Args:
            context (bpy.types.Context): the execution context
        """
        properties = get_active_settings(context)
        if not properties:
            return

        layout = self.layout
        layout.use_property_split = True

        col = layout.column(align=True)
        col.prop(properties, "book_height", text="Book Height")
        col.prop(properties, "rndm_book_height_factor", text="Random")

        col = layout.column(align=True)
        col.prop(properties, "book_depth", text="Book Depth")
        col.prop(properties, "rndm_book_depth_factor", text="Random")

        col = layout.column(align=True)
        col.prop(properties, "book_width", text="Book Width")
        col.prop(properties, "rndm_book_width_factor", text="Random")


class BOOKGEN_PT_DetailsPanel(bpy.types.Panel):
    """
    Draws the book details panel
    """
    bl_label = "Details"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = {'DEFAULT_CLOSED'}
    bl_parent_id = "BOOKGEN_PT_Panel"

    @classmethod
    def poll(self, context):
        properties = get_active_settings(context)
        return bool(properties)

    def draw(self, context):
        """ Draws the detail settings panel

        Args:
            context (bpy.types.Context): the execution context
        """

        properties = get_active_settings(context)
        if not properties:
            return
        layout = self.layout
        layout.use_property_split = True

        col = layout.column(align=True)
        col.prop(properties, "textblock_offset", text="Textblock Offset")
        col.prop(properties, "rndm_textblock_offset_factor", text="Random")

        col = layout.column(align=True)
        col.prop(properties, "cover_thickness", text="Cover Thickness")
        col.prop(properties, "rndm_cover_thickness_factor", text="Random")

        col = layout.column(align=True)
        col.prop(properties, "spine_curl", text="Spine Curl")
        col.prop(properties, "rndm_spine_curl_factor", text="Random")

        col = layout.column(align=True)
        col.prop(properties, "hinge_inset", text="Hinge Inset")
        col.prop(properties, "rndm_hinge_inset_factor", text="Random")

        col = layout.column(align=True)
        col.prop(properties, "hinge_width", text="Hinge Width")
        col.prop(properties, "rndm_hinge_width_factor", text="Random")

        layout.separator()

        layout.prop(properties, "subsurf")


class BOOKGEN_PT_Panel(BOOKGEN_PT_ShelfSettings):
    """
    Generic BookGen panel
    """
    bl_label = "Properties"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "BookGen"
    bl_options = set()


class BOOKGEN_PT_MainPanel(bpy.types.Panel):
    """
    Draws the main bookgen panel
    """
    bl_label = "Main"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BookGen"
    bl_options = set()

    def draw(self, context):
        """ Draws the main panel

        Args:
            context (bpy.types.Context): the execution context
        """
        properties = get_bookgen_collection().BookGenProperties
        layout = self.layout
        layout.operator("bookgen.select_shelf", text="Add shelf")
        # layout.operator("object.book_gen_select_shelf_faces", text="Add shelf face")
        layout.operator("object.book_gen_select_stack", text="Add stack")
        layout.operator("bookgen.rebuild", text="rebuild")
        layout.prop(properties, "auto_rebuild")
        layout.label(text="Shelves")
        row = layout.row()
        row.template_list("BOOKGEN_UL_Shelves", "", get_bookgen_collection(), "children",
                          get_bookgen_collection().BookGenProperties, "active_shelf")
        col = row.column(align=True)
        col.operator("bookgen.remove_shelf", icon="X", text="")
        col.prop(properties, "outline_active", toggle=True, icon="SHADING_BBOX", icon_only=True)

        active_shelf = self.get_active_shelf()
        layout = self.layout
        row = layout.row(align=True)
        choose_props = row.operator('bookgen.set_settings', text="", icon='PRESET')
        if active_shelf and active_shelf.BookGenShelfProperties.settings_name:
            settings = get_active_settings(context)
            row.prop(settings, "name", text="", expand=True)
        choose_props = row.operator('bookgen.create_settings', text="", icon='ADD')
        choose_props = row.operator('bookgen.remove_settings', text="", icon='X')

    def get_active_shelf(self):
        """ Get the collection of the active grouping

        TODO move somewhere were it can be reused

        Returns:
            bpy.types.Collection: the collection of the active grouping
        """
        shelf_id = get_bookgen_collection().BookGenProperties.active_shelf
        return get_shelf_collection_by_index(shelf_id)
