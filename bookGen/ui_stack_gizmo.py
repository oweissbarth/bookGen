"""
Contains a class to draw the stack gizmo
"""

import logging
from math import sin, cos, pi

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Matrix


class BookGenStackGizmo():
    """
    Draws the stack gizmo.
    """

    log = logging.getLogger("bookGen.stack_gizmo")

    def __init__(self, height, depth, context):
        self.height = height
        self.depth = depth
        self.context = context

        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.origin_batch = None
        self.forward_batch = None
        self.up_batch = None

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (self.context,), 'WINDOW', 'POST_VIEW')

        primary_color_ref = context.preferences.themes[0].user_interface.gizmo_primary
        self.origin_color = [primary_color_ref[0], primary_color_ref[1], primary_color_ref[2], 1]
        secondary_color_ref = context.preferences.themes[0].user_interface.gizmo_secondary
        self.arrow_color = [secondary_color_ref[0], secondary_color_ref[1], secondary_color_ref[2], 1]

    def draw(self, _context):
        """ Draws stack gizmo based on the current configuration

        Args:
            context (bpy.types.Context): the execution context
        """
        if self.origin_batch is None:
            return

        self.log.debug("drawing stack gizmo")

        self.shader.bind()
        gpu.state.blend_set("ALPHA")
        self.shader.uniform_float("color", self.origin_color)
        self.origin_batch.draw(self.shader)

        if self.forward_batch is not None:
            self.shader.uniform_float("color", self.arrow_color)
            self.forward_batch.draw(self.shader)

        if self.up_batch is not None:
            self.shader.uniform_float("color", self.arrow_color)
            self.up_batch.draw(self.shader)

        gpu.state.blend_set("NONE")

    def update(self, origin, forward, up, height):
        """ Updates the position and orientation of the stack gizmo

        Args:
            start (Vector): the start position of the shelf gizmo
            end (Vector): the end position of the shelf gizmo
            nrm (Vector): the normal of the shelf gizmo
        """
        if origin is None:
            return
        self.log.debug("updating stack gizmo")

        # direction.normalize()
        #rotation_matrix = Matrix([direction, direction.cross(nrm), nrm]).transposed()

        RESOLUTION = 32
        INNER_RADIUS = 0.05
        OUTER_RADIUS = 0.07
        origin_verts = []
        step_size = 2 * pi / RESOLUTION
        for i in range(RESOLUTION):
            cur_angle = step_size * i
            next_angle = step_size * (i + 1) % RESOLUTION
            c_v_inner = Vector((cos(cur_angle) * INNER_RADIUS, sin(cur_angle) * INNER_RADIUS, 0))
            c_v_outer = Vector((cos(cur_angle) * OUTER_RADIUS, sin(cur_angle) * OUTER_RADIUS, 0))

            n_v_inner = Vector((cos(next_angle) * INNER_RADIUS, sin(next_angle) * INNER_RADIUS, 0))
            n_v_outer = Vector((cos(next_angle) * OUTER_RADIUS, sin(next_angle) * OUTER_RADIUS, 0))

            origin_verts.append(c_v_outer + origin)
            origin_verts.append(c_v_inner + origin)
            origin_verts.append(n_v_outer + origin)

            origin_verts.append(c_v_inner + origin)
            origin_verts.append(n_v_inner + origin)
            origin_verts.append(n_v_outer + origin)

        self.origin_batch = batch_for_shader(self.shader, 'TRIS', {"pos": origin_verts})

        if forward is not None:

            ARROW_LENGTH = 0.08
            ARROW_WIDTH = 0.007
            ARROW_HEAD_WIDTH = 0.015
            ARROW_HEAD_LENGTH = 0.02
            forward_vertices = []

            rotation_matrix = Matrix([forward.cross(up), forward, up]).transposed()

            forward_vertices.append(rotation_matrix @ Vector((-ARROW_WIDTH / 2, 0, 0)) + origin)
            forward_vertices.append(rotation_matrix @ Vector((ARROW_WIDTH / 2, ARROW_LENGTH, 0)) + origin)
            forward_vertices.append(rotation_matrix @ Vector((-ARROW_WIDTH / 2, ARROW_LENGTH, 0)) + origin)

            forward_vertices.append(rotation_matrix @ Vector((-ARROW_WIDTH / 2, 0, 0)) + origin)
            forward_vertices.append(rotation_matrix @ Vector((ARROW_WIDTH / 2, 0, 0)) + origin)
            forward_vertices.append(rotation_matrix @ Vector((ARROW_WIDTH / 2, ARROW_LENGTH, 0)) + origin)

            forward_vertices.append(rotation_matrix @ Vector((-ARROW_HEAD_WIDTH / 2, ARROW_LENGTH, 0)) + origin)
            forward_vertices.append(rotation_matrix @ Vector((ARROW_HEAD_WIDTH / 2, ARROW_LENGTH, 0)) + origin)
            forward_vertices.append(rotation_matrix @ Vector((0, ARROW_LENGTH + ARROW_HEAD_LENGTH, 0)) + origin)
            self.forward_batch = batch_for_shader(self.shader, 'TRIS', {"pos": forward_vertices})

        if height is not None:
            RESOLUTION = 32
            RADIUS = 0.05
            height_verts = []
            step_size = 2 * pi / RESOLUTION
            for i in range(RESOLUTION):
                cur_angle = step_size * i
                next_angle = step_size * (i + 1) % RESOLUTION
                center = Vector((0, 0, 0))
                c_v = Vector((cos(cur_angle) * RADIUS, sin(cur_angle) * RADIUS, 0))
                n_v = Vector((cos(next_angle) * RADIUS, sin(next_angle) * RADIUS, 0))

                height_verts.append(center + origin + up * height)
                height_verts.append(n_v + origin + up * height)
                height_verts.append(c_v + origin + up * height)

            self.up_batch = batch_for_shader(self.shader, 'TRIS', {"pos": height_verts})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (self.context,), 'WINDOW', 'POST_VIEW')

    def remove(self):
        """
        Disables the stack gizmo by removing the draw handler
        """
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None
