"""
Contains a class for visualizing the axis constraint
"""

import logging

import bpy
import gpu
from gpu_extras.batch import batch_for_shader


class BookGenLimitLine:
    """
    Draws a visualization of the axis constraint
    """

    log = logging.getLogger("bookGen.limit_line")

    def __init__(self, direction, context):

        if bpy.app.version < (3, 6, 0):
            self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        else:
            self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

        if direction == "X":
            self.line_color = (1.0, 0.0, 0.0, 0.1)
        elif direction == "Y":
            self.line_color = (0.0, 1.0, 0.0, 0.1)
        elif direction == "Z":
            self.line_color = (0.0, 0.0, 1.0, 0.1)
        self.batch = None

        self.draw_handler = None
        self.context = context

        self.limit = context.space_data.clip_end

    def draw(self, _context):
        """Draws a visualization of the axis constraint

        Args:
            _context (bpy.types.Context): the execution context
        """
        if self.batch is None:
            return

        self.shader.bind()
        gpu.state.line_width_set(2)
        self.shader.uniform_float("color", self.line_color)
        self.batch.draw(self.shader)
        gpu.state.line_width_set(1)

    def update(self, start, direction):
        """Updates the axis constraint visualization based on the current configuration

        Args:
            start (mathutils.Vector): the starting position of the axis constraint line
            direction (mathutils.Vector): the direction of the axis constraint line
        """
        if direction == "None":
            self.batch = None
            return

        if direction == "X":
            self.line_color = (1.0, 0.0, 0.0, 0.1)
            verts = [(-self.limit, start[1], start[2]), (self.limit, start[1], start[2])]
        elif direction == "Y":
            self.line_color = (0.0, 1.0, 0.0, 0.1)
            verts = [(start[0], -self.limit, start[2]), (start[0], self.limit, start[2])]
        elif direction == "Z":
            self.line_color = (0.0, 0.0, 1.0, 0.1)
            verts = [(start[0], start[1], -self.limit), (start[0], start[1], self.limit)]

        self.batch = batch_for_shader(self.shader, "LINES", {"pos": verts})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(
                self.draw, (self.context,), "WINDOW", "POST_VIEW"
            )

    def remove(self):
        """
        Disables the axis constraint visualization by removing the draw handler
        """
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            self.draw_handler = None
