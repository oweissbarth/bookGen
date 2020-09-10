import gpu

import bpy
import gpu
import bgl
from gpu_extras.batch import batch_for_shader

import mathutils
from mathutils import Vector, Matrix

from .utils import vector_scale
import logging

from .utils import bookGen_directory


class BookGenLimitLine():

    log = logging.getLogger("bookGen.limit_line")

    def __init__(self, start, direction, args):
        self.shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')

        if direction == 'X':
            self.line_color = (1.0, 0.0, 0.0, 0.1)
        elif direction == 'Y':
            self.line_color = (0.0, 1.0, 0.0, 0.1)
        elif direction == 'Z':
            self.line_color = (0.0, 0.0, 1.0, 0.1)
        self.batch = None

        self.draw_handler = None
        self.args = args

        self.limit = args[1].space_data.clip_end

    def draw(self, op, context):
        if self.batch is None:
            return

        self.shader.bind()
        self.shader.uniform_float("color", self.line_color)
        self.batch.draw(self.shader)

    def update(self, start, direction):

        if direction == 'None':
            self.batch = None
            return

        if direction == 'X':
            self.line_color = (1.0, 0.0, 0.0, 0.1)
            verts = [(-self.limit, start[1], start[2]), (self.limit, start[1], start[2])]
        elif direction == 'Y':
            self.line_color = (0.0, 1.0, 0.0, 0.1)
            verts = [(start[0], -self.limit, start[2]), (start[0], self.limit, start[2])]
        elif direction == 'Z':
            self.line_color = (0.0, 0.0, 1.0, 0.1)
            verts = [(start[0], start[1], -self.limit), (start[0], start[1], self.limit)]

        self.batch = batch_for_shader(self.shader, 'LINES', {"pos": verts})

        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, self.args, 'WINDOW', 'POST_VIEW')

    def remove(self):
        self.log.debug("removing draw handler")
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
            self.draw_handler = None
