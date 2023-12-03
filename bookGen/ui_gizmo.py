"""
Contains a class to draw the shelf gizmo
"""

import logging

import bpy
import gpu
from gpu_extras.batch import batch_for_shader
from mathutils import Vector, Matrix

from .data.gizmo_verts import bookstand_verts_start, bookstand_verts_end
from .utils import vector_scale, bookGen_directory


class BookGenShelfGizmo:
    """
    Draws the shelf gizmo.
    """

    log = logging.getLogger("bookGen.gizmo")

    def __init__(self, height, depth, context):
        self.height = height
        self.depth = depth
        self.context = context

        with open(bookGen_directory + "/shaders/dotted_line.vert") as fp:
            vertex_shader = fp.read()

        with open(bookGen_directory + "/shaders/dotted_line.frag") as fp:
            fragment_shader = fp.read()

        self.bookstand_shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.line_shader = gpu.types.GPUShader(vertex_shader, fragment_shader)
        self.bookstand_batch = None
        self.line_batch = None

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (self.context,), "WINDOW", "POST_VIEW")

        color_ref = context.preferences.themes[0].user_interface.gizmo_primary
        # self.bookstand_color = [color_ref[0], color_ref[1], color_ref[2], 0.6]
        self.bookstand_color = [color_ref[0], color_ref[1], color_ref[2], 1.0]

    def draw(self, context):
        """Draws shelf gizmo based on the current configuration

        Args:
            context (bpy.types.Context): the execution context
        """
        if self.bookstand_batch is None or self.line_batch is None:
            return

        self.bookstand_shader.bind()

        gpu.state.depth_test_set("LESS_EQUAL")

        self.bookstand_shader.uniform_float("color", self.bookstand_color)
        self.bookstand_batch.draw(self.bookstand_shader)

        gpu.state.line_width_set(3)
        matrix = context.region_data.perspective_matrix
        self.line_shader.bind()
        self.line_shader.uniform_float("u_ViewProjectionMatrix", matrix)
        self.line_shader.uniform_float("u_Scale", 100)
        self.line_batch.draw(self.line_shader)
        gpu.state.depth_test_set("NONE")

    def update(self, start, end, nrm):
        """Updates the position and orientation of the shelf gizmo

        Args:
            start (Vector): the start position of the shelf gizmo
            end (Vector): the end position of the shelf gizmo
            nrm (Vector): the normal of the shelf gizmo
        """
        direction = end - start
        width = direction.length
        direction.normalize()
        rotation_matrix = Matrix([direction, direction.cross(nrm), nrm]).transposed()
        verts_start = []
        for vertex in bookstand_verts_start:
            scaled = vector_scale(vertex, [1, self.depth, self.height])
            rotated = rotation_matrix @ scaled
            verts_start.append(rotated + start)
        verts_end = []
        for vertex in bookstand_verts_end:
            scaled = vector_scale(vertex, [1, self.depth, self.height])
            offset = scaled + Vector((width, 0, 0))
            rotated = rotation_matrix @ offset
            verts_end.append(rotated + start)

        bookstand_verts = verts_start + verts_end

        self.bookstand_batch = batch_for_shader(self.bookstand_shader, "TRIS", {"pos": bookstand_verts})

        offset = nrm * 0.0001 + start

        lines = [
            rotation_matrix @ Vector((0, self.depth / 2, 0)) + offset,
            rotation_matrix @ Vector((width, self.depth / 2, 0)) + offset,
            rotation_matrix @ Vector((0, -self.depth / 2, 0)) + offset,
            rotation_matrix @ Vector((width, -self.depth / 2, 0)) + offset,
        ]

        arc_length = [0, width, 0, width]

        self.line_batch = batch_for_shader(self.line_shader, "LINES", {"pos": lines, "arcLength": arc_length})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (self.context,), "WINDOW", "POST_VIEW"
            )

    def remove(self):
        """
        Disables the shelf gizmo by removing the draw handler
        """
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            self.draw_handler = None


class BookGenShelfFaceGizmo:
    """
    A gizmo that highlights a faces
    """

    log = logging.getLogger("bookGen.gizmo")

    def __init__(self, context):
        self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")
        self.batch = None
        self.context = context

        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (context,), "WINDOW", "POST_VIEW")

        color_ref = context.preferences.themes[0].user_interface.gizmo_primary
        self.color = [color_ref[0], color_ref[1], color_ref[2], 0.6]

    def draw(self, _context):
        """Draws face gizmo based on the current configuration

        Args:
            context (bpy.types.Context): the execution context
        """
        if self.batch is None:
            return

        self.shader.bind()
        gpu.state.blend_set("ALPHA")
        self.shader.uniform_float("color", self.color)
        self.batch.draw(self.shader)
        gpu.state.blend_set("NONE")

    def update(self, verts, _normal):
        """Updates the face gizmo based on the current configuration

        Args:
            context (bpy.types.Context): the execution context
        """
        self.batch = batch_for_shader(self.shader, "TRIS", {"pos": verts})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (self.context,), "WINDOW", "POST_VIEW"
            )

    def remove(self):
        """
        Disables the shelf gizmo by removing the draw handler
        """
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            self.draw_handler = None
