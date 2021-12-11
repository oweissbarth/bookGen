"""
This file contains all operators to add, update, and remove book shelves
"""
import logging
import time

import bpy

from .shelf import Shelf
from .utils import (compose_grouping_name,
                    get_bookgen_collection,
                    get_shelf_parameters,
                    get_shelf_collection,
                    get_click_position_on_object,
                    get_free_shelf_id,
                    get_active_settings,
                    get_settings_by_name,
                    get_settings_for_new_grouping,
                    get_grouping_index_by_name,
                    visible_objects_and_duplis)

from .ui_gizmo import BookGenShelfGizmo
from .ui_outline import BookGenShelfOutline
from .ui_limit_line import BookGenLimitLine


class BOOKGEN_OT_SelectShelf(bpy.types.Operator):
    """
    Define where books should be generated.
    Click on a surface where the generation should start.
    Click again to set the end point
    """
    bl_idname = "bookgen.select_shelf"
    bl_label = "Select BookGen Shelf"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ("Add a shelf of books to the scene.\n\n"
                      "Click on a surface to position the start of the shelf.\n"
                      "Click again to position the end"
                      )
    log = logging.getLogger("bookGen.select_shelf")

    def __init__(self):
        self.start = None
        self.end = None
        self.end_original = None
        self.end_normal = None
        self.start_normal = None
        self.axis_constraint = "None"

        self.gizmo = None
        self.outline = None
        self.limit_line = None

    @classmethod
    def poll(cls, context):
        """ Check if we are in object mode before calling the operator

        Args:
            context (bpy.types.Context): the execution context for the operator

        Returns:
            bool: True if the operator can be executed, otherwise false.
        """
        if context.mode != 'OBJECT':
            return False

        objects = visible_objects_and_duplis(context)
        for obj in objects:
            if obj[0].type == "MESH":
                return True
        return False

    def modal(self, context, event):
        """ Handle modal events

        Args:
            context (bpy.types.Context): the execution context of the operator
            event (bpy.types.Event): the modal event

        Returns:
            Set(str): the operator return code
        """
        if context.area:
            context.area.tag_redraw()

        mouse_x, mouse_y = event.mouse_region_x, event.mouse_region_y
        if event.type == 'MOUSEMOVE':
            return self.handle_mouse_move(context, mouse_x, mouse_y)
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self.handle_confirm(context, mouse_x, mouse_y)
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.handle_cancel(context)
        if (event.type == 'X' or event.type == 'Y' or event.type == 'Z') and event.value == 'PRESS':
            return self.handle_axis_constraint(context, event.type)
        return {'RUNNING_MODAL'}

    def handle_mouse_move(self, context, mouse_x, mouse_y):
        """
        Update the gizmo for current mouse position if there is an object under the cursor.
        If there is no object under the cursor remove the gizmo.
        """
        if self.start is not None:
            self.end, normal = get_click_position_on_object(context, mouse_x, mouse_y)
            if self.end is not None:
                self.end_original = self.end.copy()
                self.end_normal = normal

                self.apply_limits(context)
                self.refresh_preview(context)

            else:
                self.gizmo.remove()
                self.outline.disable_outline()
        return {'RUNNING_MODAL'}

    def handle_confirm(self, context, mouse_x, mouse_y):
        """
        If shelf start position has not been set, get current position under cursor.
        Otherwise check if there is an object under the cursor. If that's the case collect shelf parameters,
        create the shelf and add it to the scene.
        """

        if self.start is None:
            self.start, self.start_normal = get_click_position_on_object(context,
                                                                         mouse_x, mouse_y)
            context.workspace.status_text_set(
                "Move the mouse and click on a surface again to place the end of the shelf")

            return {'RUNNING_MODAL'}

        if self.end is None:
            return {'RUNNING_MODAL'}

        shelf_id = get_free_shelf_id(context)

        settings_name = get_settings_for_new_grouping(context).name

        settings = get_settings_by_name(context, settings_name)

        parameters = get_shelf_parameters(context, shelf_id, settings)

        normal = (self.start_normal + self.end_normal) / 2
        shelf_name = compose_grouping_name(context, "shelf", shelf_id)
        shelf = Shelf(shelf_name, self.start,
                      self.end, normal, parameters)
        shelf.clean(context)
        shelf.fill()

        # set properties for later rebuild
        shelf_props = get_shelf_collection(context, shelf.name).BookGenGroupingProperties
        shelf_props.start = self.start
        shelf_props.end = self.end
        shelf_props.normal = normal
        shelf_props.id = shelf_id
        shelf_props.grouping_type = 'SHELF'
        shelf_props.settings_name = settings_name
        self.gizmo.remove()
        self.outline.disable_outline()
        self.limit_line.remove()
        shelf.to_collection(context, with_uvs=True)

        index = get_grouping_index_by_name(context, shelf.name)

        context.scene.BookGenAddonProperties.active_shelf = index
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)

        self.log.info("Added new shelf")

        return {'FINISHED'}

    def handle_cancel(self, context):
        """
        Remove all gizmos, outlines and constraints
        """
        self.gizmo.remove()
        self.outline.disable_outline()
        self.limit_line.remove()
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)

        return {'CANCELLED'}

    def handle_axis_constraint(self, context, axis):
        """
        Set the axis constraint to the given axis.
        If it is already constraint to this axis, reset the constraint.
        Update preview and constraint lines.
        """
        if self.start is None:
            return {'RUNNING_MODAL'}

        if self.axis_constraint == axis:
            self.axis_constraint = 'None'
        else:
            self.axis_constraint = axis
        self.apply_limits(context)
        self.refresh_preview(context)
        return {'RUNNING_MODAL'}

    def invoke(self, context, _event):
        """ Select shelf called from the UI

        Args:
            context (bpy.types.Context): the execution context for the operator
            _event (bpy.type.Event): the invocation event

        Returns:
            Set[str]: operator return code
        """

        settings_name = get_settings_for_new_grouping(context).name

        settings = get_settings_by_name(context, settings_name)
        props = get_shelf_parameters(context, 0, settings)
        self.outline = BookGenShelfOutline(check_depth=True)
        self.gizmo = BookGenShelfGizmo(props["book_height"], props["book_depth"], context)
        self.limit_line = BookGenLimitLine(self.axis_constraint, context)

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("CROSSHAIR")
        context.workspace.status_text_set("Click on a surface to start placing the shelf")
        return {'RUNNING_MODAL'}

    def refresh_preview(self, context):
        """
        Collect the current parameters of the shelf,
        generate the books and update the gizmo and outline accordingly.
        """
        if self.start is None or self.end is None:
            return
        normal = (self.start_normal + self.end_normal) / 2
        shelf_id = get_free_shelf_id(context)

        settings_name = get_settings_for_new_grouping(context).name

        settings = get_settings_by_name(context, settings_name)

        parameters = get_shelf_parameters(context, shelf_id, settings)

        shelf_name = compose_grouping_name(context, "shelf", shelf_id)

        shelf = Shelf(shelf_name, self.start,
                      self.end, normal, parameters)
        shelf.fill()
        self.gizmo.update(self.start, self.end, normal)

        self.outline.enable_outline(*shelf.get_geometry(), context)
        self.limit_line.update(self.start, self.axis_constraint)

    def apply_limits(self, _context):
        """
        If there is an axis constraint apply it to the end position.
        If there is none, reset the end position to the original.
        """
        if self.start is None:
            return

        if self.axis_constraint == 'None' and self.end_original is not None:
            self.end = self.end_original.copy()
            return

        self.end = self.end_original.copy()
        if self.axis_constraint == 'X':
            self.end[1] = self.start[1]
            self.end[2] = self.start[2]
        if self.axis_constraint == 'Y':
            self.end[0] = self.start[0]
            self.end[2] = self.start[2]
        if self.axis_constraint == 'Z':
            self.end[0] = self.start[0]
            self.end[1] = self.start[1]
