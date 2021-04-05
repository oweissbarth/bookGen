"""
Contains the operators for manipulating stacks of books.
"""
import logging

import bpy
from mathutils import Vector
import bpy_extras
import mathutils


from .stack import Stack
from .ui_stack_gizmo import BookGenStackGizmo
from .utils import (
    compose_grouping_name,
    project_to_screen,
    get_click_position_on_object,
    get_free_stack_id,
    get_stack_parameters,
    get_shelf_collection,
    get_settings_for_new_grouping,
    get_settings_by_name,
    get_click_on_plane,
    get_grouping_index_by_name,
    visible_objects_and_duplis)
from .ui_outline import BookGenShelfOutline


class BOOKGEN_OT_SelectStack(bpy.types.Operator):
    """
    Define where books should be generated.
    Click on a surface where the generation should start.
    Click again to set the end point
    """
    bl_idname = "bookgen.select_stack"
    bl_label = "Select BookGen Stack"
    bl_options = {'REGISTER', 'UNDO'}
    bl_description = ("Add a stack of books to the scene.\n\n"
                      "Click on a surface to position the stack.\n"
                      "Move the cursor and click again to choose the direction the stack is facing.\n"
                      "Move the cursor upwards and click to select the height of the stack"
                      )
    log = logging.getLogger("bookGen.select_stack")

    def __init__(self):
        self.origin = None
        self.origin_normal = None
        self.forward = None
        self.height = None

        self.origin_normal_2d = None
        self.origin_2d = None
        self.gizmo = None

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
        """Handle modal events

        Args:
            context (bpy.types.Context): the execution context of the operator
            event (bpy.types.Event): the modal event

        Returns:
            Set(str): the operator return code
        """
        if context.area:
            context.area.tag_redraw()

        context.window.cursor_modal_set("CROSSHAIR")

        mouse_x, mouse_y = event.mouse_region_x, event.mouse_region_y
        if event.type == 'MOUSEMOVE':
            return self.handle_mouse_move(context, mouse_x, mouse_y)
        if event.type in {'MIDDLEMOUSE', 'WHEELUPMOUSE', 'WHEELDOWNMOUSE'}:
            return {'PASS_THROUGH'}
        if event.type == 'LEFTMOUSE' and event.value == 'RELEASE':
            return self.handle_confirm(context, mouse_x, mouse_y)
        if event.type in {'RIGHTMOUSE', 'ESC'}:
            return self.handle_cancel(context)

        return {'RUNNING_MODAL'}

    def handle_mouse_move(self, context, mouse_x, mouse_y):
        """
        Update the gizmo for current mouse position if necessary.
        Otherwise remove the gizmo.
        """

        if self.forward is not None:
            self.log.info("forward is not none")
            relative_mouse_pos = Vector((mouse_x, mouse_y)) - self.origin_2d
            t = relative_mouse_pos.dot(self.origin_normal_2d)
            projected = self.origin_2d + t * self.origin_normal_2d

            p_x = projected[0]
            p_y = projected[1]

            relative_mouse_pos = Vector((mouse_x, mouse_y)) - self.origin_2d
            t = relative_mouse_pos.dot(self.origin_normal_2d)
            projected = self.origin_2d + t * self.origin_normal_2d

            p_x = projected[0]
            p_y = projected[1]

            region = context.region
            region_data = context.space_data.region_3d

            view_vector = bpy_extras.view3d_utils.region_2d_to_vector_3d(region, region_data, (p_x, p_y))
            ray_origin = bpy_extras.view3d_utils.region_2d_to_origin_3d(region, region_data, (p_x, p_y))

            ray_target = ray_origin + view_vector

            points = mathutils.geometry.intersect_line_line(
                self.origin, self.origin + self.origin_normal, ray_origin, ray_target)

            self.height = (points[0] - self.origin).length

        self.refresh_preview(context, mouse_x, mouse_y)

        return {'RUNNING_MODAL'}

    def handle_confirm(self, context, mouse_x, mouse_y):
        """ If it is the first click and there is and object under the cursor set the stack origin.
        If it is the second click and there is and object under the cursor set the stack forward.
        If it is the third click set the stack height.

        Args:
            context (bpy.types.Context): the execution context
            mouse_x (float): x position of the cursor in pixels
            mouse_y (float): y position of the cursor in pixels

        Returns:
            Set[str]: the operator return code
        """
        if self.origin is None:
            self.origin, self.origin_normal = get_click_position_on_object(context,
                                                                           mouse_x, mouse_y)
            if self.origin is None:
                return {'RUNNING_MODAL'}

            self.origin_2d = project_to_screen(context, self.origin)
            normal_offset_2d = project_to_screen(context, self.origin + self.origin_normal)
            self.origin_normal_2d = (normal_offset_2d - self.origin_2d).normalized()
            context.workspace.status_text_set("Move the mouse and click to select the forward direction of the stack.")

            return {'RUNNING_MODAL'}
        if self.forward is None:
            front = get_click_on_plane(context, mouse_x, mouse_y, self.origin, self.origin_normal)
            original_direction = front - self.origin
            distance = original_direction.dot(self.origin_normal)
            projected_front = front - distance * self.origin_normal
            self.forward = (projected_front - self.origin).normalized()
            context.workspace.status_text_set("Move the mouse upwards and click to select the height of the stack.")

            return {'RUNNING_MODAL'}

        stack_id = get_free_stack_id(context)
        settings_name = get_settings_for_new_grouping(context).name
        settings = get_settings_by_name(context, settings_name)

        parameters = get_stack_parameters(context, stack_id, settings)

        stack_name = compose_grouping_name(context, "stack", stack_id)
        stack = Stack(stack_name, self.origin,
                      self.forward, self.origin_normal, self.height, parameters)
        stack.clean(context)
        stack.fill()

        # set properties for later rebuild
        stack_props = get_shelf_collection(context,
                                           stack.name).BookGenGroupingProperties
        stack_props.origin = self.origin
        stack_props.forward = self.forward
        stack_props.normal = self.origin_normal
        stack_props.height = self.height
        stack_props.id = stack_id
        stack_props.grouping_type = 'STACK'
        stack_props.settings_name = settings_name

        self.gizmo.remove()
        self.outline.disable_outline()
        stack.to_collection(context, with_uvs=True)

        index = get_grouping_index_by_name(context, stack.name)

        context.scene.BookGenAddonProperties.active_shelf = index

        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)

        return {'FINISHED'}

    def handle_cancel(self, context):
        """
        Remove all gizmos and outlines
        """
        self.gizmo.remove()
        self.outline.disable_outline()
        context.window.cursor_modal_restore()
        context.workspace.status_text_set(None)

        return {'CANCELLED'}

    def invoke(self, context, _event):
        """ Select stack called from the UI

        Args:
            _context (bpy.types.Context): the execution context for the operator
            _event (bpy.type.Event): the invocation event

        Returns:
            Set[str]: operator return code
        """

        self.outline = BookGenShelfOutline(check_depth=True)
        self.gizmo = BookGenStackGizmo(0, 0, context)

        context.window_manager.modal_handler_add(self)
        context.window.cursor_modal_set("CROSSHAIR")
        context.workspace.status_text_set("Click on a surface to start placing the stack")
        return {'RUNNING_MODAL'}

    def refresh_preview(self, context, mouse_x, mouse_y):
        """
        Collect the current parameters of the stack,
        generate the books and update the gizmo and outline accordingly.

        Args:
            context (bpy.types.Context): the execution context
        """
        self.log.info("Refreshing preview")

        if self.origin is None:
            origin, origin_normal = get_click_position_on_object(context,
                                                                 mouse_x, mouse_y)
            if origin is None:
                self.gizmo.remove()
            else:
                self.gizmo.update(origin, self.forward, origin_normal, None)
            return

        if self.forward is None:
            front = get_click_on_plane(context, mouse_x, mouse_y, self.origin, self.origin_normal)
            if front is None:
                return
            original_direction = front - self.origin
            distance = original_direction.dot(self.origin_normal)
            projected_front = front - distance * self.origin_normal
            forward = (projected_front - self.origin).normalized()
            self.gizmo.update(self.origin, forward, self.origin_normal, None)
            return

        self.gizmo.remove()
        stack_id = get_free_stack_id(context)
        settings_name = get_settings_for_new_grouping(context).name
        settings = get_settings_by_name(context, settings_name)

        parameters = get_stack_parameters(context, stack_id, settings)
        stack_name = compose_grouping_name(context, "stack", stack_id)
        stack = Stack(stack_name, self.origin,
                      self.forward, self.origin_normal, self.height, parameters)
        stack.fill()
        self.outline.enable_outline(*stack.get_geometry(), context)

        self.gizmo.update(self.origin, self.forward, self.origin_normal, self.height)
