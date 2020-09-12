import logging
import time

import bpy

from .shelf import Shelf
from .utils import (obj_ray_cast,
                    get_bookgen_collection,
                    get_shelf_parameters,
                    get_shelf_collection,
                    get_click_position_on_object,
                    get_free_shelf_id)

from .ui_gizmo import BookGenShelfGizmo
from .ui_outline import BookGenShelfOutline
from .ui_limit_line import BookGenLimitLine


class OBJECT_OT_BookGenRebuild(bpy.types.Operator):
    """Regenerate all books"""
    bl_idname = "object.book_gen_rebuild"
    bl_label = "BookGen"
    bl_options = {'REGISTER', 'UNDO'}

    """def hinge_inset_guard(self, context):
        if(self.hinge_inset > self.cover_thickness):
            self.hinge_inset = self.cover_thickness - self.cover_thickness / 8"""

    log = logging.getLogger("bookGen.operator")

    def check(self, _context):
        self.run()

    def invoke(self, _context, _event):
        self.run()
        return {'FINISHED'}

    def execute(self, _context):
        self.run()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def run(self):

        time_start = time.time()
        parameters = get_shelf_parameters()

        for shelf_collection in get_bookgen_collection().children:
            shelf_props = shelf_collection.BookGenShelfProperties

            parameters["seed"] += shelf_props.id

            shelf = Shelf(shelf_collection.name, shelf_props.start,
                          shelf_props.end, shelf_props.normal, parameters)
            shelf.clean()
            shelf.fill()

            parameters["seed"] -= shelf_props.id

            shelf.to_collection()

        self.log.info("Finished populating shelf in %.4f secs", (time.time() - time_start))


class OBJECT_OT_BookGenRemoveShelf(bpy.types.Operator):
    """Delete the selected shelf"""
    bl_idname = "object.book_gen_remove_shelf"
    bl_label = "BookGen"
    bl_options = {'REGISTER', 'UNDO'}

    log = logging.getLogger("bookGen.operator")

    def check(self, _context):
        self.run()

    def invoke(self, _context, _event):
        self.run()
        return {'FINISHED'}

    def execute(self, _context):
        self.run()
        return {'FINISHED'}

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def run(self):
        parent = get_bookgen_collection()
        active = parent.BookGenProperties.active_shelf
        if active < 0 or active >= len(parent.children):
            return
        collection = parent.children[active]

        for obj in collection.objects:
            collection.objects.unlink(obj)
            bpy.data.meshes.remove(obj.data)
        parent.children.unlink(collection)
        bpy.data.collections.remove(collection)

        parent.BookGenProperties.active_shelf -= 1

        if active != len(parent.children):
            parent.BookGenProperties.active_shelf += 1


class BookGen_SelectShelf(bpy.types.Operator):
    """Define where books should be generated.\nClick on a surface where the generation should start. Click again to set the end point"""
    bl_idname = "object.book_gen_select_shelf"
    bl_label = "Select BookGen Shelf"
    bl_options = {'REGISTER', 'UNDO'}
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

    def modal(self, context, event):
        if context.area:
            context.area.tag_redraw()

        x, y = event.mouse_region_x, event.mouse_region_y
        if event.type == 'MOUSEMOVE':
            return self.handle_mouse_move(context, x, y)
        elif event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            # allow navigation
            return {'PASS_THROUGH'}
        elif event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self.handle_confirm(context, x, y)
        elif event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.handle_cancel(context)
        elif (event.type == 'X' or event.type == 'Y' or event.type == 'Z') and event.value == 'PRESS':
            return self.handle_axis_constraint(context, event.type)
        return {'RUNNING_MODAL'}

    def handle_mouse_move(self, context, mouse_x, mouse_y):
        """
        Update the gizmo for current mouse position if there is an object under the cursor.
        If there is no object under the cursor remove the gizmo.
        """
        if self.start is not None:
            self.end, normal = get_click_position_on_object(mouse_x, mouse_y)
            if self.end is not None:
                self.end_original = self.end.copy()
                self.end_normal = normal

                self.apply_limits(context)
                self.refresh_preview(context)

            else:
                self.gizmo.remove()
                self.outline.disable_outline()
        return {'RUNNING_MODAL'}

    def handle_confirm(self, _context, mouse_x, mouse_y):
        """
        If shelf start position has not been set, get current position under cursor.
        Otherwise check if there is an object under the cursor. If that's the case collect shelf parameters,
        create the shelf and add it to the scene.
        """

        if self.start is None:
            self.start, self.start_normal = get_click_position_on_object(
                mouse_x, mouse_y)
            return {'RUNNING_MODAL'}

        if self.end is None:
            return {'RUNNING_MODAL'}

        shelf_id = get_free_shelf_id()
        parameters = get_shelf_parameters()
        parameters["seed"] += shelf_id
        normal = (self.start_normal + self.end_normal) / 2
        shelf = Shelf("shelf_" + str(shelf_id), self.start,
                      self.end, normal, parameters)
        shelf.clean()
        shelf.fill()

        # set properties for later rebuild
        shelf_props = get_shelf_collection(
            shelf.name).BookGenShelfProperties
        shelf_props.start = self.start
        shelf_props.end = self.end
        shelf_props.normal = normal
        shelf_props.id = shelf_id
        self.gizmo.remove()
        self.outline.disable_outline()
        self.limit_line.remove()
        shelf.to_collection()
        return {'FINISHED'}

    def handle_cancel(self, _context):
        """
        Remove all gizmos, outlines and constraints
        """
        self.gizmo.remove()
        self.outline.disable_outline()
        self.limit_line.remove()
        return {'CANCELLED'}

    def handle_axis_constraint(self, context, axis):
        if self.axis_constraint == axis:
            self.axis_constraint = 'None'
        else:
            self.axis_constraint = axis
        self.apply_limits(context)
        self.refresh_preview(context)
        return {'RUNNING_MODAL'}

    def invoke(self, context, _event):

        args = (self, context)

        props = get_shelf_parameters()
        self.gizmo = BookGenShelfGizmo(
            self.start, self.end, None, props["book_height"], props["book_depth"], args)
        self.outline = BookGenShelfOutline()
        self.limit_line = BookGenLimitLine(self.start, self.axis_constraint, args)

        context.window_manager.modal_handler_add(self)
        return {'RUNNING_MODAL'}

    def refresh_preview(self, context):
        if self.start is None or self.end is None:
            return
        normal = (self.start_normal + self.end_normal) / 2
        shelf_id = get_free_shelf_id()
        parameters = get_shelf_parameters(shelf_id)
        shelf = Shelf("shelf_" + str(shelf_id), self.start,
                      self.end, normal, parameters)
        shelf.fill()
        self.outline.enable_outline(*shelf.get_geometry(), context)
        self.gizmo.update(self.start, self.end, normal)
        self.limit_line.update(self.start, self.axis_constraint)

    def apply_limits(self, _context):
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
