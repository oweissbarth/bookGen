import gpu

import bpy
import gpu
from gpu_extras.batch import batch_for_shader

from .data.gizmo_verts import bookstand_verts
import logging

class BookGenShelfGizmo():

    log = logging.getLogger("bookGen.gizmo")


    def __init__(self, start, end, nrm):
        self.bookstand_shader = gpu.shader.from_builtin('3D_UNIFORM_COLOR')
        self.bookstand_batch = batch_for_shader(self.bookstand_shader, 'TRIS', {"pos": bookstand_verts})
        self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self._draw, (), 'WINDOW', 'POST_VIEW')


    def _draw(self):
        self.bookstand_shader.bind()
        self.bookstand_shader.uniform_float("color", (1, 1, 0, 1))
        self.bookstand_batch.draw(self.bookstand_shader)

    def update(self, start, end, nrm):
        dir = end - start
        gpu.matrix.scale((dir.length, 1, 1))
        gpu.matrix.push()

    def remove(self):
        self.log.debug("removing draw handler")
        bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, 'WINDOW')
