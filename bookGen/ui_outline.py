"""
Contains a class for drawing a transparent shelf overlay
"""

import bpy
import gpu
from gpu_extras.batch import batch_for_shader


class BookGenShelfOutline:
    """
    Draws a transparent shelf overlay
    """

    draw_handler = None
    batch = None

    def __init__(self, check_depth=False):
        self.batch = None
        self.shader = None
        self.check_depth = check_depth
        self.outline_color = None
        if bpy.app.version < (3, 6, 0):
            self.shader = gpu.shader.from_builtin("3D_UNIFORM_COLOR")
        else:
            self.shader = gpu.shader.from_builtin("UNIFORM_COLOR")

    def update(self, vertices, faces, context):
        """Updates the axis constraint visualization based on the current configuration

        Args:
            vertices (List[mathutils.Vector]): the vertices of the shelf overlay
            faces (List[mathutils.Vector]): the face indices of the shelf overlay
        """
        col_ref = context.preferences.themes[0].view_3d.face_select
        self.outline_color = (col_ref[0], col_ref[1], col_ref[2], 0.3)
        indices = []
        for face in faces:
            indices.append((face[0], face[1], face[2]))
            indices.append((face[0], face[2], face[3]))

        self.batch = batch_for_shader(self.shader, "TRIS", {"pos": vertices}, indices=indices)

    def enable_outline(self, vertices, faces, context):
        """Enables the shelf overlay

        Args:
            vertices (List[mathutils.Vector]): the vertices of the shelf overlay
            faces (List[mathutils.Vector]): the face indices of the shelf overlay
            context (bpy.types.Context): the execution context
        """
        if self.draw_handler is None:
            self.draw_handler = bpy.types.SpaceView3D.draw_handler_add(self.draw, (context,), "WINDOW", "POST_VIEW")
        self.update(vertices, faces, context)

    def disable_outline(self):
        """
        Disables the shelf overlay
        """
        if self.draw_handler is not None:
            bpy.types.SpaceView3D.draw_handler_remove(self.draw_handler, "WINDOW")
            self.draw_handler = None

    def draw(self, _context):
        """Draws the shelf overlay

        Args:
            context (bpy.types.Context): the execution context
        """
        if self.batch is None:
            return
        self.shader.bind()
        gpu.state.blend_set("ALPHA")
        if self.check_depth:
            gpu.state.depth_test_set("LESS_EQUAL")

        self.shader.uniform_float("color", self.outline_color)
        self.batch.draw(self.shader)
        gpu.state.blend_set("NONE")
        gpu.state.depth_test_set("NONE")
